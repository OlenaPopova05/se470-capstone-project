## ADDED Requirements

### Requirement: YCSB baseline

The project SHALL run YCSB against the two-shard key-value store through a documented binding or adapter and retain workload configuration and measured results. The results SHALL identify run environment, shard count, operation count, concurrency, throughput, and latency so they can be compared with Milestones 3 and 5.

#### Scenario: Reproduce the baseline
- **WHEN** a reviewer follows the documented benchmark setup and commands
- **THEN** they can run the same workload against a two-shard deployment and obtain the same categories of measurements.

#### Scenario: Inspect recorded results
- **WHEN** the Milestone 2 hand-in is reviewed
- **THEN** the benchmark parameters and output are available in the repository as a baseline, with limitations noted.
