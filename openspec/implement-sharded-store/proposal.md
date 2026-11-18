# Proposal: Implement the Milestone 2 Sharded Store

## Why

Milestone 2 must demonstrate table registration, key-based CRUD, Coordinator routing, consistent hashing across physical shards, reproducible application infrastructure, CI/CD, and a YCSB baseline. The API and required ADRs exist, but the application and deployment pipeline do not yet exist. This change records the intended behavior before implementation.

## What Changes

- Implement the OpenAPI contract for table registration and CREATE, READ, EXISTS, and DELETE.
- Support a single-node Coordinator with in-memory storage, then a sharded deployment with at least two physical shards.
- Route records by SHA-256 of the length-prefixed UTF-8 encoding of `(table_name, record_key)` and a ring with 100 virtual nodes per shard.
- Allow registration and ring changes while the sharded deployment has never accepted a record; lock membership after the first successful CREATE. Demonstrate adding a shard to an empty ring. Data migration is outside this change.
- Add an application CloudFormation stack separate from the Milestone 1 network stack, and a CI/CD pipeline that deploys infrastructure and application changes within AWS Academy constraints.
- Benchmark the two-shard store with YCSB and retain a reproducible baseline for later milestones.

## Capabilities

### New Capabilities

- `table-records`: Register logical tables and perform key-based CRUD in single-node and sharded modes.
- `shard-routing`: Deterministically route writes and reads, register shards, and safely limit ring changes before data migration exists.
- `application-delivery`: Deploy and verify the application through IaC and CI/CD.
- `benchmark-baseline`: Capture reproducible YCSB results for the two-shard deployment.

## Impact

- New Coordinator, shard, storage, routing, and integration-test code will be added.
- `openapi.yaml` is the HTTP contract; the existing Milestone 2 ADRs and this change record the decisions before code.
- The existing CloudFormation network stack is reused. Application resources live in a separate stack.
- The README will explain local and AWS startup, verification, limitations, and changes since Milestone 1.
- A Milestone 2 AI architecture critique and defense demo will be recorded.

## Scope Boundary and Grading Risk

This change supports dynamic *ring configuration while no record has ever been created* in the sharded deployment. It does not provide online data migration or rebalance after writes; that work is planned for Milestone 5. The Milestone 2 wording mentions dynamic updates, so this limited interpretation should be confirmed with the tutor and demonstrated explicitly rather than described as online resharding.
