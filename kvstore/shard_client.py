"""HTTP adapter for the shard-local record store API."""

import json
from http.client import HTTPException
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from kvstore.storage import RecordAlreadyExists, RecordNotFound


class StoreUnavailable(Exception):
    """The selected shard did not return a usable response."""


class HTTPRecordStore:
    def __init__(self, address: str) -> None:
        self.address = address.rstrip("/")

    def _request(self, method: str, table_name: str, key: str, value: Any = None) -> tuple[int, bytes]:
        url = f"{self.address}/internal/records/{table_name}/{key}"
        body = json.dumps({"value": value}, allow_nan=False).encode("utf-8") if method == "PUT" else None
        headers = {"Content-Type": "application/json"} if body is not None else {}
        request = Request(url, data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=3) as response:
                return response.status, response.read()
        except HTTPError as error:
            return error.code, error.read()
        except (HTTPException, URLError, OSError, TimeoutError) as error:
            raise StoreUnavailable("Selected shard is unavailable") from error

    @staticmethod
    def _record_value(body: bytes, table_name: str, key: str) -> Any:
        try:
            record = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise StoreUnavailable("Invalid response from selected shard") from error
        if not isinstance(record, dict) or record.get("table_name") != table_name or record.get("key") != key or "value" not in record:
            raise StoreUnavailable("Invalid response from selected shard")
        return record["value"]

    def create(self, table_name: str, key: str, value: Any) -> Any:
        status, body = self._request("PUT", table_name, key, value)
        if status == 201:
            return self._record_value(body, table_name, key)
        if status == 409:
            raise RecordAlreadyExists
        raise StoreUnavailable(f"Selected shard returned {status}")

    def read(self, table_name: str, key: str) -> Any:
        status, body = self._request("GET", table_name, key)
        if status == 200:
            return self._record_value(body, table_name, key)
        if status == 404:
            raise RecordNotFound
        raise StoreUnavailable(f"Selected shard returned {status}")

    def exists(self, table_name: str, key: str) -> bool:
        status, _ = self._request("HEAD", table_name, key)
        if status in (200, 404):
            return status == 200
        raise StoreUnavailable(f"Selected shard returned {status}")

    def delete(self, table_name: str, key: str) -> None:
        status, _ = self._request("DELETE", table_name, key)
        if status != 204:
            raise StoreUnavailable(f"Selected shard returned {status}")
