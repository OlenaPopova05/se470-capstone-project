"""Coordinator behavior shared by the HTTP handlers and future shard routing."""

import math
import re
from threading import RLock
from typing import Any
from urllib.parse import urlsplit

from kvstore.ring import ConsistentHashRing, VIRTUAL_NODES_PER_SHARD
from kvstore.shard_client import HTTPRecordStore, StoreUnavailable
from kvstore.storage import InMemoryRecordStore, RecordAlreadyExists, RecordNotFound, RecordStore


TABLE_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_-]*\Z")
RECORD_KEY = re.compile(r"[A-Za-z0-9_-]+\Z")


def is_json_value(value: Any) -> bool:
    """Exclude non-JSON values such as NaN that a permissive parser may accept."""

    if value is None or isinstance(value, (str, bool, int)):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, list):
        return all(is_json_value(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and is_json_value(item) for key, item in value.items())
    return False


class APIError(Exception):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message

    def response(self) -> dict[str, str]:
        return {"error": self.code, "message": self.message}


class Coordinator:
    def __init__(self, mode: str = "single-node", store: RecordStore | None = None) -> None:
        if mode not in {"single-node", "sharded"}:
            raise ValueError("STORAGE_MODE must be single-node or sharded")
        if mode == "sharded" and store is not None:
            raise ValueError("sharded mode cannot use a local record store")

        self.mode = mode
        self.tables: dict[str, dict[str, str]] = {}
        self._table_lock = RLock()
        self.store = (store if store is not None else InMemoryRecordStore()) if mode == "single-node" else None
        self.shards: dict[str, str] = {}
        self._ring = ConsistentHashRing(())
        self._ring_lock = RLock()
        self._membership_locked = False

    @staticmethod
    def _check_table_name(table_name: Any) -> str:
        if not isinstance(table_name, str) or TABLE_NAME.fullmatch(table_name) is None:
            raise APIError(400, "bad_request", "Invalid table name")
        return table_name

    @staticmethod
    def _check_key(key: Any) -> str:
        if not isinstance(key, str) or RECORD_KEY.fullmatch(key) is None:
            raise APIError(400, "bad_request", "Invalid record key")
        return key

    def register_table(self, definition: Any) -> dict[str, str]:
        if not isinstance(definition, dict) or set(definition) != {"table_name", "partition_key"}:
            raise APIError(400, "bad_request", "Expected table_name and partition_key")

        table_name = self._check_table_name(definition["table_name"])
        partition_key = definition["partition_key"]
        if not isinstance(partition_key, str) or not partition_key:
            raise APIError(400, "bad_request", "Invalid partition_key")

        with self._table_lock:
            if table_name in self.tables:
                raise APIError(409, "conflict", "Table already exists")
            self.tables[table_name] = {"partition_key": partition_key}
        return {"table_name": table_name, "partition_key": partition_key}

    def register_shard(self, definition: Any) -> dict[str, str | int]:
        if self.mode != "sharded":
            raise APIError(409, "conflict", "Shard registration requires sharded mode")
        if not isinstance(definition, dict) or set(definition) != {"shard_id", "address"}:
            raise APIError(400, "bad_request", "Expected shard_id and address")
        shard_id = definition["shard_id"]
        address = definition["address"]
        if not isinstance(shard_id, str) or not shard_id:
            raise APIError(400, "bad_request", "Invalid shard ID")
        if not isinstance(address, str):
            raise APIError(400, "bad_request", "Invalid shard address")
        try:
            parsed = urlsplit(address)
            parsed.port
        except ValueError:
            raise APIError(400, "bad_request", "Invalid shard address") from None
        if (parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password
                or parsed.path not in {"", "/"} or parsed.query or parsed.fragment):
            raise APIError(400, "bad_request", "Invalid shard address")
        address = f"{parsed.scheme.lower()}://{parsed.netloc.lower()}"

        with self._ring_lock:
            old_address = self.shards.get(shard_id)
            if old_address == address:
                return {"shard_id": shard_id, "status": "already_registered", "virtual_nodes": VIRTUAL_NODES_PER_SHARD}
            if self._membership_locked:
                raise APIError(409, "conflict", "Ring membership is locked")
            if address in self.shards.values():
                raise APIError(409, "conflict", "Shard address is already registered")
            self.shards[shard_id] = address
            self._ring = ConsistentHashRing(self.shards)
            return {"shard_id": shard_id, "status": "registered", "virtual_nodes": VIRTUAL_NODES_PER_SHARD}

    def _record_store(self, table_name: Any, key: Any) -> tuple[str, str, RecordStore]:
        table_name = self._check_table_name(table_name)
        key = self._check_key(key)
        with self._table_lock:
            if table_name not in self.tables:
                raise APIError(404, "table_not_found", "Table does not exist")
        if self.store is not None:
            return table_name, key, self.store
        with self._ring_lock:
            if len(self.shards) < 2:
                raise APIError(503, "service_unavailable", "At least two shards are required")
            shard_id = self._ring.owner(table_name, key)
            return table_name, key, HTTPRecordStore(self.shards[shard_id])

    def create_record(self, table_name: Any, key: Any, body: Any) -> dict[str, Any]:
        if self.mode == "sharded":
            with self._ring_lock:
                if not self._membership_locked:
                    # Keep registration from changing the ring during the first write.
                    return self._create_record(table_name, key, body)
        return self._create_record(table_name, key, body)

    def _create_record(self, table_name: Any, key: Any, body: Any) -> dict[str, Any]:
        table_name, key, store = self._record_store(table_name, key)
        if not isinstance(body, dict) or "value" not in body:
            raise APIError(400, "bad_request", "Expected a JSON object containing value")
        if not is_json_value(body["value"]):
            raise APIError(400, "bad_request", "Value must be valid JSON")
        try:
            value = store.create(table_name, key, body["value"])
        except RecordAlreadyExists:
            if self.mode == "sharded":
                self._membership_locked = True
            raise APIError(409, "conflict", "Record already exists") from None
        except StoreUnavailable as error:
            # A timed-out CREATE may have reached the shard, so do not remap its key.
            if self.mode == "sharded":
                self._membership_locked = True
            raise APIError(503, "service_unavailable", str(error)) from error
        if self.mode == "sharded":
            self._membership_locked = True
        return {"table_name": table_name, "key": key, "value": value}

    def read_record(self, table_name: Any, key: Any) -> dict[str, Any]:
        table_name, key, store = self._record_store(table_name, key)
        try:
            value = store.read(table_name, key)
        except RecordNotFound:
            raise APIError(404, "not_found", "Record does not exist") from None
        except StoreUnavailable as error:
            raise APIError(503, "service_unavailable", str(error)) from error
        return {"table_name": table_name, "key": key, "value": value}

    def record_exists(self, table_name: Any, key: Any) -> bool:
        table_name, key, store = self._record_store(table_name, key)
        try:
            return store.exists(table_name, key)
        except StoreUnavailable as error:
            raise APIError(503, "service_unavailable", str(error)) from error

    def delete_record(self, table_name: Any, key: Any) -> None:
        table_name, key, store = self._record_store(table_name, key)
        try:
            store.delete(table_name, key)
        except StoreUnavailable as error:
            raise APIError(503, "service_unavailable", str(error)) from error
