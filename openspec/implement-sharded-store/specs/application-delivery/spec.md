## ADDED Requirements

### Requirement: Reproducible application infrastructure

The application infrastructure SHALL be described by CloudFormation in a stack separate from the existing network stack. It SHALL support one Coordinator and two shards using the AWS Academy sandbox and reuse network identifiers exported by the network stack.

#### Scenario: Deploy the application
- **WHEN** the network stack exists and the application template is deployed
- **THEN** a Coordinator and two reachable internal shard services can be started without manually creating the application infrastructure.

#### Scenario: Restrict internal endpoints
- **WHEN** a client outside the shard network attempts to access shard-local record endpoints
- **THEN** network rules do not expose those endpoints as public application entry points.

### Requirement: CI/CD deployment path

The repository SHALL contain a CI/CD pipeline that checks the application and deploys both infrastructure and application updates. The delivery method SHALL be verified against AWS Academy permissions and the absence of general outbound internet from the private subnets before relying on it.

#### Scenario: Infrastructure update
- **WHEN** an approved application-stack template change is delivered through the pipeline
- **THEN** the pipeline applies that change with CloudFormation and reports the result.

#### Scenario: Application update
- **WHEN** an approved application build is delivered through the pipeline
- **THEN** the running Coordinator and shard services are updated and can be verified through the external API.

### Requirement: Local startup and hand-in

The repository SHALL provide a repeatable local startup for the Coordinator and two shards, a smoke test, and a README covering startup, verification, changes since Milestone 1, and known limitations. The Milestone 2 hand-in SHALL include an AI architecture critique with responses to two or three points.

#### Scenario: Local demo
- **WHEN** a reviewer follows the README on a supported development machine
- **THEN** they can start the system and verify table registration, CRUD, and shard routing.
