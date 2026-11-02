# Proposal: Set Up AWS Infrastructure

## Why

The capstone needs a reproducible AWS foundation with controlled access and isolated network areas. Infrastructure as Code (IaC) will let us deploy, verify, remove, and recreate resources consistently.

## What Changes

- Define a read-only IAM policy and an assumable IAM role in CloudFormation, without deploying them in the restricted AWS Academy sandbox.
- Create a dedicated VPC with one public subnet and two private subnets, an Internet Gateway, and appropriate route tables.
- Deploy the network through a separate CloudFormation stack, leaving application resources in a different stack in the future.
- Review relevant AWS service quotas and estimate one month of infrastructure cost for a coordinator and **two shards**; compare the estimate with the sandbox credit limit.
- Verify that the network stack can be deleted and recreated from IaC alone, and document results and limitations.

## Capabilities

### New Capabilities

- `iam-access`: Document restricted, read-only IAM access and an assumable role using IaC.
- `network`: Provision and validate the AWS network foundation.

## Impact

- CloudFormation IAM and network templates will be added to the repository.
- The network stack will be deployed in AWS Academy; IAM resources will only be specified and validated without deployment.
- The README will document deployment, verification, quotas, estimated costs, and reproducibility.
- Architecture decisions are recorded in ADR-001 (IaC tool), ADR-002 (stack layout), and ADR-003 (CIDR addressing).
