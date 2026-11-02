# Design: AWS Infrastructure Setup

## Overview

Use **AWS CloudFormation** for the infrastructure (ADR-001). Keep the **network in its own stack**, separate from future application resources (ADR-002). Use the private IPv4 addressing plan from ADR-003.

## Network layout

| Resource | CIDR | Planned use |
|---|---|---|
| VPC | `10.0.0.0/16` | Private network address space |
| Public subnet | `10.0.1.0/24` | Resources that may need direct internet routing |
| Private subnet 1 | `10.0.2.0/24` | Internal resources |
| Private subnet 2 | `10.0.3.0/24` | Internal resources |

- Place the subnets within the VPC. Put the two private subnets in different Availability Zones if the sandbox region supports it.
- Attach an Internet Gateway to the VPC.
- Associate the public subnet with a route table containing a default route `0.0.0.0/0` to the Internet Gateway.
- Associate both private subnets with a private route table containing only the VPC's local route; do not add a default route to the Internet Gateway. No NAT Gateway is planned for Milestone 1.
- The CIDR blocks are non-overlapping; `/24` leaves 251 usable IPv4 addresses per subnet in AWS. A public subnet alone does not grant public access to an instance; public IPs and security rules are also required.

## IAM design

- Define a standalone CloudFormation template for a **read-only policy** with an explicit list of read actions required to inspect relevant AWS resources. Avoid write actions and broad `*` action permissions.
- Define a role that can be assumed by an explicitly specified trusted AWS principal using a trust policy (`sts:AssumeRole`). Attach the read-only policy to that role in the template. The trusted principal will be selected and documented before implementation; avoid making the role assumable by everyone.
- Do not deploy IAM resources in the sandbox: simulation showed `iam:CreatePolicy` and `iam:CreateRole` as `implicitDeny`. Validate the YAML/template statically instead. A policy containing only read allows does not prevent permissions from other policies attached to the same principal.

## Deployment and verification

- Store templates in Git, for example `infra/network.yaml` and `infra/iam-readonly.yaml`.
- Validate templates before deployment. Deploy only the network stack to the AWS Academy sandbox.
- Check VPC/subnet CIDRs, gateway attachment, route table associations, and that private route tables have no IGW default route.
- Record relevant M2 quotas and an estimated monthly budget for a coordinator and two shards. The specific compute and storage sizes will be selected in the budget assessment, not assumed here; compare the estimate with the actual sandbox credit ceiling.
- Measure stack deletion and recreation time; log issues encountered on the first attempt. Do not delete the default VPC.

## Risks and trade-offs

- AWS Academy may block specific CloudFormation operations even if a general permission simulation reports `allowed`.
- Cross-stack dependencies will require passing network IDs to a future application stack and observing deployment/deletion order.
- A VPC `/16` uses more private IPv4 space than currently needed and might overlap with a network connected later.
- Private subnets without NAT have no general outbound internet path; this is intentional for this milestone.

## Decisions

See `docs/adr/iac-tool.md`, `docs/adr/stack-layout.md`, and `docs/adr/cidr-addressing.md` in the repository.
