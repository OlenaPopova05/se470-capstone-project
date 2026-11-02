## ADDED Requirements

### Requirement: Dedicated VPC address space

The infrastructure SHALL create a dedicated VPC with CIDR `10.0.0.0/16` and three non-overlapping IPv4 subnets: public `10.0.1.0/24`, private 1 `10.0.2.0/24`, and private 2 `10.0.3.0/24`.

#### Scenario: Verify network addressing
- **WHEN** the network stack is deployed
- **THEN** the VPC and all three subnets exist with the specified CIDRs and belong to the same VPC.

### Requirement: Public subnet routing

The infrastructure SHALL attach an Internet Gateway to the VPC and associate the public subnet with a route table containing `0.0.0.0/0` directed to that gateway.

#### Scenario: Inspect the public route table
- **WHEN** the public subnet's route table is inspected
- **THEN** its default IPv4 route points to the attached Internet Gateway.

### Requirement: Private subnet routing

The infrastructure SHALL keep private subnets without a direct default route to the Internet Gateway. Both private subnets SHALL be explicitly associated with a private route table.

#### Scenario: Inspect private routing
- **WHEN** either private subnet's route table is inspected
- **THEN** it contains the VPC local route and no default route to the Internet Gateway.

### Requirement: Network managed as a separate stack

The network resources SHALL be defined in a standalone CloudFormation template, independently of application resources, and SHALL expose necessary network identifiers for later use.

#### Scenario: Deploy the network
- **WHEN** the network stack is created using CloudFormation
- **THEN** VPC, subnets, gateway, and routing resources are created without an application stack.

### Requirement: Reproducible deployment

The deployed network SHALL be removable and recreatable from the committed IaC template alone.

#### Scenario: Recreate the network
- **WHEN** the managed network stack is deleted and created again using only the template
- **THEN** the expected network topology is recreated and the duration and first-attempt issues are documented.

### Requirement: Quota and cost assessment

The project SHALL document service quotas relevant to a two-shard deployment and a monthly cost estimate for one coordinator and two shards, compared with the actual AWS Academy credit ceiling.

#### Scenario: Review the infrastructure plan
- **WHEN** the planning documentation is reviewed
- **THEN** it identifies the assumed services, sizes, hours, region, relevant quotas, estimated monthly total, and budget comparison.
