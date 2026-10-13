# 04. AWS VPC (Virtual Private Cloud) - Networking

**Author:** Jinesh Gandhi  
**Domain:** Cloud Networking, Perimeter Security & Topology  
**Service:** Amazon Virtual Private Cloud (Amazon VPC)

---

## 1. What is VPC?

**Amazon Virtual Private Cloud (Amazon VPC)** enables you to provision a logically isolated, software-defined virtual network section within the AWS Cloud. It provides complete administrative control over your virtual networking environment, including the selection of your own IP address range, creation of subnets, and configuration of route tables, network gateways, and access controls.

A VPC is bounded within a single AWS Region, spanning across all Availability Zones (AZs) in that region.

---

## 2. Core Concepts & Building Blocks

### 2.1. CIDR Blocks (Classless Inter-Domain Routing)
When creating a VPC, you assign an IPv4 CIDR block representing the primary private IP address space (e.g., `10.0.0.0/16`).
- A `/16` network provides $2^{16} = 65,536$ total IP addresses.
- Allowed VPC CIDR block sizes range from `/16` (largest, 65,536 IPs) down to `/28` (smallest, 16 IPs).
- Recommended private IPv4 RFC 1918 ranges: `10.0.0.0/16`, `172.16.0.0/16`, or `192.168.0.0/16`.

### 2.2. Subnets
A **Subnet** is a range of IP addresses carved out from your VPC CIDR block.
- Each subnet must reside entirely within a single **Availability Zone (AZ)**.
- **AWS Reserved IPs**: In every subnet, AWS reserves **5 IP addresses** for internal networking:
  - `.0`: Network address.
  - `.1`: Assigned to the AWS VPC router default gateway.
  - `.2`: Assigned to the AWS Amazon Provided DNS (Amazon Route 53 Resolver).
  - `.3`: Reserved by AWS for future use.
  - `.255`: Network broadcast address (AWS VPC does not support broadcast, but address is reserved).
- Thus, a `/24` subnet ($256$ IPs) yields $256 - 5 = 251$ usable host IPs.

### 2.3. Route Tables
A **Route Table** contains a set of rules (routes) that determine where network traffic from your subnet or gateway is directed.
- Every VPC has a default **Main Route Table**.
- Contains a default local route: `10.0.0.0/16 -> local` (allows all subnets in the VPC to communicate with each other).
- Destination addresses are evaluated using **longest prefix matching**.

### 2.4. Internet Gateway (IGW)
An **Internet Gateway** is a horizontally scaled, redundant, highly available VPC component that enables communication between resources in your VPC and the internet.
- Does not introduce availability risks or bandwidth bottlenecks.
- Performs Network Address Translation (1:1 NAT) between an instance's private IPv4 and its assigned public IPv4 address.
- A route table pointing `0.0.0.0/0 -> igw-xxxx` makes the associated subnet **Public**.

### 2.5. NAT Gateway (Network Address Translation)
A **NAT Gateway** enables instances in a **private subnet** to connect to services outside your VPC (e.g., downloading OS security patches, updating software packages), while preventing external internet entities from initiating inbound connections to those private instances.
- Must be deployed in a **Public Subnet** and allocated an **Elastic IP (EIP)**.
- Managed, resilient, and automatically scales up to 100 Gbps per gateway.
- Private subnet route tables route `0.0.0.0/0 -> nat-xxxx`.

### 2.6. Security Groups vs. Network ACLs (NACLs)

```
       Internet / Remote Traffic
                   |
                   v
     +---------------------------+
     |   Network ACL (Subnet)    |   <--- First line of defense (Stateless, Subnet level)
     +---------------------------+
                   |
                   v
     +---------------------------+
     |  Security Group (ENI)     |   <--- Second line of defense (Stateful, Instance level)
     +---------------------------+
                   |
                   v
          [ EC2 Instance ]
```

| Feature | Security Group (SG) | Network Access Control List (NACL) |
|---|---|---|
| **Level of Operation** | Instance / Elastic Network Interface (ENI) level | Subnet level |
| **State Nature** | **Stateful**: Return traffic automatically allowed | **Stateless**: Return traffic must be explicitly allowed |
| **Rules Type** | **Allow rules only** (cannot specify Deny) | **Allow and Deny rules** |
| **Rule Processing** | All rules evaluated simultaneously | Evaluated in numerical order (lowest rule number first) |
| **Default Setting** | Inbound all blocked; Outbound all allowed | Inbound and Outbound all allowed (default NACL) |

### 2.7. Public Subnet vs. Private Subnet

```
+-----------------------------------------------------------------------------------------+
| AWS Region (VPC: 10.0.0.0/16)                                                           |
|                                                                                         |
|  +-------------------------------------+      +--------------------------------------+  |
|  | Public Subnet (10.0.1.0/24)         |      | Private Subnet (10.0.2.0/24)         |  |
|  |                                     |      |                                      |  |
|  |   [ Public Web / ALB ]              |      |   [ Backend DB / RDS ]               |  |
|  |   [ NAT Gateway ]                   |      |   (No Public IP, isolated)           |  |
|  |                                     |      |                                      |  |
|  |   Route: 0.0.0.0/0 -> Internet GW   |      |   Route: 0.0.0.0/0 -> NAT Gateway    |  |
|  +-------------------------------------+      +--------------------------------------+  |
|                     |                                              |                    |
+---------------------|----------------------------------------------|--------------------+
                      |                                              |
                      v                                              v
             [ Internet Gateway ]                           [ Outbound Internet Only ]
```

- **Public Subnet**: Subnet whose route table has a route to an Internet Gateway (`0.0.0.0/0 -> igw-xxxx`). Instances can have public IPs and receive direct inbound traffic from the internet.
- **Private Subnet**: Subnet whose route table does NOT route directly to an Internet Gateway. Outbound traffic to the internet passes through a NAT Gateway in a public subnet. Instances have only private IPs.

---

## 3. Common Architecture Patterns

1. **Classic Three-Tier Web Architecture**:
   - *Public Subnets*: Application Load Balancer (ALB) and NAT Gateways.
   - *Private Application Subnets*: EC2 instances or container tasks running application business logic.
   - *Private Database Subnets*: Multi-AZ Amazon RDS PostgreSQL/MySQL clusters isolated from all internet access.
2. **VPC Peering**:
   - Connecting two VPCs directly using private IP addresses with non-overlapping CIDR blocks.
3. **AWS Transit Gateway**:
   - Central hub interconnecting hundreds of VPCs and on-premises corporate data centers via site-to-site VPN or Direct Connect.
