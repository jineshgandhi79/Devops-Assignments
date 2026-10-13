# 02. AWS EC2 (Elastic Compute Cloud) - Compute

**Author:** Jinesh Gandhi  
**Domain:** Cloud Compute & Virtual Server Infrastructure  
**Service:** Amazon Elastic Compute Cloud (Amazon EC2)

---

## 1. What is EC2?

**Amazon Elastic Compute Cloud (Amazon EC2)** is a foundational AWS web service providing secure, resizable compute capacity in the cloud. It eliminates the need to invest in physical hardware upfront, enabling organizations to build, deploy, and scale virtual servers (**EC2 instances**) within minutes.

Key benefits include:
- **Elasticity**: Rapidly scale compute capacity up or down according to traffic demands.
- **Complete Control**: Root/Administrator-level access to the underlying virtual machine operating systems.
- **Pay-As-You-Go**: Billing calculated per second or per hour of compute instance usage.

---

## 2. Core Concepts & Building Blocks

### 2.1. Amazon Machine Image (AMI)
An **AMI** is a pre-configured template packaged with the operating system, architecture, application server, and required dependencies to launch an EC2 instance.
- **Types of AMIs**:
  - *AWS Managed AMIs*: Clean base OS images maintained by AWS (Amazon Linux 2023, Ubuntu, Red Hat Enterprise Linux, Windows Server).
  - *Custom AMIs (Golden Images)*: Baked by engineering teams with hardened security configs and pre-installed dependencies.
  - *AWS Marketplace AMIs*: Pre-packaged commercial appliances (e.g., Cisco firewalls, WordPress, Splunk).

### 2.2. Instance Types & Families
EC2 offers optimized instance configurations balancing vCPU, Memory, Storage, and Networking:

| Family | Prefix | Ideal Workload | Example |
|---|---|---|---|
| **General Purpose** | `t4g`, `m6i`, `m7g` | Web servers, small databases, code repositories | `t3.micro`, `m6i.large` |
| **Compute Optimized** | `c6i`, `c7g` | Batch processing, media transcoding, gaming servers, high-performance web servers | `c7g.xlarge` |
| **Memory Optimized** | `r6i`, `r7g`, `x2gd` | High-performance relational DBs, in-memory caches (Redis, Memcached), big data analytics | `r6i.2xlarge` |
| **Storage Optimized** | `i3en`, `d3`, `d3en` | Data warehousing, distributed file systems, Elasticsearch, Kafka clusters | `i3en.large` |
| **Accelerated Computing** | `g5`, `p4d`, `p5` | Machine learning training/inference, 3D rendering, graphics processing | `g5.xlarge` |

### 2.3. Key Pairs
Amazon EC2 uses public-key cryptography to authenticate and encrypt login credentials:
- **Public Key**: Retained by AWS and injected into `~/.ssh/authorized_keys` during instance initialization.
- **Private Key (`.pem` / `.ppk`)**: Downloaded and kept securely on the administrator's local machine.
- Used for passwordless SSH connection (`ssh -i key.pem ec2-user@<public-ip>`) on Linux, and decoding the initial Windows Administrator password.

### 2.4. Security Groups
A **Security Group** acts as a virtual firewall for your EC2 instance controlling inbound and outbound network traffic.
- **Stateful**: If you allow incoming traffic on port 80, the return traffic is automatically permitted regardless of outbound rules.
- **Allow-Only**: Security groups have allow rules only; you cannot write explicit deny rules (use Network ACLs for deny rules).
- **Default Behavior**: By default, all inbound traffic is blocked, and all outbound traffic is allowed.

### 2.5. Elastic Block Store (EBS)
**Amazon EBS** provides high-performance, persistent block-level storage volumes designed for use with EC2 instances.
- Operates like a virtual hard disk drive (independent of instance lifecycle).
- **Volume Types**:
  - *General Purpose SSD (`gp2`, `gp3`)*: Baseline 3,000 IOPS, balanced cost and throughput for boot volumes and system drives.
  - *Provisioned IOPS SSD (`io1`, `io2 Block Express`)*: Critical I/O-intensive database workloads requiring sub-millisecond latencies.
  - *Throughput Optimized HDD (`st1`)*: Frequently accessed sequential big data and log workloads.
  - *Cold HDD (`sc1`)*: Lowest-cost block storage for infrequent access workloads.
- **EBS Snapshots**: Point-in-time incremental backups backed up automatically to Amazon S3.

### 2.6. Public IP vs. Private IP vs. Elastic IP
- **Private IP Address**:
  - Assigned automatically to all instances in a VPC subnet.
  - Accessible only within the VPC or connected private networks (VPN, Direct Connect).
  - Remains with the instance through stop/start cycles.
- **Public IP Address**:
  - Assigned from Amazon's pool of public IPv4 addresses if enabled on the subnet.
  - Accessible across the public Internet.
  - **Dynamic**: Released and changes whenever the instance is stopped and started.
- **Elastic IP (EIP)**:
  - A static, allocated public IPv4 address that remains permanently associated with your AWS account until released.
  - Can be rapidly remapped to another instance during failover.

---

## 3. EC2 Instance Lifecycle

```
    [ Launch ]
        |
        v
    [ Pending ]  <---- (Allocating hardware, preparing AMI)
        |
        v
    [ Running ]  <----+ (Instance is active and passing status checks)
      |     |         |
      |     +--> [ Rebooting ]
      |               |
      v               |
   [ Stopping ]       |
      |               |
      v               |
   [ Stopped ]  ------+ (EBS data intact; no compute billing accrued)
      |
      v
   [ Shutting-down ]
      |
      v
   [ Terminated ]     (Hardware deallocated; root EBS deleted by default)
```

1. **Pending**: Instance preparation, acquiring host hardware.
2. **Running**: Compute actively serving requests. Status checks (System Status Check & Instance Status Check) passing 2/2.
3. **Stopping / Stopped**: Available for EBS-backed instances. Compute capacity released; RAM lost; root EBS storage remains persisted.
4. **Terminated**: Instance permanently destroyed and removed from EC2 management console.

---

## 4. Common Use Cases

1. **Container Hosts & Kubernetes Nodes**:
   - Serving as worker nodes for Amazon EKS (Elastic Kubernetes Service) or self-hosted Docker clusters.
2. **Enterprise Web and API Hosting**:
   - Paired with Auto Scaling Groups (ASG) and Application Load Balancers (ALB) to dynamically scale web traffic during peaks.
3. **Self-Managed Databases**:
   - Running specialized database software (e.g., MongoDB, Cassandra, Microsoft SQL Server with specific enterprise licensing) on Provisioned IOPS EBS volumes.
4. **CI/CD Build Runners**:
   - Ephemeral Jenkins or GitHub Actions self-hosted runners executing automated integration builds and container packaging.
5. **Batch Processing and Big Data Workers**:
   - Leveraging EC2 Spot Instances (at up to 90% discount) to process massive batch compute jobs where interruptions can be tolerated.
