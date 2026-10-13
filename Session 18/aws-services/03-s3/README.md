# 03. AWS S3 (Simple Storage Service) - Storage

**Author:** Jinesh Gandhi  
**Domain:** Object Storage & Data Lake Architecture  
**Service:** Amazon Simple Storage Service (Amazon S3)

---

## 1. What is S3?

**Amazon Simple Storage Service (Amazon S3)** is an industry-leading object storage service offering industry-leading scalability, data availability, security, and performance. 

Unlike traditional block storage (EBS) or file system hierarchies (EFS), S3 stores data as **objects** within logical containers called **buckets**. S3 is designed to deliver **99.999999999% (11 9's) of data durability** by automatically distributing stored data across a minimum of three physically distinct Availability Zones (AZs) within an AWS Region.

---

## 2. Core Concepts & Building Blocks

### 2.1. S3 Buckets
A **Bucket** is a top-level container for objects stored in Amazon S3.
- **Naming Rule**: Bucket names must be **globally unique across all AWS accounts worldwide**, between 3 and 63 characters long, and DNS-compliant (lowercase letters, numbers, and hyphens only).
- Created within a specific AWS Region (e.g., `us-east-1`, `eu-west-1`).

### 2.2. S3 Objects
An **Object** is the fundamental entity stored in Amazon S3, composed of:
- **Key**: The unique name/identifier for the object inside the bucket (e.g., `images/profile-picture.png`).
- **Value**: The data content itself (ranging from 0 bytes up to a maximum of 5 TB per individual object).
- **Metadata**: Key-value pairs containing system properties (e.g., `Content-Type`, `Content-Length`) and custom user metadata.
- **Version ID**: A unique string assigned when versioning is active.

### 2.3. S3 Storage Classes
AWS provides tiered storage classes optimized for different access patterns and cost profiles:

| Storage Class | Durability | Availability | Min Storage Duration | Typical Use Case |
|---|---|---|---|---|
| **S3 Standard** | 99.999999999% | 99.99% | None | Frequently accessed data, active websites, dynamic applications, mobile app assets |
| **S3 Intelligent-Tiering** | 99.999999999% | 99.9% | None (small monitoring fee) | Unknown, unpredictable, or changing access patterns (auto-moves objects without retrieval fees) |
| **S3 Standard-IA (Infrequent Access)** | 99.999999999% | 99.9% | 30 days | Long-term data requiring rapid ms access (disaster recovery backups, audit logs) |
| **S3 One Zone-IA** | 99.999999999% | 99.5% | 30 days | Secondary backup copies, re-creatable thumbnails, non-critical data in 1 AZ |
| **S3 Glacier Flexible Retrieval** | 99.999999999% | 99.9% | 90 days | Regulatory archives, medical records; retrieval time 1 min (expedited) to 5 hours |
| **S3 Glacier Deep Archive** | 99.999999999% | 99.9% | 180 days | Lowest-cost cloud storage ($1/TB/month); compliance archives; retrieval 12-48 hours |

### 2.4. S3 Versioning
**Versioning** preserves, retrieves, and restores every version of every object stored in your Amazon S3 bucket.
- **Protection Against Accidents**: If a user overwrites or deletes an object, the previous version remains preserved.
- **Delete Markers**: When an object is deleted in a version-enabled bucket, S3 inserts a delete marker instead of permanently erasing the data. An administrator can simply delete the marker to restore the file.
- **Lifecycle**: Once enabled, versioning cannot be disabled; it can only be suspended.

### 2.5. Lifecycle Policies
**S3 Lifecycle Management** defines automated rules that direct S3 to manage objects cost-effectively over time:
- **Transition Actions**: Automatically migrate objects from expensive storage classes to lower-cost tiers (e.g., Move to Standard-IA after 30 days $\rightarrow$ Move to Glacier Flexible Retrieval after 90 days).
- **Expiration Actions**: Permanently delete old objects or noncurrent version generations after a specified retention threshold (e.g., delete noncurrent versions after 365 days).

### 2.6. Encryption Mechanisms
AWS S3 supports robust data-at-rest encryption:
1. **Server-Side Encryption with Amazon S3-Managed Keys (SSE-S3)**: Default AES-256 encryption handled automatically by AWS without additional cost.
2. **Server-Side Encryption with AWS KMS Keys (SSE-KMS)**: Uses AWS Key Management Service providing audit logs (via CloudTrail) and customizable key rotation policies.
3. **Server-Side Encryption with Customer-Provided Keys (SSE-C)**: The client manages the cryptographic keys while AWS manages encryption and decryption operations.
4. **Client-Side Encryption**: Encrypting data before uploading to S3 using the AWS Encryption SDK.

### 2.7. Bucket Policies & Public Access Block
- **Bucket Policy**: A JSON-based resource policy attached directly to the bucket to regulate access by AWS principals, IP ranges, or referrers.
- **S3 Block Public Access (PAB)**: A centralized security safeguard that overrides all existing and future ACLs and bucket policies, ensuring that private data is never unintentionally exposed to the public internet.

---

## 3. Common Use Cases

1. **Static Website Hosting**:
   - Serving static HTML, CSS, JavaScript, and SPA frontends (React, Angular, Vue) globally with zero server overhead.
2. **Cloud Data Lakes & Analytics**:
   - Serving as the centralized repository for raw, structured, and semi-structured big data queried via Amazon Athena, AWS Glue, and Amazon EMR.
3. **Enterprise Backup & Disaster Recovery**:
   - Long-term archiving of database snapshots, virtual machine images, and file system backups utilizing S3 Glacier Deep Archive.
4. **Software & Media Distribution**:
   - Paired with Amazon CloudFront (CDN) to distribute software packages, streaming video files, and high-resolution assets with low latency.
5. **Application File Attachments**:
   - Storing user profile avatars, invoices, document attachments, and user uploads with pre-signed URLs providing controlled, time-limited download access.
