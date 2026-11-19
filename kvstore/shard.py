"""Shard-local FastAPI service with an in-memory record store."""

import asyncio
import json
import os
from contextlib import asynccontextmanager
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request as URLRequest, urlopen

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from kvstore.coordinator import APIError, Coordinator, is_json_value
from kvstore.models import CreateRecordRequest, Record
from kvstore.storage import InMemoryRecordStore, RecordAlreadyExists, RecordNotFound


def register_with_coordinator(coordinator_url: str, shard_id: str, address: str) -> None:
    body = json.dumps({"shard_id": shard_id, "address": address}).encode("utf-8")
    request = URLRequest(
        f"{coordinator_url.rstrip('/')}/internal/shards/register",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=3) as response:
            if response.status not in (200, 201):
                raise RuntimeError(f"Shard registration returned {response.status}")
    except HTTPError as error:
        raise RuntimeError(f"Coordinator rejected shard registration with {error.code}") from error
    except (URLError, OSError, TimeoutError) as error:
        raise RuntimeError("Could not register shard with Coordinator") from error


def create_shard_app(
    shard_id: str,
    address: str,
    coordinator_url: str,
) -> FastAPI:
    """Create a shard service that registers with the Coordinator."""

    if any(not value.strip() for value in (shard_id, address, coordinator_url)):
        raise ValueError("shard_id, address, and coordinator_url must not be empty")
    record_store = InMemoryRecordStore()

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        await asyncio.to_thread(register_with_coordinator, coordinator_url, shard_id, address)
        yield

    app = FastAPI(title="Shard Record API", version="1.0.0", lifespan=lifespan)

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, error: APIError) -> Response:
        if request.method == "HEAD":
            return Response(status_code=error.status)
        return JSONResponse(status_code=error.status, content=error.response())

    def check_identifiers(table_name: str, key: str) -> None:
        Coordinator._check_table_name(table_name)
        Coordinator._check_key(key)

    @app.put("/internal/records/{table_name}/{key}", status_code=201, response_model=Record)
    def create_record(table_name: str, key: str, body: CreateRecordRequest) -> dict[str, Any]:
        check_identifiers(table_name, key)
        if not is_json_value(body.value):
            raise APIError(400, "bad_request", "Value must be valid JSON")
        try:
            value = record_store.create(table_name, key, body.value)
        except RecordAlreadyExists:
            raise APIError(409, "conflict", "Record already exists") from None
        return {"table_name": table_name, "key": key, "value": value}

    @app.get("/internal/records/{table_name}/{key}", response_model=Record)
    def read_record(table_name: str, key: str) -> dict[str, Any]:
        check_identifiers(table_name, key)
        try:
            value = record_store.read(table_name, key)
        except RecordNotFound:
            raise APIError(404, "not_found", "Record does not exist") from None
        return {"table_name": table_name, "key": key, "value": value}

    @app.head("/internal/records/{table_name}/{key}")
    def record_exists(table_name: str, key: str) -> Response:
        check_identifiers(table_name, key)
        return Response(status_code=200 if record_store.exists(table_name, key) else 404)

    @app.delete("/internal/records/{table_name}/{key}", status_code=204)
    def delete_record(table_name: str, key: str) -> Response:
        check_identifiers(table_name, key)
        record_store.delete(table_name, key)
        return Response(status_code=204)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "healthy"}

    return app


def main() -> None:
    shard_id = os.getenv("SHARD_ID")
    if not shard_id:
        raise SystemExit("SHARD_ID is required")
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8081"))
    address = os.getenv("SHARD_ADDRESS", f"http://127.0.0.1:{port}")
    coordinator_url = os.getenv("COORDINATOR_URL", "http://127.0.0.1:8080")
    uvicorn.run(
        create_shard_app(shard_id=shard_id, address=address, coordinator_url=coordinator_url),
        host=host,
        port=port,
    )


if __name__ == "__main__":
    main()
