# 01. AWS IAM (Identity and Access Management) - Governance

**Author:** Jinesh Gandhi  
**Domain:** Cloud Security, Governance & Access Control  
**Service:** AWS Identity and Access Management (IAM)

---

## 1. What is IAM?

**AWS Identity and Access Management (IAM)** is a web service that helps you securely control individual and programmatic access to AWS resources. IAM is a **global service** (no region selection required) that authenticates (verifies who you are) and authorizes (specifies what you can do) principals across your AWS infrastructure.

IAM provides centralized administration of:
- **Authentication**: Managing identities via passwords, Access Keys, Multi-Factor Authentication (MFA), and federated single sign-on (SSO).
- **Authorization**: Granular policies dictating allowed or denied actions on specific AWS resource ARNs under precise conditions.

---

## 2. Core Concepts & Building Blocks

### 2.1. IAM Users
An **IAM User** represents an individual person or service that interacts with AWS.
- Contains credentials: Password for AWS Management Console access, and up to 2 active Access Key ID & Secret Access Key pairs for CLI/API/SDK programmatic access.
- Recommended practice: Avoid creating IAM users with long-term keys for applications; use IAM Roles instead.

### 2.2. IAM User Groups
An **IAM Group** is a collection of IAM users.
- Groups simplify permission management by allowing administrators to attach policies to the group rather than each user individually.
- Examples: `Developers`, `SecurityAuditors`, `DBAdmins`.
- Note: Groups cannot be identified as a `Principal` in resource-based policies, and groups cannot be nested inside other groups.

### 2.3. IAM Roles
An **IAM Role** is an identity with specific permission policies that can be assumed by trusted entities for a temporary period.
- Roles do **not** have permanent credentials (no static passwords or access keys).
- When assumed (via AWS Security Token Service - STS), AWS provides **temporary security credentials** that automatically expire (15 minutes to 12 hours).
- **Who can assume a role?**
  - AWS Services (e.g., EC2 instances accessing S3, Lambda reading from DynamoDB).
  - External users federated via SAML 2.0 or OpenID Connect (OIDC) (e.g., Okta, Google Workspace, GitHub Actions).
  - Cross-account IAM users (e.g., switching from Dev account to Prod account).

### 2.4. IAM Policies
An **IAM Policy** is a formal JSON document defining permissions. A policy contains one or more `Statement` blocks.

**Structure of a JSON Policy Statement:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ReadOnlyDevBucket",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::jinesh-dev-bucket",
        "arn:aws:s3:::jinesh-dev-bucket/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "true"
        }
      }
    }
  ]
}
```

**Policy Elements:**
| Element | Purpose | Description |
|---|---|---|
| `Effect` | Allow or Deny | The result of the policy evaluation. Explicit Deny always overrides Allow. |
| `Action` | API calls | Specific AWS API actions (e.g., `ec2:DescribeInstances`, `s3:PutObject`). |
| `Resource` | Target ARNs | The exact Amazon Resource Name(s) the action applies to. |
| `Condition` | Guardrails | Contextual filters (e.g., IP address whitelist, requiring MFA, SSL enforcement). |

### 2.5. Types of Policies
1. **Identity-Based Policies**: Attached directly to Users, Groups, or Roles.
   - *AWS Managed Policies*: Standard policies maintained by AWS (e.g., `AdministratorAccess`, `AmazonS3ReadOnlyAccess`).
   - *Customer Managed Policies*: Custom policies created and versioned by your organization.
   - *Inline Policies*: Embedded directly into a single principal (generally discouraged in favor of customer managed).
2. **Resource-Based Policies**: Attached directly to AWS resources (e.g., S3 Bucket Policies, KMS Key Policies, SQS Queue Policies).
3. **Service Control Policies (SCPs)**: Organization-level guardrails applied across member AWS accounts in AWS Organizations.

---

## 3. The Principle of Least Privilege

The **Principle of Least Privilege (PoLP)** dictates that a user, service, or program must be granted **only the minimum permissions necessary** to perform its assigned duties—and nothing more.

### How Least Privilege is Enforced:
1. **Default Deny**: By default, all requests are implicitly denied unless explicitly allowed.
2. **Evaluation Logic**:
   - Step 1: Start with implicit deny.
   - Step 2: Evaluate all applicable policies.
   - Step 3: If an **Explicit Deny** exists anywhere $\rightarrow$ **DENY**.
   - Step 4: If an **Explicit Allow** exists and no explicit deny $\rightarrow$ **ALLOW**.
   - Step 5: Otherwise $\rightarrow$ **DENY**.
3. **Scoping Resources**: Never use `"Resource": "*"` for state-mutating actions (`Delete*`, `Put*`, `Update*`). Specify exact bucket names, instance IDs, or ARN prefixes.
4. **Conditional Access**: Require MFA tokens or restrict CIDR IP ranges for critical administrative tasks.

---

## 4. IAM Best Practices

1. **Lock Away the AWS Account Root User**:
   - Never use the root user for daily administrative or development tasks.
   - Enable hardware or virtual MFA on the root account and keep credentials in a secure physical vault.
2. **Enforce Multi-Factor Authentication (MFA)**:
   - Mandatory for all IAM users with console access.
3. **Use IAM Roles for Workloads & EC2**:
   - Never hardcode AWS Access Keys in application code, configuration files, or Docker images.
   - Assign an **IAM Instance Profile** to EC2 or ECS tasks.
4. **Regularly Rotate and Audit Credentials**:
   - Enable automated rotation for access keys.
   - Use IAM Credential Reports and AWS Access Analyzer to identify unused permissions.
5. **Use IAM Identity Center (AWS SSO) for Humans**:
   - Centralize enterprise identity management by connecting to Okta, Azure AD, or PingIdentity.
6. **Implement Permission Boundaries**:
   - Guardrails to ensure developers cannot create IAM roles with higher privileges than themselves (prevent privilege escalation).

---

## 5. Common Use Cases

| Scenario | Architectural Solution |
|---|---|
| **EC2 Web App uploading logs to S3** | Attach an IAM Role with `s3:PutObject` permission to the EC2 Instance Profile; AWS STS delivers temporary rotated keys automatically. |
| **GitHub Actions CI/CD deploying to AWS** | Configure OpenID Connect (OIDC) identity provider in IAM so GitHub Actions can assume a deployment role without storing static AWS secret keys in GitHub secrets. |
| **Multi-Tier Departmental Separation** | Create IAM Groups (`Developers`, `QATesters`, `DataEngineers`) and attach targeted customer-managed policies to manage changes centrally. |
| **Cross-Account Audit Access** | Create an IAM Role in the Production account trusting the Security Audit account ARN; auditors switch roles securely without duplicate users. |
| **Enforcing TLS / HTTPS on Storage** | Write an S3 bucket policy with an explicit Deny statement where `aws:SecureTransport` is `false`. |
