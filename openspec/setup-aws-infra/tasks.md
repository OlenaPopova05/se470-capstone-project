# Implementation Tasks — Milestone 1

## 1. Preparation

- [x] Investigate the actual sandbox identity (`voclabs`) and document tested allows/denies and methods (Console, CLI, Policy Simulator), including simulator limitations.
- [x] Record ADR-001 (CloudFormation), ADR-002 (separate network/application stacks), and ADR-003 (VPC/subnet CIDRs).
- [ ] Review and commit this OpenSpec proposal before writing implementation templates.

## 2. IAM policy and role (IaC only)

- [ ] Select a justified set of AWS read-only actions.
- [ ] Write CloudFormation code defining the read-only IAM policy.
- [ ] Define an IAM role and specific trusted principal in the same or a related template; attach the policy.
- [ ] Validate/review the IAM template without deploying IAM resources.
- [ ] Document `iam:CreatePolicy` and `iam:CreateRole` as `implicitDeny` in the simulator and explain the sandbox limitation.

## 3. Network stack

- [ ] Write a standalone CloudFormation network template with VPC `10.0.0.0/16` and three non-overlapping `/24` subnets.
- [ ] Add and attach an Internet Gateway; configure explicit public and private route table associations.
- [ ] Validate the template, deploy the network stack, and verify CIDRs, routing, and stack outputs.

## 4. Planning

- [ ] Review quotas relevant to Milestone 2 (including sandbox EC2 instance type/count and storage restrictions).
- [ ] Choose and document the assumed architecture for one coordinator and two shards.
- [ ] Estimate monthly compute, storage, networking, and other applicable charges and compare with the sandbox credit ceiling.

## 5. Reproducibility and hand-in

- [ ] Delete only the project network stack and recreate it from IaC; record timings and what failed on the first attempt.
- [ ] Update README with setup, verification commands, changes in Milestone 1, limitations, and evidence/screenshots.
- [ ] Record an AI architecture critique and accept or reject 2–3 points with explanations.
- [ ] Prepare a working demo and rehearse explaining the ADRs, chosen implementation, and relevant control questions.
