# Implementation Tasks — Milestone 2

## 1. Contract and decisions, before code

- [x] Review this OpenSpec change, the OpenAPI contract, and the Milestone 2 ADRs before application implementation.
- [x] Commit the Milestone 2 specification and ADRs when Git write access is available; they were written before application code.
- [x] Fix URL path validation rules for table names and keys in OpenAPI and OpenSpec.
- [x] Select FastAPI and Uvicorn for the HTTP implementation.

## 2. Single-node behavior

- [x] Build the Coordinator API, in-memory table registry, and a reusable in-memory record-store interface.
- [x] Implement table registration and CREATE, READ, EXISTS, DELETE in single-node mode with contract-level status and error behavior.
- [x] Verify duplicate tables, duplicate records, missing tables/records, JSON `null`, and two tables using the same key.

## 3. Ring and sharded behavior

- [x] Implement and test the exact length-prefixed UTF-8 hash input, SHA-256 positions, 100 virtual nodes per shard, clockwise lookup, and wraparound.
- [x] Implement shard registration, idempotent re-registration, empty-ring additions, two-shard readiness, and membership lock after the first successful CREATE.
- [x] Implement the shard-local internal CRUD API and Coordinator forwarding for all four operations.
- [x] Verify writes and reads reach the selected shard, failed shards yield `503`, and no local fallback occurs in sharded mode.
- [x] Demonstrate routing changes when a third shard joins an empty ring and rejection of membership changes after a write.

## 4. Local and AWS delivery

- [x] Provide a reproducible local startup for one Coordinator and two shards with a smoke-test script or commands.
- [ ] Verify AWS Academy permissions, private-shard artifact delivery, and CI/CD credentials before choosing the deployment mechanism; record the decision.
- [x] Create and locally validate a separate CloudFormation application template that reuses Milestone 1 network outputs.
- [ ] Deploy the application stack in the sandbox; verify endpoint reachability, security boundaries, service health, and CRUD across two shards.
- [ ] Add CI/CD checks and pipeline stages that deploy both IaC and application updates; demonstrate one update of each.

## 5. Baseline and hand-in

- [ ] Build or configure a YCSB binding for the API and capture the workload, run environment, throughput, latency, and two-shard results.
- [ ] Update README with startup, verification, changes since Milestone 1, known limitations, and benchmark reproduction.
- [ ] Record an AI architecture critique and accept or reject 2–3 points with reasons.
- [ ] Rehearse the ADR, implementation, and benchmark walkthroughs for the oral defense.
