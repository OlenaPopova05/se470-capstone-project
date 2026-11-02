Спочатку я визначила свою роль за допомогою команди `aws sts get-caller-identity`у AWS CLI і виявила, що я працюю через IAM Role voclabs.
![alt text](<Screenshot 2026-10-29 at 14.49.11.png>)

Потім я хотіла переглянути permissions моєї ролі через ui і виявила, що моя роль має Explicit Deny для iam:GetRole.
![alt text](<Screenshot 2026-10-29 at 14.52.16.png>)

Тому я вирішила перевірити їх через AWS CLI через наступні дві команди: `aws ec2 describe-vpcs` і `aws ec2 describe-instances`.
![alt text](<Screenshot 2026-10-29 at 15.32.21.png>)

Також я спробувала переглянути permissions через policy simulator, але через Explicit Deny на iam:GetRolePolicy, я не змогла провести симуляцію.
![alt text](<Screenshot 2026-10-29 at 16.42.41.png>)


| AWS Action | Result | Verification method |
|---|---|---|
| `sts:GetCallerIdentity` | Allowed | AWS CLI |
| `iam:ListRoles` | Allowed | AWS Console |
| `iam:GetRole` | Explicit Deny | AWS Console |
| `iam:GetRolePolicy` | Explicit Deny | Policy Simulator |
| `ec2:DescribeVpcs` | Allowed | AWS CLI |
| `ec2:DescribeInstances` | Allowed | AWS CLI |


Після цього я використала AWS CLI для симуляції permissions, необхідних для виконання Milestone 1.

Результати показали, що `iam:CreateRole` та `iam:CreatePolicy` мають статус `implicitDeny`, тобто роль не має необхідних дозволів для створення IAM Roles та Policies.

Водночас `ec2:CreateVpc` і `cloudformation:CreateStack` отримали статус `allowed`. Отже, відповідно до результатів симуляції, я можу створювати VPC та CloudFormation stacks.

Таким чином, IAM Policy та Role я опишу через Infrastructure as Code без розгортання в sandbox, а мережеву інфраструктуру планую створити через CloudFormation.
![alt text](<Screenshot 2026-10-29 at 18.38.00.png>)
