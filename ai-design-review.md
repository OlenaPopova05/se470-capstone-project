# Milestone 1 — AI Architecture Design Review

## 1. Architecture Overview

The project aims to develop a distributed key-value store with a Coordinator and multiple Shards.

For Milestone 1, I created the network infrastructure using AWS CloudFormation. The architecture includes:

- One VPC (`10.0.0.0/16`).
- One public subnet and two private subnets across two Availability Zones.
- An Internet Gateway and a public route table.
- A private route table with only local routing.
- Separate Network and Application Stacks (the Application Stack is planned for Milestone 2).
- Read-only IAM Policy and Role templates, which were not deployed due to sandbox restrictions.

The infrastructure was successfully deployed and recreated using CloudFormation.

## 2. AI Architecture Critique

### Issue 1 — No Internet Access from Private Subnets

**AI Critique:**

Private subnets do not have a NAT Gateway or another way to access the internet. This may cause problems when installing dependencies, downloading updates, or deploying code to private EC2 instances.

**Decision: Partially Accept**

I agree that private EC2 instances may require outbound internet access during deployment. However, a NAT Gateway would significantly increase costs, which is a problem with the $20 sandbox budget.

For now, I will keep the private subnets isolated. In Milestone 2, I will consider using preconfigured images or another deployment method that does not require direct internet access.

### Issue 2 — Limited High Availability

**AI Critique:**

Although the private subnets are distributed across two Availability Zones, this alone does not provide high availability. If the Coordinator runs on only one EC2 instance, it becomes a single point of failure.

**Decision: Accept**

I agree with this concern. Currently, the architecture only prepares the network for future application deployment.

In Milestone 2, the initial implementation may use one Coordinator to keep the system simple. However, in later milestones, I will consider replication and failover mechanisms to improve availability.

### Issue 3 — EC2 May Be Expensive and Requires Server Management

**AI Critique:**

Using separate EC2 instances for the Coordinator and Shards can increase costs and requires managing operating systems, updates, and deployment. It also does not fully follow the serverless approach described in the project.

**Decision: Partially Accept**

I agree that EC2 introduces additional management and costs. However, it provides more control over running processes and makes it easier to implement and test my own sharding logic.

For the initial implementation, I plan to use small EC2 instances and run them only when needed for development and testing.

I will also consider containers or serverless services if they become more suitable for later milestones.

## 3. Conclusion

The AI review identified three important risks: lack of internet access from private subnets, limited high availability, and the cost and management overhead of EC2.

I accepted or partially accepted these points. However, I decided not to make unnecessary changes to the current network because it satisfies the requirements of Milestone 1.

The identified limitations will be considered during the implementation of Milestone 2 and later milestones.
