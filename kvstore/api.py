"""FastAPI transport for the Coordinator's external REST API."""

import os
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from kvstore.coordinator import APIError, Coordinator
from kvstore.models import CreateRecordRequest, Record, ShardRegistration, ShardRegistrationResponse, TableDefinition


def create_app(coordinator: Coordinator | None = None) -> FastAPI:
    """Create an isolated app so tests never share in-memory records."""

    service = coordinator if coordinator is not None else Coordinator(os.getenv("STORAGE_MODE", "single-node"))
    app = FastAPI(title="Serverless Key-Value Store API", version="1.0.0")

    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, error: APIError) -> Response:
        if request.method == "HEAD":
            return Response(status_code=error.status)
        return JSONResponse(status_code=error.status, content=error.response())

    @app.post("/tables", status_code=201, response_model=TableDefinition)
    def register_table(definition: TableDefinition) -> dict[str, str]:
        return service.register_table(definition.model_dump())

    @app.post("/internal/shards/register", status_code=201, response_model=ShardRegistrationResponse)
    def register_shard(definition: ShardRegistration, response: Response) -> dict[str, str | int]:
        result = service.register_shard(definition.model_dump(mode="json"))
        if result["status"] == "already_registered":
            response.status_code = 200
        return result

    @app.put("/tables/{table_name}/records/{key}", status_code=201, response_model=Record)
    def create_record(table_name: str, key: str, body: CreateRecordRequest) -> dict[str, Any]:
        return service.create_record(table_name, key, body.model_dump())

    @app.get("/tables/{table_name}/records/{key}", response_model=Record)
    def read_record(table_name: str, key: str) -> dict[str, Any]:
        return service.read_record(table_name, key)

    @app.head("/tables/{table_name}/records/{key}")
    def record_exists(table_name: str, key: str) -> Response:
        return Response(status_code=200 if service.record_exists(table_name, key) else 404)

    @app.delete("/tables/{table_name}/records/{key}", status_code=204)
    def delete_record(table_name: str, key: str) -> Response:
        service.delete_record(table_name, key)
        return Response(status_code=204)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "healthy"}

    return app


app = create_app()
