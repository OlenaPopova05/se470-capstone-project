"""Request and response models shared by Coordinator and shard APIs."""

from typing import Any, Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


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


class ShardRegistration(BaseModel):
    shard_id: str = Field(min_length=1)
    address: AnyHttpUrl


class ShardRegistrationResponse(BaseModel):
    shard_id: str
    status: Literal["registered", "already_registered"]
    virtual_nodes: int
