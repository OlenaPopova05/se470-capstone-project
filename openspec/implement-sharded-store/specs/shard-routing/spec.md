## ADDED Requirements

### Requirement: Deterministic record hash

The Coordinator SHALL hash the pair `(table_name, record_key)` by UTF-8 encoding each string, prefixing each byte string with its byte length as a four-byte unsigned big-endian integer, concatenating the two fields in that order, and applying SHA-256. The stored JSON value SHALL not affect routing.

#### Scenario: Distinguish formerly ambiguous pairs
- **WHEN** the pairs `("ab", "c")` and `("a", "bc")` are hashed
- **THEN** their encoded byte sequences differ.

#### Scenario: Stable routing
- **WHEN** the same table and key are routed with the same shard membership
- **THEN** the Coordinator selects the same physical shard for CREATE, READ, EXISTS, and DELETE.

### Requirement: Consistent hashing ring

Each registered physical shard SHALL have 100 deterministic virtual-node positions on the SHA-256 ring. The Coordinator SHALL select the first virtual node clockwise at or after the record hash, wrapping to the first position when necessary.

#### Scenario: Two physical shards
- **WHEN** two shards are registered
- **THEN** the ring contains 200 virtual nodes, and record keys can be assigned to either physical shard.

#### Scenario: Wrap around
- **WHEN** a record hash is greater than every virtual-node position
- **THEN** the first position in the sorted ring owns the record.

### Requirement: Empty-ring membership changes

In sharded mode, the Coordinator SHALL allow registering new physical shards until the first successful record CREATE or an attempted CREATE whose outcome is uncertain. It SHALL require at least two registered shards before accepting record operations. After membership is locked, it SHALL reject new shard IDs and changes to registered shard addresses with `409`, even if all records are later deleted. Re-registering an existing ID with the same address SHALL return `200` without adding virtual nodes. Before membership is locked, changing an existing shard's address SHALL return `201`; registering a second ID with an address already in use SHALL return `409`.

#### Scenario: Add a shard before writes
- **WHEN** two shards are registered, no record has ever been created, and a third shard registers
- **THEN** the ring is recomputed with 300 virtual nodes and record ownership can change for keys that have not been stored.

#### Scenario: Not enough shards
- **WHEN** sharded mode has fewer than two registered shards
- **THEN** record operations return `503`; table registration remains available.

#### Scenario: Reject membership change after a write
- **WHEN** a record was successfully created and a new shard or changed address is registered
- **THEN** registration returns `409` and the existing ring remains unchanged.

#### Scenario: Uncertain write result
- **WHEN** a CREATE may have reached a shard but the Coordinator cannot confirm its result
- **THEN** the Coordinator returns `503` and locks membership to preserve the possible record's owner.

#### Scenario: Idempotent re-registration
- **WHEN** the same shard ID and address are registered again
- **THEN** registration returns `200` and no duplicate virtual nodes appear, including after membership is locked.

### Requirement: Sharded forwarding and failure

In sharded mode, the Coordinator SHALL forward all record operations to the selected shard and SHALL NOT use local record storage as a fallback. A shard failure SHALL not trigger automatic remapping to another shard.

#### Scenario: Responsible shard is unavailable
- **WHEN** the selected shard cannot complete a record request
- **THEN** the Coordinator returns `503` and does not claim that another shard owns the record.
