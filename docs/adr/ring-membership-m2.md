# Ring Membership Changes in Milestone 2

## Context

Consistent hashing can recompute ownership when a shard joins, but changing the ring after records exist can send reads to a different shard. Milestone 2 must demonstrate the ring and shard registration without claiming that records have been migrated.

## Alternatives Considered

### A. Static ring

Register exactly two shards before writes and reject further membership changes. This is simple but demonstrates little dynamic behavior.

### B. Dynamic ring while empty

Allow shard registration and ring recomputation before any successful record CREATE, then lock membership. This demonstrates that the routing map can change without making stored records unreachable.

### C. Online shard addition with migration

Allow membership changes after writes and move affected records. This provides complete dynamic resharding but requires a migration protocol, consistency handling, and failure recovery beyond the planned Milestone 2 scope.

## Decision

Choose **B** for Milestone 2. The sharded deployment starts empty. At least two physical shards register before record operations. A third shard may join while no record has ever been successfully created. The first successful CREATE locks membership for that running deployment. An attempted CREATE whose result cannot be confirmed also locks membership: the shard might have stored the record before the connection failed. Deleting all records does not unlock it. Re-registering the same shard ID and address remains idempotent; a new ID or changed address returns `409` after lock.

The move from single-node development to the sharded deployment uses fresh empty stores. There is no migration of temporary single-node data. Online addition and data rebalancing are deferred to a later milestone.

## Consequences

- The demo can show changes in owner mapping when a shard is added to an empty ring.
- Existing records remain on the shard chosen by the ring that was active for their writes.
- A failed shard does not cause automatic remapping; affected requests fail until the shard is restored.
