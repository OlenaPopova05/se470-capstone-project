# CloudFormation Stack Layout

## Context

The project infrastructure will be managed using AWS CloudFormation. We need to decide how to organize AWS resources into stacks to make the infrastructure easier to manage, update, and maintain.

Two approaches were considered: a single CloudFormation stack or separate stacks for network and application resources.

## Alternatives Considered

### 1. Single Stack

**Advantages:**
- Simpler initial setup and deployment.
- All resources are managed in one place.
- No need to manage dependencies between stacks.

**Disadvantages:**
- All resources share the same deployment lifecycle.
- Changes to one part of the infrastructure may affect other components.
- Deleting the stack can remove both network and application resources.

### 2. Separate Stacks

**Advantages:**
- Better modularity and organization of infrastructure.
- Network and application resources can be updated independently.
- Individual components can be modified or recreated without unnecessarily affecting other parts of the system.

**Disadvantages:**
- Requires managing multiple CloudFormation templates.
- Resource identifiers must be shared between stacks.
- Dependencies between stacks must be considered during deployment and deletion.

## Decision

I decided to use **separate CloudFormation stacks** for network and application resources.

This approach makes the infrastructure more modular and easier to maintain. Different parts of the system can be updated or recreated independently without unnecessarily affecting other components.

## Consequences

- Network and application infrastructure will have separate deployment lifecycles.
- Changes to application resources will not normally require modifications to the network stack.
- Resource identifiers will need to be shared between stacks.
- Deployment and deletion order must account for dependencies between stacks.