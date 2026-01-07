# AWS Cloud Architecture & Deployment Research

**Author:** Hope Donglo - OpenClassrooms (DataSoluTech)  
**Project:** Healthcare Data Migration Pipeline  
**Date:** January 2026

---

## Table of Contents
- [Research Overview](#research-overview)
- [Understanding Servers](#understanding-servers)
- [AWS Services Overview](#aws-services-overview)
- [MongoDB Deployment Options](#mongodb-deployment-options)
- [AWS Account Setup](#aws-account-setup)
- [Pricing Models & Cost Analysis](#pricing-models--cost-analysis)
- [Benefits of Cloud Migration](#benefits-of-cloud-migration)
- [Recommendations](#recommendations)

---

## Research Overview

**Client Challenge**: Healthcare provider experiencing scalability issues with daily patient record management using traditional relational database. They need a horizontally scalable Big Data solution with minimal IT overhead.

**Research Objectives**:
- Explore MongoDB deployment options on AWS
- Compare AWS services (S3, DocumentDB, ECS)
- Analyze pricing models and cost optimization
- Evaluate cloud migration benefits
- Provide actionable recommendations

**Scope**: Exploratory research to inform client decision-making.

---


## Understanding Servers

### Server Types Comparison

| Type | Description | Advantages | Disadvantages | Cost Model |
|------|-------------|------------|---------------|------------|
| **Physical** | Owned hardware in data center | Maximum performance, complete control | High upfront cost ($5k-$50k), long provisioning, fixed capacity | Capital expense |
| **Virtual (EC2)** | Software-defined on shared hardware | Instant provisioning, easy scaling, no hardware maintenance | Shared resources, internet dependency | Pay-as-you-go |
| **Managed (DocumentDB)** | Fully managed by provider | Zero server management, automatic scaling, built-in HA | Less control, vendor lock-in | Monthly subscription |
| **Serverless (Lambda)** | No infrastructure visible | Zero management, pay per execution | Execution limits, cold starts | Per-invocation |

**Key Takeaway**: For the client's needs (scalability, minimal IT staff, healthcare compliance), managed or virtual servers are most appropriate. Physical servers contradict the scalability requirement.

---

## AWS Services Overview

This section provides high-level introductions to AWS services evaluated for the project. Detailed comparisons appear in [MongoDB Deployment Options](#mongodb-deployment-options).

### Amazon S3 (Simple Storage Service)

**Purpose**: Scalable object storage for any data type.

**Key Capabilities**:
- Unlimited storage capacity with automatic scaling
- 99.999999999% durability (data replicated across facilities)
- Multiple storage tiers: Standard ($0.023/GB), Glacier ($0.004/GB)
- Lifecycle policies for automatic archiving

**Healthcare Use Cases**:
- Store raw CSV files and processed datasets
- Automated database backups
- Long-term archival for compliance (7-year retention)

---

### Amazon DocumentDB

**What It Is**: AWS-managed document database compatible with MongoDB 3.6, 4.0, and 5.0 APIs.

**Core Features**:
- MongoDB driver compatibility (works with pymongo)
- Automatic scaling 
- **Multi-AZ high availability (6 copies across 3 zones)**
- **HIPAA-eligible with built-in encryption**
- Automated backups with point-in-time recovery

**Trade-offs**:
- API-compatible, not full native MongoDB (some features unsupported)
- Higher cost than self-managed (~$200/month  vs ~$150/month)
- Limited configuration compared to self-hosting

Detailed advantages/disadvantages in [Option 1](#option-1-amazon-documentdb-recommended) below.

---

### Amazon ECS (Elastic Container Service)

**What It Is**: Managed container orchestration for Docker workloads.

**Two Launch Types**:

| Feature | Fargate (Serverless) | EC2 (Self-Managed) |
|---------|---------------------|-------------------|
| Management | Fully managed | Manage instances |
| Cost | Higher per hour | Lower for sustained use |
| Scaling | Automatic | Manual |
| Best For | Variable workloads | Predictable workloads |

**Integration Benefits**:
- Runs existing Docker containers without modification
- ECR for container image storage
- EFS for persistent MongoDB data
- CloudWatch for centralized logging

Detailed comparison in [Option 4](#option-4-containerized-mongodb-on-ecs) below.

---

### RDS for MongoDB - Clarification

**Important**: AWS does not offer "RDS for MongoDB."

Amazon RDS only supports relational databases (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, Aurora). For MongoDB on AWS, use:
- Amazon DocumentDB (managed, MongoDB-compatible)
- MongoDB Atlas (third-party on AWS infrastructure)
- Self-managed on EC2 or ECS

---

## MongoDB Deployment Options

Comprehensive comparison of all deployment approaches, with detailed advantages and disadvantages.

---

### Option 1: Amazon DocumentDB (Recommended)

**Type**: Fully managed database service  
**Server Management**: AWS handles everything

#### Advantages

**Operational**:
- Zero database administration (no patching, backups, scaling decisions)
- 24/7 AWS monitoring and management included
- Automatic failover in <30 seconds

**Scalability**:
- Storage auto-scales to 128TB without intervention
- Add up to 15 read replicas for horizontal scaling
- Vertical scaling (instance resize) with minimal downtime

**Reliability**:
- 99.99% uptime SLA
- 6 copies of data across 3 Availability Zones
- Continuous backups to S3 with point-in-time recovery (1-35 days)
- Cross-region backup copies for disaster recovery

**Security & Compliance**:
- HIPAA-eligible out-of-the-box
- Automatic encryption at rest (KMS) and in transit (TLS)
- VPC network isolation
- IAM database authentication
- Audit logging built-in

**Cost Predictability**:
- Fixed monthly pricing (~$200/month production)
- No hidden operational costs
- Reserved Instances: 75% savings with 3-year commitment

#### Disadvantages

**Compatibility**:
- API-compatible, not native MongoDB (some features missing: full-text search, graph processing)
- Potential minor code adjustments required
- Cannot use all MongoDB tools

**Control**:
- Limited server-level configuration
- Cannot access underlying infrastructure
- AWS-controlled maintenance windows

**Cost**:
- Premium pricing compared to self-managed
- Ongoing monthly expense (vs one-time hardware purchase)

**Best For**: Production workloads requiring HIPAA compliance, high availability, and minimal operational overhead.

---

### Option 2: MongoDB Atlas on AWS

**Type**: Third-party managed service by MongoDB Inc.  
**Server Management**: MongoDB Inc. handles everything

#### Advantages

- **Native MongoDB**: 100% feature compatibility, latest versions immediately available
- **Multi-Cloud**: Easy migration between AWS, Azure, GCP
- **Expert Support**: Managed by MongoDB creators
- **Advanced Features**: Full-text search, graph, time-series, change streams

#### Disadvantages

- **Cost**: ~$300-400/month (2x DocumentDB)
- **Integration**: Less seamless with AWS services
- **Complexity**: Separate billing and management from AWS
- **Overhead**: Two vendor relationships (AWS + MongoDB)

**Best For**: Applications requiring full MongoDB features or multi-cloud strategy.

---

### Option 3: Self-Managed MongoDB on EC2

**Type**: Manual installation on virtual servers  
**Server Management**: Your team manages everything

#### Advantages

- **Complete Control**: Root access, any configuration, all MongoDB features
- **Lower Base Cost**: ~$100-150/month compute (before operational costs)
- **Flexibility**: Choose instance types, customize everything
- **No Lock-in**: Standard MongoDB, easy to migrate

#### Disadvantages

- **High Operational Burden**:
  - Manual backups, updates, security patches
  - Configure high availability yourself
  - 24/7 monitoring required
  - Requires database administration expertise
  
- **Hidden Costs**:
  - Staff time for management (significant salary cost)
  - Monitoring tool licenses
  - Risk of downtime

- **Scalability Complexity**:
  - Manual sharding configuration
  - Capacity planning required
  - Scaling causes downtime without careful planning

**Best For**: Organizations with experienced MongoDB DBAs and need for specific configurations.

---

### Option 4: Containerized MongoDB on ECS

**Type**: Docker containers on AWS infrastructure  
**Server Management**: Semi-managed (AWS handles containers, you handle database)

#### Advantages

- **Docker Compatibility**: Our existing setup works unchanged
- **Development Parity**: Identical local and cloud environments
- **Modern Architecture**: Microservices-ready, easy CI/CD
- **Cost Flexibility**: Fargate ($20/month occasional) or EC2 ($150/month sustained)

#### Disadvantages

- **Database Anti-Pattern**: Containers designed for stateless apps, not databases
- **Complexity**: Requires container orchestration knowledge
- **Manual Management**: Backups, replication, monitoring all manual
- **Storage Overhead**: EFS costs $0.30/GB-month for persistence

**Best For**: Development/testing only. Not recommended for production databases.

---

### Option 5: Physical Servers (On-Premises)

**Type**: Owned hardware  
**Server Management**: Complete responsibility

#### Advantages

- One-time capital expense
- Maximum control
- Data stays on-premises

#### Disadvantages

- **Contradicts Client Need**: Fixed capacity vs scalability requirement
- **Massive Upfront Investment**: $50k-$200k initial cost
- **Operational Complexity**: Requires full IT infrastructure team
- **Hidden Costs**: Electricity, cooling, space rental, hardware refresh (3-5 years)
- **Single Point of Failure**: No geographic redundancy without additional cost

**Not Recommended**: Client's scalability issues require cloud flexibility.

---

### Deployment Decision Matrix

| Option | Monthly Cost | Management | Scalability | HIPAA Ready | Recommended For |
|--------|-------------|------------|-------------|-------------|-----------------|
| **DocumentDB** | ~$200 | Fully managed | Automatic | Yes | **Production** |
| **MongoDB Atlas** | ~$400 | Fully managed | Automatic | Configurable | Full MongoDB features |
| **EC2 Self-Managed** | ~$150* | Manual | Manual | DIY | MongoDB expertise |
| **ECS Containers** | ~$20-150 | Semi-managed | Semi-auto | DIY | Development only |
| **Physical** | High upfront | Complete | Very difficult | DIY | Not applicable |

*Plus significant operational costs

### Selection Criteria

**Choose DocumentDB if**:
- Need HIPAA compliance immediately
- Limited IT infrastructure staff
- Require 99.99% uptime
- Want predictable monthly costs

**Choose MongoDB Atlas if**:
- Require full MongoDB feature set
- Planning multi-cloud strategy
- Budget allows premium pricing

**Choose Self-Managed EC2 if**:
- Have experienced MongoDB DBAs
- Need specific customizations
- Willing to invest in operational overhead

**Choose ECS if**:
- Development/testing only
- Not for production databases

---

## AWS Account Setup

### Account Creation (5 Steps)

**Step 1: Registration**
1. Navigate to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create an AWS Account"
3. Enter email address
4. Choose account name (e.g., "DataSoluTech-Healthcare")
5. Set root user password

**Step 2: Contact Information**
1. Select account type:
   - **Business**: For company use (recommended)
   - **Personal**: For individual use
2. Enter company/personal details
3. Provide valid phone number
4. Enter billing address

**Step 3: Payment Information**
1. Enter credit/debit card details
2. Card charged $1 for verification (refunded)
3. Required even for Free Tier usage

**Step 4: Identity Verification**
1. Choose verification method:
   - SMS text message (faster)
   - Voice call
2. Enter verification code received
3. Complete verification

**Step 5: Support Plan Selection**

| Plan | Cost | Support Level | Response Time |
|------|------|---------------|---------------|
| **Basic** | Free | Forums, documentation | Community-driven |
| **Developer** | $29/month | Business hours email | <24 hours |
| **Business** | $100/month | 24/7 phone/email | <1 hour |
| **Enterprise** | $15,000/month | Dedicated TAM | <15 minutes |


**Account Activation**:
- Wait for account activation (minutes to 24 hours)
- Receive confirmation email
- Sign in to AWS Management Console

### Free Tier Benefits

**12-Month Free Tier** (starts from signup date):

**Compute**:
- 750 hours/month EC2 t2.micro instances
- 750 hours/month ECS Fargate (2 vCPU, 4GB RAM)

**Storage**:
- 5GB S3 Standard storage
- 30GB EBS storage

**Database**:
- 750 hours/month RDS db.t2.micro
- 25GB DocumentDB storage (30-day trial)

**Monitoring**:
- 10 CloudWatch metrics
- 10 alarms

**Data Transfer**:
- 15GB outbound data transfer/month

**Always Free** (no expiration):
- 1 million Lambda requests/month
- 25GB DynamoDB storage

### Post-Account Setup Security

**Critical Security Steps** (do immediately):

**1. Enable MFA on Root Account**
```
IAM Console → Root user → Security credentials → 
Activate MFA → Use authenticator app (Google Authenticator, Authy)
```

**2. Create IAM Admin User**
```Do not use root account for daily operations
Create IAM user with admin permissions
Use IAM user for all work
```

**3. Set Up Billing Alerts**
```
Billing Console → Budgets → Create budget
Set threshold: $50/month warning
Alert via email
```

**4. Enable CloudTrail**
```
CloudTrail Console → Create trail
Log all API calls for audit
Store logs in S3
```

**5. Configure Budget Alarms**
```
Set up multiple thresholds:
- $25 (50% of budget) - warning
- $50 (100% of budget) - critical
- $75 (150% of budget) - emergency stop
```

---

## Pricing Models & Cost Analysis

### AWS Pricing Models

| Model | Commitment | Discount | Best For |
|-------|-----------|----------|----------|
| **On-Demand** | None | 0% | Testing, unpredictable workloads |
| **Reserved (1-year)** | 1 year | ~40% | Production with some flexibility |
| **Reserved (3-year)** | 3 years | ~75% | Stable production workloads |
| **Savings Plans** | 1-3 years | ~66% | Flexible across services |
| **Spot Instances** | None | ~90% | Interruptible workloads only |

### Core Pricing Philosophy

AWS uses **pay-as-you-go** pricing with no upfront commitments (for most services).

**Key Principles**:
- Pay only for what you use
- No upfront costs (except Reserved Instances)
- No long-term contracts required
- Stop anytime
- Scale up/down as needed

### AWS Cost Management Tools

**AWS Pricing Calculator**: [calculator.aws](https://calculator.aws)
- Estimate costs before deployment
- Compare different configurations
- Export estimates to PDF/CSV

**AWS Cost Explorer**:
- Visualize last 13 months of spending
- Forecast next 3 months
- Filter by service, region, tags
- Identify cost anomalies

**AWS Budgets**:
- Set custom spending limits
- Alert when exceeding thresholds
- Track Reserved Instance utilization

### Project Cost Analysis

#### Development Environment

| Service | Configuration | Cost |
|---------|--------------|------|
| ECS Fargate | Occasional migration tasks | $20 |
| S3 | 10GB data | $0.50 |
| CloudWatch | Basic logging | $2 |
| **Total Development** | | **$23/month** |

#### Production Environment

| Service | Configuration | Cost |
|---------|--------------|------|
| DocumentDB | db.r5.large (2 vCPU, 16GB RAM) | $202 |
| DocumentDB Storage | 100GB | $10 |
| S3 | 100GB Standard + 500GB Glacier | $5 |
| ECS Fargate | Migration tasks | $20 |
| CloudWatch | Detailed monitoring | $5 |
| Data Transfer | 50GB outbound | $5 |
| **Total Production (On-Demand)** | | **$247/month** |
| **With 3-Year Reserved** | | **$62/month** |

### 3-Year Total Cost of Ownership

**AWS (with Reserved Instances)**:
- Year 1: $247 × 12 = $2,964
- Year 2-3: $62 × 24 = $1,488
- **Total: $4,452**

**On-Premises Equivalent**:
- Hardware: $30,000
- Staff (DBA): $60k/year × 3 = $180,000
- Infrastructure: $7,200
- **Total: $217,200**

**AWS Savings: $212,748 (98%)** when accounting for dedicated database administration and infrastructure overhead required for on-premises deployment.

> **Note**: This comparison includes operational costs (database administrator salary, infrastructure management) which represent the largest cost differential between cloud and on-premises deployments. Hardware costs alone would show ~85% savings.

### Cost Optimization Strategies

**1. Right-Sizing**
- Start with smaller instances
- Monitor actual usage
- Scale up only when needed

**2. Reserved Instances (Production)**
- 3-year commitment for DocumentDB
- Save 75% ($247 → $62/month)
- ROI break-even: 4 months

**3. Storage Lifecycle**
- Move old data to S3 Glacier (82% cheaper)
- Delete temporary files automatically
- Compress backups

**4. Development Optimization**
- Stop dev resources when not in use
- Use Spot instances for testing
- Schedule automatic shutdown (nights/weekends)
- Potential savings: 70%

**5. Data Transfer Reduction**
- Keep data in same region
- Use CloudFront CDN for static files
- Compress data transfers

---

## Benefits of Cloud Migration

### Business Impact

| Client Problem | AWS Solution | Measurable Benefit |
|----------------|--------------|-------------------|
| Scalability bottleneck | Auto-scaling storage/compute | Unlimited growth capacity |
| System downtime | Multi-AZ deployment | 99.99% uptime (8.76 hrs/year max) |
| Data loss risk | Automated backups + PITR | Recovery to any second |
| High infrastructure costs | Pay-as-you-go pricing | 98% cost reduction |
| Limited IT staff | Fully managed services | Zero DBA requirement |
| Compliance burden | HIPAA-eligible services | Built-in compliance |

### Technical Advantages

**Performance**:
- SSD storage (faster than traditional drives)
- Read replicas for query distribution
- Global edge locations (low latency)

**Innovation**:
- AI/ML integration (SageMaker)
- Analytics (Athena, QuickSight)
- Serverless functions (Lambda)

**Reliability**:
- Self-healing infrastructure
- Automated failover
- Proven at Netflix/Airbnb scale

**Scalability**:
- Horizontal scaling (add more resources)
- Vertical scaling (bigger resources)
- Auto-scaling based on demand
- Global distribution

---

## Recommendations

### Primary: Amazon DocumentDB

**Justification** (referencing prior analysis):

1. **Addresses Core Need**: Client's scalability issues require automatic scaling → DocumentDB provides storage auto-scaling (10GB to 128TB) and compute scaling without manual intervention (see [Option 1](#option-1-amazon-documentdb-recommended))

2. **Minimal Migration Effort**: MongoDB API compatibility means our existing pymongo-based code works with minor adjustments, reducing migration risk and timeline

3. **Healthcare Compliance**: HIPAA-eligible out-of-the-box with built-in encryption, audit logging, and compliance documentation (critical for medical records)

4. **Operational Fit**: Client lacks dedicated IT infrastructure staff → fully managed service eliminates need for database administrators

5. **Cost-Effective**: $247/month initially, reduces to $62/month with 3-year Reserved Instances after validation period (see [Cost Analysis](#project-cost-analysis))

**Why Other Options Were Rejected**:

- **MongoDB Atlas**: Eliminated due to 2x higher cost ($400/month) without sufficient additional value for this use case
- **Self-Managed EC2**: Rejected due to client's limited database administration capacity and operational complexity
- **ECS Containers**: Suitable only for development/testing, not production databases (stateful workload anti-pattern)
- **Physical Servers**: Fundamentally contradicts client's scalability requirements and requires massive upfront investment

### Deployment Roadmap

**Phase 1: Proof of Concept (Month 1)** - $50
- Deploy minimal DocumentDB instance (db.t3.medium)
- Migrate 1,000 sample records
- Validate compatibility and performance

**Phase 2: Development (Month 2)** - $100/month
- Full development cluster
- Complete dataset migration (54,966 records)
- Integration testing

**Phase 3: Production (Month 3)** - $247/month
- Scale to db.r5.large
- Enable Multi-AZ deployment
- Configure 7-day automated backups
- Implement disaster recovery

**Phase 4: Optimization (Month 4+)** - $62/month
- Purchase 3-year Reserved Instances (75% savings)
- Implement S3 Lifecycle policies
- Right-size based on actual usage

### Alternative: Hybrid Approach

For cost-sensitive scenarios:
- **Development**: ECS + MongoDB containers ($20/month)
- **Production**: DocumentDB ($200/month)
- **Total**: $220/month (12% savings vs all-DocumentDB)

This approach maintains development environment parity while ensuring production reliability.

---

**Final Recommendation**: Proceed with Amazon DocumentDB using the phased deployment roadmap. This solution directly addresses the client's scalability challenges while providing HIPAA compliance, high availability, and minimal operational burden. The 3-4 month timeline allows thorough validation before full production commitment, and Reserved Instances provide long-term cost optimization once workload patterns are confirmed.

---

## Implementation Checklist

### Migration Steps

**1. Preparation**
- Export current data (complete)
- Upload to S3 bucket
- Create backup

**2. Infrastructure**
- Create VPC and security groups
- Launch DocumentDB cluster
- Configure monitoring

**3. Migration**
- Run Python migration script
- Validate data integrity
- Performance testing

**4. Cutover**
- Schedule maintenance window
- Update connection strings
- Monitor for 48 hours

### Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Compatibility issues | Thorough Phase 1 testing, maintain fallback |
| Team unfamiliarity | AWS training, comprehensive documentation |
| Cost overruns | Budget alerts at $25/$50/$75 thresholds |
| Data breach | Encryption everywhere, VPN, audit logging |

---

## Research Conclusion

**Status**: Comprehensive evaluation complete  
**Date**: January 2026  
**Primary Recommendation**: Amazon DocumentDB with phased deployment  
**Total Investment**: $247/month production (reduces to $62/month with Reserved Instances)

### Key Findings Summary

- DocumentDB addresses all client requirements: scalability, HIPAA compliance, minimal operational overhead
- 98% cost reduction vs on-premises when including staff costs
- Migration achievable in 3-4 months with minimal risk
- Phased approach allows validation before full commitment

### Additional Resources

**AWS Documentation**:
- [DocumentDB Documentation](https://docs.aws.amazon.com/documentdb/)
- [ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [S3 Documentation](https://docs.aws.amazon.com/s3/)

**AWS Tools**:
- [Pricing Calculator](https://calculator.aws)
- [Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Training and Certification](https://aws.amazon.com/training/)

**Support Channels**:
- AWS Support (if subscribed)
- AWS Forums
- Stack Overflow (aws tag)
- AWS re:Post community

---

**Prepared by**: Hope Donglo, Data Engineer Intern  
**Company**: DataSoluTech  
**Program**: OpenClassrooms Data Engineering - Project 5

---

*This research was conducted to explore cloud deployment options for healthcare data migration without actual implementation. All recommendations are based on client requirements analysis and AWS service capabilities.*