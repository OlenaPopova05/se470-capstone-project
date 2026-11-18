"""FastAPI transport for the Coordinator's external REST API."""

import os
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from kvstore.coordinator import APIError, Coordinator


TABLE_NAME_PATTERN = r"^[A-Za-z][A-Za-z0-9_-]*$"


class TableDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    table_name: str = Field(pattern=TABLE_NAME_PATTERN)
    partition_key: str = Field(min_length=1)


class CreateRecordRequest(BaseModel):
    value: Any


class Record(BaseModel):
    table_name: str
    key: str
    value: Any


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
