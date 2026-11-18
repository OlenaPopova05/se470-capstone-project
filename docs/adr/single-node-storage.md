# Single-Node Storage for Milestone 2

## Context

The Coordinator must support table registration and CRUD before the sharded deployment is built. A storage choice is needed that keeps request handling independent of the later shard layout. Milestone 2 does not require data to survive process restarts.

## Alternatives Considered

### In-memory Python dictionary

- Simple to implement and inspect during the single-node demonstration.
- No service or disk setup is needed.
- Process restarts lose data, and it is unsuitable for durable production storage.

### SQLite or another durable local store

- Survives process restarts and offers transactional operations.
- Introduces schema, file lifecycle, and migration concerns before the sharding behavior is demonstrated.

## Decision

Use two in-memory Python dictionaries in the initial single-node implementation: `tables[table_name]` stores definition metadata, and `records[(table_name, key)]` stores a JSON value. Test tuple membership before reading so a stored JSON `null` is distinct from an absent record. Put record operations behind a storage interface so the same behavior can be implemented by shard services and replaced by durable storage later. Select the Coordinator mode with `STORAGE_MODE` at startup, defaulting to `single-node`. Sharded deployment begins with empty stores; temporary single-node test records are not migrated.

## Consequences

- Single-node CREATE, READ, EXISTS, and DELETE can be implemented without cloud resources.
- A process restart may remove all table definitions and records.
- The local store must not be used as an automatic fallback when a shard is unavailable.
- Durable storage and restart recovery require a later design and implementation.
