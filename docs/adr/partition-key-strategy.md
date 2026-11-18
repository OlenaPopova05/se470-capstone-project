# Choice of Partition Key Strategy

## Context

Milestone 2 requires implementing consistent hashing to distribute records across multiple shards.

We need to choose a partition key strategy to determine which information will be hashed to select the appropriate shard.

Our system is a generic key-value store that supports multiple tables and key-based CREATE, READ, EXISTS, and DELETE operations without a predefined record schema.

Three approaches were considered: **full record key**, **key prefix**, and **separate partition key**.

## Alternatives Considered

### 1. Full Record Key

**Advantages:**
- Simple to implement without additional key processing.
- Does not require a predefined record schema or key format.
- Allows different record keys to be distributed independently across shards.
- Well suited for key-based CRUD operations.

**Disadvantages:**
- Identical record keys from different tables produce the same hash and are routed to the same shard.
- Related records are not guaranteed to be stored on the same shard.
- Does not prevent hot keys caused by frequently accessed records.

### 2. Key Prefix

**Advantages:**
- Allows related records with the same prefix to be stored on the same shard.
- Can be useful when records are frequently accessed as a group.

**Disadvantages:**
- Requires a predefined key format.
- Popular prefixes may create uneven data distribution and hot partitions.
- Less flexible for a generic key-value store.

### 3. Separate Partition Key

**Advantages:**
- Allows clients to explicitly define how records should be grouped.
- Provides flexibility for more complex data models.

**Disadvantages:**
- Requires an additional field in API requests.
- Makes the API and key management more complex.
- Adds unnecessary complexity for our current CRUD operations.

## Decision

I decided to use **the table name combined with the full record key** as the input for consistent hashing.

Since our key-value store supports multiple tables, identical record keys may exist in different tables. Including the table name allows these records to be hashed independently.

This approach does not require a predefined record schema or additional partition key fields. It also supports key-based CRUD operations without introducing constraints on the structure of stored values.

Hashing the full logical record identifier provides a simple and flexible partitioning strategy compatible with our consistent hashing mechanism.

## Consequences

- The Coordinator will UTF-8 encode the table name and full record key, prefix each byte string with its length as a four-byte unsigned big-endian integer, concatenate them in that order, and calculate the SHA-256 hash of the result. Lengths count bytes, not characters.
- The resulting hash will determine the record's position on the consistent hash ring and its destination shard.
- Identical record keys from different tables can be routed to different shards.
- No separate partition key field or semantic key prefix is required; the Milestone 2 HTTP API restricts the characters allowed in table names and keys.
- Related records may be stored on different shards.
- Frequently accessed keys may still create uneven workloads.
- Queries based on non-key attributes would require additional mechanisms, such as secondary indexes.
- Changing the partitioning strategy after storing data would require redistributing existing records.
