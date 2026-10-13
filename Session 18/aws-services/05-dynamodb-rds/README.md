# 05. AWS DynamoDB & RDS - Database Services

**Author:** Jinesh Gandhi  
**Domain:** Cloud Managed Relational & NoSQL Database Services  
**Services:** Amazon DynamoDB & Amazon Relational Database Service (Amazon RDS)

---

## 1. Amazon DynamoDB (NoSQL Key-Value & Document DB)

### 1.1. What is DynamoDB?
**Amazon DynamoDB** is a fully managed, serverless, key-value and document NoSQL database designed for fast, flexible performance at any scale. It delivers consistent **single-digit millisecond response times** and automatic multi-region, multi-active data replication with built-in security, backup, and in-memory caching via DAX (DynamoDB Accelerator).

### 1.2. Core Data Modeling Elements
- **Tables**: Similar to a collection in MongoDB or a table in SQL. Contains a collection of data items.
- **Items**: A group of attributes that is uniquely identifiable among all other items (similar to a row in a relational database or a JSON document). Max item size: 400 KB.
- **Attributes**: A fundamental data element, analogous to a field or column. Unlike SQL, DynamoDB is schemaless (except for primary key attributes)—items in the same table can contain completely different attributes.

### 1.3. Primary Keys: Partition Key vs. Sort Key
DynamoDB uses primary keys to uniquely identify each item in a table and distribute data across partitions:

1. **Simple Primary Key (Partition Key only)**:
   - Also known as the **Hash Key**.
   - DynamoDB uses the partition key value as input to an internal hash function to determine physical storage partition.
   - Every item must have a unique partition key (e.g., `UserID: "usr_98124"`).
2. **Composite Primary Key (Partition Key + Sort Key)**:
   - **Partition Key (Hash Key)** + **Sort Key (Range Key)**.
   - All items with the same partition key are stored together in physical proximity, sorted in ascending order by sort key value.
   - Allows querying ranges using operators like `>`, `<`, `BETWEEN`, `begins_with` (e.g., `PartitionKey = "CustomerID#101"`, `SortKey = "OrderDate#2026-10-13"`).

### 1.4. Key Features & Strengths
- **Capacity Modes**:
  - *On-Demand*: Scales automatically to accommodate unexpected bursts without capacity planning (pay-per-request).
  - *Provisioned*: Specify Read Capacity Units (RCU) and Write Capacity Units (WCU) with auto-scaling to optimize costs.
- **DynamoDB Streams**: Captures time-ordered sequences of item-level modifications for event-driven architectures (triggering AWS Lambda).
- **Global Tables**: Fully managed multi-region, active-active replication with automatic resolution.

### 1.5. Common Use Cases
- High-velocity session store for web and mobile applications.
- Real-time gaming leaderboards and player profiles.
- E-commerce shopping carts and product catalog lookups.
- IoT telemetry sensor data ingestion.

---

## 2. Amazon RDS (Relational Database Service)

### 2.1. What is RDS?
**Amazon Relational Database Service (Amazon RDS)** is a managed web service that simplifies the setup, operation, and scaling of relational databases in the cloud. It automates time-consuming administrative tasks such as hardware provisioning, operating system patching, database setup, automated backups, and failure recovery.

### 2.2. Supported Database Engines
Amazon RDS supports six industry-standard relational database engines:
1. **Amazon Aurora** (MySQL & PostgreSQL compatible, cloud-native high throughput)
2. **PostgreSQL**
3. **MySQL**
4. **MariaDB**
5. **Oracle Database**
6. **Microsoft SQL Server**

### 2.3. DB Instances & Storage
- **DB Instance**: An isolated database environment in the cloud running a specific DB engine version with dedicated compute resources (CPU, Memory).
- **Storage Types**:
  - *General Purpose SSD (`gp2`, `gp3`)*: Standard transaction workloads.
  - *Provisioned IOPS SSD (`io1`)*: High-throughput, latency-sensitive enterprise I/O workloads.

### 2.4. Security Architecture
- **Network Isolation**: Placed inside private subnets of a VPC, with no direct public route.
- **Access Control**: Database access controlled via RDS DB Security Groups filtering client IP/ENIs on specific engine ports (e.g., 5432 for Postgres, 3306 for MySQL).
- **Encryption**:
  - *Encryption-at-Rest*: Powered by AWS KMS (encrypts tables, automated backups, read replicas, and snapshots).
  - *Encryption-in-Transit*: Mandatory SSL/TLS connections for client queries.
  - *IAM Authentication*: Ability to authenticate database users via IAM tokens instead of hardcoded passwords.

### 2.5. Automated Backups & Snapshots
- **Automated Backups**: Continuous transaction log capture and daily storage volume snapshots with a retention period of 1 to 35 days. Enables Point-in-Time Recovery (PITR) down to a specific second.
- **Manual DB Snapshots**: User-initiated point-in-time backups that persist even after the parent RDS instance is deleted.

### 2.6. High Availability: Multi-AZ Deployments

```
+-----------------------------------------------------------------------------------+
| Multi-AZ Deployment Architecture                                                  |
|                                                                                   |
|     Availability Zone A (Primary)                 Availability Zone B (Standby)   |
|  +---------------------------------+           +--------------------------------+ |
|  |     Primary DB Instance         |           |     Standby DB Instance        | |
|  |       (Active Reads/Writes)     |           |        (Passive Sync)          | |
|  +---------------------------------+           +--------------------------------+ |
|                  |                                              ^                 |
|                  |========= Synchronous Block Replication =====|                 |
|                                                                                   |
|  [ In event of outage: Automatic DNS Failover takes ~60-120 seconds with 0 data loss ]
+-----------------------------------------------------------------------------------+
```

- Synchronous physical block-level replication to a standby instance in another Availability Zone.
- Purely for **High Availability & Disaster Recovery** (standby instance cannot accept read traffic).
- Automatic DNS failover occurs in 60-120 seconds if the primary host suffers hardware failure or network disruption.

### 2.7. Scalability: Read Replicas

```
+-----------------------------------------------------------------------------------+
| Read Replica Architecture                                                         |
|                                                                                   |
|  [ Primary DB Instance ] (Writes & Reads)                                         |
|            |                                                                      |
|            |------- Asynchronous Replication ------+---------------------+        |
|            |                                       |                     |        |
|            v                                       v                     v        |
|   [ Read Replica 1 ]                      [ Read Replica 2 ]    [ Read Replica 3 ]|
|   (Reporting / BI)                        (Web App Reads)       (Cross-Region)    |
+-----------------------------------------------------------------------------------+
```

- **Asynchronous replication** from the primary instance.
- Used to scale **read throughput** for read-heavy workloads (e.g., analytics, dashboards).
- Can be created across different AWS Regions.
- Can be promoted to an independent standalone database if necessary.

---

## 3. Direct Comparison: DynamoDB vs. Amazon RDS

| Dimension | Amazon DynamoDB | Amazon RDS |
|---|---|---|
| **Data Model** | NoSQL (Key-Value, Document) | Relational (SQL, Tables, Foreign Keys, Schemas) |
| **Schema** | Flexible / Dynamic / Schemaless | Fixed, strict relational schema |
| **Scalability** | Horizontal (Automatic partitioning, virtually infinite) | Vertical scaling (compute/storage) + Read Replicas |
| **Latency** | Single-digit millisecond at any scale | Millisecond, dependent on query complexity and index size |
| **Complex Joins / ACID** | Optimized for targeted queries (No complex SQL joins) | Full ACID compliance with multi-table joins |
| **Management** | 100% Serverless | Managed instances (OS/hardware managed, engine tuned) |
| **Pricing Model** | Per request (on-demand) or provisioned RCU/WCU | Per instance-hour + allocated storage volume GB |

---

## 4. Architectural Selection Guide

```
Does the workload require complex relational joins and ACID constraints across dozens of tables?
  ├── YES ──> Choose Amazon RDS (PostgreSQL / MySQL / Aurora)
  └── NO  ──> Does the workload demand ultra-low single-digit ms latencies with massive throughput?
                ├── YES ──> Choose Amazon DynamoDB
                └── NO  ──> Compare cost, access patterns, and team familiarity
```
