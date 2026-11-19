# Milestone 2 Application Compute and Network Placement

## Context

Milestone 2 needs one Coordinator and two independent shard services in the AWS Academy sandbox. The Milestone 1 network stack already provides one public subnet, two private subnets, and exported IDs. The sandbox limits EC2 instance types and budget, restricts IAM operations, and gives private subnets no general internet route.

## Options

1. **Three EC2 instances.** One process can run on each instance, with direct private HTTP between Coordinator and shards. This matches the local multi-process design and the existing cost estimate. Application installation and updates still need a delivery path.
2. **Managed containers.** ECS/Fargate could run the services but adds service, image registry, IAM, and networking dependencies whose sandbox permissions and cost have not been verified.
3. **One instance for all services.** This is cheaper and easier to bootstrap but would not demonstrate physical shard placement across separate nodes.

## Decision

Use three small EC2 instances in a separate CloudFormation application stack. Put the Coordinator in the public subnet and one shard in each private subnet. Give only the Coordinator a public IPv4 address. Permit client access to its port 8080 from a deployment parameter `ClientCidr`; permit shard registration to the Coordinator's private port 8080 and shard-local CRUD from the Coordinator to port 8081. Each shard runs on its own instance and may use the same port 8081.

Default to `t3.nano` and 8 GiB `gp2` root volumes, matching the Milestone 1 budget assumptions. Set T-instance CPU credits to `standard` to avoid unlimited-credit charges. Supply the AMI ID and its root device name at deployment time, because the sandbox's allowed image and application delivery path have not yet been verified.

## Consequences

- The application stack imports the existing network exports and can be replaced without rebuilding the VPC.
- Shard instances have no public address, and their record API is reachable only from the Coordinator security group. VPC-local routing allows the shards to register with the Coordinator.
- The Coordinator's port 8080 also carries `/internal/shards/register`; the client CIDR must be restricted to trusted callers until a separate authenticated or path-filtered public entry point is added.
- The template provisions compute and network access, but does not install or start application code. Private subnets cannot download packages from the internet; the artifact and credential path must be verified before AWS application deployment and CI/CD are added.
- `t3.nano` has limited memory. Measure application startup and workload behavior in the sandbox; use a larger allowed type for short runs if needed, with the budget impact recorded.

## References

- [CloudFormation EC2 instance properties](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-ec2-instance.html)
- [CloudFormation security group behavior](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-ec2-securitygroup.html)
- [CloudFormation cross-stack imports](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/intrinsic-function-reference-importvalue.html)
- [CloudFormation CPU credit options](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-ec2-instance-creditspecification.html)
