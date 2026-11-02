## Task 6 — Service Quotas Review

The goal of this task was to review AWS service quotas and identify possible limitations for Milestone 2.

For the initial implementation, I considered using Amazon EC2 to run one Coordinator and two Shards. Therefore, I focused on EC2 compute limits and the networking resources required for the application.

All quotas were checked in the **us-east-1 (N. Virginia)** region, where the Network Stack was deployed.

### 1. EC2 — Running On-Demand Standard Instances

![alt text](<Screenshot 2026-11-02 at 07.15.49.png>)

The applied quota is **256 vCPUs**, with current utilization of 0.

For a possible architecture with three `t3.micro` instances (one Coordinator and two Shards), we would need 6 vCPUs in total.

Therefore, the EC2 vCPU quota is sufficient for our initial architecture. However, the AWS Academy sandbox has additional restrictions on instance types and quantities.

### 2. VPCs per Region

![alt text](<Screenshot 2026-11-02 at 07.22.34.png>)

The applied quota is **5 VPCs per region**, and 2 VPCs are currently in use.

One is the default VPC, while the second was created for our capstone project.

We plan to reuse the existing Capstone VPC in Milestone 2, so this quota should not limit our implementation.

### 3. Subnets per VPC

![alt text](<Screenshot 2026-11-02 at 07.24.57.png>)

The applied quota is **200 subnets per VPC**.

Our Capstone VPC currently contains 3 subnets: one public and two private.

AWS does not display utilization for this quota, but we verified the three subnets in the VPC Console.

This quota is sufficient for our current network architecture.

### 4. Internet Gateways per Region

![alt text](<Screenshot 2026-11-02 at 07.26.14.png>)

The applied quota is **5 Internet Gateways per region**.

We created one Internet Gateway and attached it to our Capstone VPC. It provides a route to the internet for the public subnet.

We do not plan to create additional Internet Gateways for Milestone 2, so this quota should not be a limitation.

### 5. AWS Academy Sandbox Restrictions

In addition to the standard AWS service quotas, the sandbox has its own restrictions.

The main restrictions are:

- Maximum of **9 EC2 instances**.
- Only `t2.nano` through `t2.medium` and `t3.nano` through `t3.medium` are allowed.
- EBS volumes are limited to 35 GB and the `gp2` type.
- IAM operations are restricted.
- The sandbox has a **$20 credit budget**.

These restrictions are important because they may be more limiting than the standard AWS quotas.

### Conclusion

The reviewed service quotas are sufficient for the initial EC2-based architecture with one Coordinator and two Shards.

The main limitations are the sandbox restrictions on EC2 instances, allowed instance types, storage, IAM permissions, and budget.

For Milestone 2, I will consider using small EC2 instances and reusing the existing VPC and subnets. The estimated monthly cost will be calculated in Task 7.