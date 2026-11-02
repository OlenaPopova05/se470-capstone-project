## ADDED Requirements

### Requirement: Read-only IAM policy

The infrastructure SHALL define an IAM policy as CloudFormation code that grants only selected read/list/describe permissions for AWS resources relevant to the project and grants no create, update, or delete actions.

#### Scenario: Inspect an allowed resource
- **WHEN** a principal with this policy and no conflicting restrictions requests a listed read action on an allowed resource
- **THEN** the policy grants that action.

#### Scenario: Attempt a write operation
- **WHEN** a principal with only this policy attempts a write action such as `ec2:RunInstances`
- **THEN** the policy does not authorize the action, so it is implicitly denied.

### Requirement: Assumable role

The infrastructure SHALL define an IAM role with a trust policy for a specific trusted principal and with the read-only permissions attached.

#### Scenario: Trusted principal assumes the role
- **WHEN** the designated principal is authorized to call `sts:AssumeRole` and the trust policy conditions are satisfied
- **THEN** it can assume the role and obtain temporary credentials.

#### Scenario: Untrusted principal requests the role
- **WHEN** a principal not permitted by the trust policy attempts to assume the role
- **THEN** the trust policy does not grant assumption.

### Requirement: Sandbox-safe IAM delivery

The IAM policy and role SHALL be delivered as IaC templates without attempting to create or attach IAM resources in the restricted sandbox.

#### Scenario: Validate IAM code
- **WHEN** the IAM template is reviewed or statically validated
- **THEN** its policy, role, and trust relationships can be inspected without deploying IAM resources.

#### Scenario: Explain sandbox restrictions
- **WHEN** the IAM deliverable is reviewed
- **THEN** the documentation records the `iam:CreatePolicy` and `iam:CreateRole` simulation results (`implicitDeny`) and explains why deployment was skipped.
