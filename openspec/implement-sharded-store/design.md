# Design: Milestone 2 Sharded Store

## Modes and Components

- A Coordinator exposes the external REST API from `openapi.yaml` and owns the table registry.
- `single-node` mode uses a local in-memory Python dictionary for records. It does not depend on shard registration.
- `sharded` mode uses the same external API, but forwards record operations to shard services through `/internal/records/{table_name}/{key}`. Each shard uses a separate in-memory store. The Coordinator does not silently fall back to local storage.
- Select the mode at process startup with `STORAGE_MODE=single-node` (the default) or `STORAGE_MODE=sharded`. Changing the variable requires a new, empty deployment; it never migrates data.
- Use FastAPI for the HTTP routes and request validation, and Uvicorn to serve the ASGI app. Keep HTTP handling separate from the Coordinator and storage classes. FastAPI's default handler returns `422` with a validation-error body for Pydantic failures; the Coordinator's `APIError` handler returns its own error body and status (`400`, `404`, `409`, or `503`).
- The table registry is in Coordinator memory. Neither tables nor records are guaranteed to survive process restarts in Milestone 2. Switching from single-node development to sharded deployment starts with empty stores; test data is not migrated. After a partial Coordinator restart, the deployment must not attach a fresh ring to shards that may still contain records; restart the full in-memory deployment empty or leave it unavailable.
- Storage operations are behind a small storage interface so request handling and routing do not depend on dictionary details. This permits durable storage later.

## Table and Record Semantics

- `POST /tables` registers a unique `table_name` and the logical `partition_key` attribute name. A duplicate table name returns `409`.
- A table name must match `^[A-Za-z][A-Za-z0-9_-]*$`; a record key must match `^[A-Za-z0-9_-]+$`. These are deliberate Milestone 2 URL-path restrictions. An invalid table definition rejected by Pydantic returns `422`; an invalid path parameter rejected by the Coordinator returns `400`. A URL whose path cannot match an endpoint may return `404` before validation.
- The actual key value is the decoded `{key}` path parameter. The stored JSON `value` may be any JSON value, including `null`; the Coordinator does not require an attribute named by `partition_key` inside it.
- Keep `tables: dict[str, dict]` and `records: dict[tuple[str, str], JSON value]` separate. Test membership with `key in records`; `dict.get()` cannot distinguish an absent record from a stored JSON `null`.
- Records are identified by `(table_name, key)`. `PUT` is create-only and returns `409` without overwriting an existing record. `GET` returns the stored record or `404`. `HEAD` returns `200` or `404` with no body. `DELETE` returns `204` for both an existing and an already absent record, but an unknown table returns `404`.
- The Coordinator checks table existence before forwarding to a shard. A shard stores the tuple and does not keep table definitions.
- The restricted key alphabet excludes `/`, spaces, and Unicode characters in Milestone 2; no special path escaping is needed for accepted keys. This restriction is independent of the logical `(table_name, key)` hash encoding.

## Hashing and Ring

- Encode each logical identifier as `uint32_be(len(utf8(table_name))) || utf8(table_name) || uint32_be(len(utf8(key))) || utf8(key)`. Lengths count bytes. SHA-256 of those bytes yields the record's ring position.
- Each physical shard contributes 100 virtual nodes. A virtual-node position is SHA-256 of the same two-field length-prefixed encoding applied to `(shard_id, decimal virtual-node index)`, where the index is `0..99` with no leading zeroes. This makes ring construction deterministic across Coordinator restarts.
- Sort virtual-node positions by their 256-bit hash. Route a record to the first position clockwise at or after its hash, wrapping to the first ring position when necessary. Define a deterministic tie-break by `(shard_id, index)` if hashes collide.
- All CRUD operations for the same tuple use the same routing decision. Table names are part of the hash input, so equal keys in different tables are independent.

## Membership: Option B

- In sharded mode, new shard IDs may be registered while no record has ever been successfully created. A third shard can therefore be added to an empty two-shard ring and the routing map can be recomputed.
- At least two shards must be registered before sharded record operations are accepted. Until then, the Coordinator returns `503` for record operations; table registration can proceed.
- The first successful record CREATE locks membership for that running deployment. Later registration of a new shard or changing an existing shard's address returns `409`, even if every record is deleted. Re-registering the same ID and address remains idempotent (`200`) and adds no virtual nodes.
- This lock is a Milestone 2 safety boundary. There is no data transfer, shard removal, or online resharding. A fresh empty deployment may construct a new ring. A shard failure does not cause automatic remapping; affected requests return `503`.
- The defense demo will show the owner mapping for a fixed set of sample keys before and after adding a shard to an empty ring, then show that membership changes are rejected after a successful write. This demonstrates ring behavior without implying that stored data was migrated.

## Delivery and Operations

- Keep the Milestone 1 network stack intact and define application resources in a separate CloudFormation stack using its exported network IDs.
- The initial target is one Coordinator and two shard services in the AWS Academy sandbox. The Coordinator is client reachable; shard record endpoints are restricted to internal traffic. The chosen compute sizes and runtime schedule must stay within the documented sandbox quotas and credit budget.
- Private subnets have no general internet route. Before implementing application deployment, verify an allowed artifact-delivery and credential path for private shards, then record the selected method in the design/ADR. CI/CD must deploy both CloudFormation and application updates; a pipeline that only runs tests does not satisfy this change.
- Provide a local multi-process or container-based startup path so the API and ring can be demonstrated without cloud access.
- Use YCSB through a documented binding or adapter for this REST API. Fix workload, operation count, concurrency, key distribution, environment, and run commands; retain throughput and latency results for the two-shard baseline and note whether the run is local or AWS-hosted.

## Risks and Trade-offs

- In-memory data and table definitions disappear on process restart. The ring lock also resets only with a fresh empty deployment; no surviving records may be attached to a newly built ring without migration.
- A single Coordinator is a point of failure. Replication and failover are outside Milestone 2.
- Option B does not support changing membership when data exists. The course's dynamic-update wording may require a stronger demonstration; confirm this interpretation with the tutor.
- AWS Academy permissions and the lack of private-subnet egress may constrain the CI/CD delivery method. Validate the approach before provisioning application resources.

## Decisions

See `docs/adr/api-design.md`, `docs/adr/hash-func.md`, `docs/adr/virtual-nodes-num.md`, `docs/adr/partition-key-strategy.md`, and the Milestone 2 storage and membership ADRs.
