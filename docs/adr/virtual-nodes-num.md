# Choice of Number of Virtual Nodes

## Context

Milestone 2 requires implementing consistent hashing to distribute keys across multiple physical shards.

We need to determine how many virtual nodes should represent each physical shard on the consistent hash ring to achieve reasonably balanced key distribution while keeping routing overhead low.

The system initially consists of two physical shards with equal capacity.

## Alternatives Considered

### 1. One Virtual Node per Shard

**Advantages:**
- Simple to implement and maintain.
- Minimal memory and ring management overhead.

**Disadvantages:**
- May result in uneven key distribution between shards.
- Provides limited flexibility for balancing the hash ring.

### 2. 100 Virtual Nodes per Shard

**Advantages:**
- Provides multiple positions per shard, improving the expected balance of key distribution.
- Introduces relatively low memory and routing overhead.
- Suitable as a starting configuration for a small distributed system.

**Disadvantages:**
- Requires maintaining more positions on the hash ring.
- Does not guarantee perfectly balanced key distribution.

### 3. 500 Virtual Nodes per Shard

**Advantages:**
- Provides more positions on the hash ring, potentially improving key distribution.
- May provide more consistent balancing as the system scales.

**Disadvantages:**
- Requires additional memory and ring management overhead.
- The improvement over 100 virtual nodes may be limited for our current project.

## Decision

I decided to use **100 virtual nodes per physical shard**.

Based on the reviewed article on consistent hashing, 100–500 virtual nodes per physical server is a suggested practical range. I selected 100 as the lower end of this range because our project initially consists of only two physical shards with equal capacity.

Using 100 virtual nodes provides multiple positions for each shard on the hash ring while keeping routing overhead low. A larger number of virtual nodes would introduce additional overhead without a demonstrated need at our current scale.

As the system grows, additional physical shards can be introduced while maintaining the same number of virtual nodes per shard.

## Consequences

- Each physical shard will be represented by 100 virtual nodes on the consistent hash ring.
- With two initial shards, the Coordinator will manage 200 virtual node positions.
- Equal-capacity shards will have the same number of virtual nodes to support approximately balanced key distribution.
- Virtual nodes will not require additional EC2 instances or separate allocation of computing resources.
- Additional physical shards can be introduced without changing the number of virtual nodes assigned to existing shards.
- Adding shards or changing the number of virtual nodes after data has been stored will require data rebalancing.

## References

- [System Design — Chapter 3: Consistent Hashing Explained](https://medium.com/@RobuRishabh/system-design-chapter-3-consistent-hashing-explained-aeef2f3ebf63)
