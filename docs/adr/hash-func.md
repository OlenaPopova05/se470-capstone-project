# Choice of Hash Function

## Context

Milestone 2 requires implementing consistent hashing to distribute keys across multiple shards.

We need to choose a hash function to calculate positions for keys and virtual nodes on the consistent hash ring.

Three approaches were considered: **SHA-256**, **MD5**, and **MurmurHash3**.

## Alternatives Considered

### 1. SHA-256

**Advantages:**
- Provides deterministic hashing and good hash distribution.
- Available in Python's standard library without additional dependencies.
- Suitable for generating stable positions on the consistent hash ring.

**Disadvantages:**
- Slower than non-cryptographic hash functions.
- Its cryptographic properties are not necessary for key distribution.

### 2. MD5

**Advantages:**
- Fast and deterministic.
- Available in Python's standard library.
- Produces smaller hash values than SHA-256.

**Disadvantages:**
- Has known cryptographic collision vulnerabilities.
- Does not provide a significant advantage for our current project.

### 3. MurmurHash3

**Advantages:**
- Designed for fast, non-cryptographic hashing.
- Provides good hash distribution.
- Suitable for systems requiring frequent hash calculations.

**Disadvantages:**
- Usually requires an additional Python library.
- Requires choosing and maintaining a specific implementation and seed.

## Decision

I decided to use **SHA-256** for consistent hashing.

SHA-256 provides deterministic and well-distributed hash values, which are suitable for assigning keys and virtual nodes to positions on the hash ring.

It is also available in Python's standard library, allowing us to implement consistent hashing without introducing additional dependencies.

Although SHA-256 is slower than non-cryptographic alternatives, its performance is sufficient for the initial scale of our project.

## Consequences

- SHA-256 will be used to calculate hash values for both keys and virtual nodes.
- The same input will produce the same hash value across Coordinator restarts.
- No additional hashing libraries are required.
- SHA-256 may introduce more computational overhead compared to faster non-cryptographic alternatives.
- Changing the hash function after data has been stored would require redistributing keys across shards.
