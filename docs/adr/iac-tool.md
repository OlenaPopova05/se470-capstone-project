# Choice of Infrastructure as Code Tool

## Context

Milestone 1 requires Infrastructure as Code (IaC) to create and manage AWS resources, such as VPCs, subnets, and routing configurations.

Two tools were considered: **AWS CloudFormation** and **Terraform**.

## Alternatives Considered

### 1. AWS CloudFormation

**Advantages:**
- Native AWS service, available directly in AWS Console.
- Uses YAML or JSON templates.
- AWS automatically manages infrastructure state, so no separate state backend is needed.
- Supports Change Sets to preview changes and Drift Detection to detect manual modifications.

**Disadvantages:**
- Mainly supports AWS.
- YAML templates can become complicated for large projects.

### 2. Terraform

**Advantages:**
- Supports multiple cloud providers (AWS, Azure, GCP).
- Uses HCL, a language designed for infrastructure configuration.
- Supports reusable modules, change previews (`terraform plan`), and drift detection.

**Disadvantages:**
- Requires installing Terraform and configuring the AWS provider.
- Uses a state file (`terraform.tfstate`) that needs to be managed. For CI/CD, a remote backend is usually recommended.
- Requires additional setup compared to CloudFormation.

## Decision

I chose **AWS CloudFormation** because the entire project runs in AWS Academy, so multi-cloud support is unnecessary.

CloudFormation is already integrated into AWS and manages infrastructure state automatically, without requiring a separate state backend.

Additionally, the AWS Academy Policy Simulator confirmed that `cloudformation:CreateStack` is allowed.

## Consequences

- Infrastructure can be created, updated, deleted, and recreated using YAML templates.
- Templates can be version-controlled using Git.
- Change Sets and Drift Detection help monitor infrastructure changes.
- No separate IaC tool or state backend is required.
- The project becomes more dependent on AWS.