# Task 7 — Monthly Cost Estimation

**Goal:** Estimate the monthly cost of one Coordinator and **two Shards** running on Amazon EC2, then compare it with the **$20 AWS Academy sandbox budget**.

## Assumptions

- Region: **us-east-1** (N. Virginia); Linux, On-Demand.
- **730 hours/month** (all instances running 24/7).
- Three EC2 instances; one **8 GB EBS gp2** volume each (24 GB total).
- One billed **public IPv4 address** (Coordinator); the Shards use private IPs.
- No NAT Gateway or Load Balancer.

## Unit prices used

| Item | Price |
|---|---:|
| `t3.nano` | $0.0052/hour |
| `t3.micro` | $0.0104/hour |
| EBS `gp2` | $0.10/GB-month |
| Public IPv4 | $0.005/hour |

Sources: [AWS EC2 T3](https://aws.amazon.com/ec2/instance-types/t3/), [AWS EBS pricing](https://aws.amazon.com/ebs/pricing/), [AWS VPC pricing](https://aws.amazon.com/vpc/pricing/). Prices are input assumptions from AWS published pricing; confirm in [AWS Pricing Calculator](https://calculator.aws/) before submission.

## Calculations

**Storage:** 3 × 8 × $0.10 = **$2.40/month**  
**Public IPv4:** 730 × $0.005 = **$3.65/month**

| Configuration (Coordinator + 2 Shards) | EC2 / month | EBS + IPv4 | Total / month | vs. $20 |
|---|---:|---:|---:|---:|
| `nano` + `nano` + `nano` | $11.39 | $6.05 | **$17.44** | $2.56 under |
| `micro` + `nano` + `nano` | $15.18 | $6.05 | **$21.23** | $1.23 over |
| `micro` + `micro` + `micro` | $22.78 | $6.05 | **$28.83** | $8.83 over |

Formula: **Monthly EC2 cost = number of instances × hourly instance rate × 730**.

## Conclusion

Only the **three `t3.nano`** configuration is below $20 in this basic estimate. However, 0.5 GiB RAM per `t3.nano` may be insufficient for the application. Additional charges (for example, network data transfer or T3 unlimited CPU credits) are **not included**. For development, running instances only when needed can reduce costs.

*This is a manual estimate using published AWS rates, not an exported AWS Pricing Calculator quote. The $20 sandbox credit is a budget ceiling, not a guarantee of one month of continuous operation.*
