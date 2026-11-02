# CIDR Addressing Scheme

## Context

Milestone 1 requires creating a VPC with public and private subnets. We need to choose an addressing scheme that provides enough IP addresses for our resources and allows future expansion.

## Decision

I decided to use **`10.0.0.0/16` for the VPC** and divide it into three non-overlapping subnets:

| Subnet | CIDR Block | Purpose |
|---|---|---|
| Public Subnet | `10.0.1.0/24` | Resources requiring internet access |
| Private Subnet 1 | `10.0.2.0/24` | Internal application resources |
| Private Subnet 2 | `10.0.3.0/24` | Internal application resources |

## Rationale

- Each `/24` subnet provides 251 usable IP addresses, which is more than enough for the current infrastructure.
- The `/16` VPC leaves enough address space for additional subnets in the future.
- Separate CIDR blocks prevent IP address conflicts between subnets.
- The addressing scheme is simple to understand and manage.
- Smaller subnets were also possible, but `/24` provides more flexibility for future expansion.

## Consequences

- Resources will have separate, non-overlapping IP address ranges.
- Additional subnets and resources can be added without changing the existing addressing scheme.
- More private IP address space is reserved than currently required.
- The VPC CIDR must be considered when connecting to other networks to avoid overlapping address ranges.