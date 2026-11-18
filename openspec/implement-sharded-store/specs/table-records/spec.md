## ADDED Requirements

### Requirement: Table registration

The Coordinator SHALL register a unique logical table with a `table_name` and `partition_key` attribute name through the external API. The `partition_key` SHALL be metadata; its value SHALL be supplied by the record URL's `{key}` parameter and SHALL NOT be required inside the stored JSON value.

The `table_name` SHALL match `^[A-Za-z][A-Za-z0-9_-]*$`; the record `key` SHALL match `^[A-Za-z0-9_-]+$`. Invalid request data rejected by Pydantic SHALL return `422`; an invalid path parameter rejected by the Coordinator SHALL return `400`. A malformed URL that matches no endpoint MAY return `404` before validation.

#### Scenario: Register a new table
- **WHEN** a client submits a valid new table definition
- **THEN** the Coordinator records it and returns `201`.

#### Scenario: Reuse a table name
- **WHEN** a client submits a table name that is already registered
- **THEN** the Coordinator returns `409` without replacing the existing definition.

#### Scenario: Invalid table definition
- **WHEN** Pydantic rejects an invalid table name in `POST /tables`
- **THEN** the API returns `422` without changing stored state.

#### Scenario: Invalid record path parameter
- **WHEN** the Coordinator receives an invalid table name or record key from a record URL
- **THEN** the API returns `400` without changing stored state.

### Requirement: Key-based CRUD

The Coordinator SHALL expose CREATE, READ, EXISTS, and DELETE for records identified by `(table_name, key)` according to `openapi.yaml`. CREATE SHALL not overwrite an existing record. DELETE SHALL be idempotent for an existing table. An unknown table SHALL not be treated as an empty table.

#### Scenario: Create and read a record
- **WHEN** a table is registered and a client creates a new record under a key
- **THEN** CREATE returns `201`, READ returns the same JSON value, and EXISTS returns `200` without a body.

#### Scenario: Duplicate record
- **WHEN** a client creates a record with an existing `(table_name, key)`
- **THEN** CREATE returns `409` and the original value remains unchanged.

#### Scenario: Missing record and deletion
- **WHEN** a record is absent from a registered table
- **THEN** READ and EXISTS return `404`, while DELETE returns `204` without a body.

#### Scenario: Unknown table
- **WHEN** a client addresses a table that was never registered
- **THEN** the Coordinator returns `404` for record operations, except EXISTS which returns `404` without a body.

#### Scenario: Same key in different tables
- **WHEN** two registered tables contain the same key string
- **THEN** their values remain independent.

#### Scenario: Store JSON null
- **WHEN** a client creates a record with `value: null`
- **THEN** READ returns that record with `value: null` and EXISTS returns `200`.

### Requirement: Single-node in-memory operation

The Coordinator SHALL support table registration and all four record operations without shards in single-node mode. Initial local record storage SHALL use an in-memory Python dictionary keyed by `(table_name, key)` behind a reusable storage interface, separate from the in-memory table registry. The mode SHALL be selected at startup by `STORAGE_MODE`, defaulting to `single-node`. The API SHALL document that in-memory data is not guaranteed to survive a process restart.

#### Scenario: Run without shards
- **WHEN** the Coordinator starts in single-node mode and no shard is registered
- **THEN** table registration and CRUD work against the local store.

#### Scenario: Restart the process
- **WHEN** the single-node process restarts
- **THEN** the service may start with empty table and record stores; no persistence guarantee is implied.

### Requirement: Shard-local record API

Each shard SHALL implement PUT, GET, HEAD, and DELETE at `/internal/records/{table_name}/{key}` using the request and response semantics in `openapi.yaml`. The Coordinator SHALL check table registration before forwarding. A shard SHALL NOT require a copy of the table registry to store a record by tuple.

#### Scenario: Coordinator forwards a record operation
- **WHEN** the Coordinator selects an available shard for a registered table and key
- **THEN** it calls the corresponding internal CRUD method and returns the documented external result.
