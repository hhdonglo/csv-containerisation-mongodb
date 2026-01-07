# Security Guide

**Author:** Hope Donglo - OpenClassrooms (DataSoluTech)  
**Project:** Healthcare Data Migration Pipeline  
**Date:** January 2026

---

## Table of Contents
- [Security Overview](#security-overview)
- [Authentication](#authentication)
- [Authorization & RBAC](#authorization--rbac)
- [Network Security](#network-security)
- [Data Protection](#data-protection)
- [Audit & Logging](#audit--logging)
- [Compliance Considerations](#compliance-considerations)
- [Security Limitations](#security-limitations)

---

## Security Overview

### Scope & Assumptions

This document outlines the security architecture for the healthcare data migration pipeline, with focus on:
- Healthcare data sensitivity (PHI - Protected Health Information)
- Research-level compliance discussion (HIPAA eligibility)
- Implementation for local and AWS cloud environments

**Assumptions**:
- Data contains sensitive patient information
- HIPAA compliance is a requirement for production
- This is research-level documentation, not production deployment

### Threat Model

**Identified Risks**:
1. Unauthorized data access
2. Data breach during transmission
3. Credential exposure
4. Insider threats
5. Accidental data deletion

**Mitigation Strategy**: Defense in depth with multiple security layers

---

## Authentication

### MongoDB Authentication

**Authentication Method**: SCRAM-SHA-256 (Salted Challenge Response Authentication Mechanism)

**Why SCRAM-SHA-256?**:
- Industry standard for MongoDB
- Prevents password transmission in plain text
- Resistant to eavesdropping attacks
- Challenge-response mechanism

**Enable Authentication**:
```javascript
// Connect to MongoDB
use admin

// Create admin user
db.createUser({
  user: "admin",
  pwd: "SecurePassword123!",
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" },
    { role: "dbAdminAnyDatabase", db: "admin" }
  ]
})
```

**Configuration**:
```yaml
# docker-compose.yml
services:
  mongodb:
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    command: ["mongod", "--auth"]
```

### AWS IAM Authentication (DocumentDB)

**IAM Database Authentication**:
- No password management required
- Temporary credentials (15 minutes)
- Integrated with AWS IAM policies

**Enable IAM Authentication**:
```bash
# Create DocumentDB cluster with IAM auth
aws docdb create-db-cluster \
  --db-cluster-identifier healthcare-cluster \
  --engine docdb \
  --master-username admin \
  --enable-iam-database-authentication
```

**Connect with IAM**:
```python
import boto3
from pymongo import MongoClient

# Generate IAM auth token
client = boto3.client('rds')
token = client.generate_db_auth_token(
    DBHostname='healthcare-cluster.cluster-xxxxx.us-east-1.docdb.amazonaws.com',
    Port=27017,
    DBUsername='iam_user',
    Region='us-east-1'
)

# Connect using token
uri = f"mongodb://iam_user:{token}@healthcare-cluster..."
mongo_client = MongoClient(uri, authSource='$external', authMechanism='MONGODB-AWS')
```

### Secrets Management

**AWS Secrets Manager**:
```bash
# Store credentials
aws secretsmanager create-secret \
  --name healthcare/mongodb/credentials \
  --secret-string '{"username":"admin","password":"SecurePassword123!"}'

# Retrieve credentials
aws secretsmanager get-secret-value \
  --secret-id healthcare/mongodb/credentials
```

**Docker Secrets** (Swarm mode):
```bash
# Create secret
echo "SecurePassword123!" | docker secret create mongo_password -

# Use in docker-compose.yml
services:
  mongodb:
    secrets:
      - mongo_password
    environment:
      MONGO_PASSWORD_FILE: /run/secrets/mongo_password

secrets:
  mongo_password:
    external: true
```

**Environment Variables** (.env file):
```env
# .env (DO NOT COMMIT TO GIT)
MONGO_USERNAME=admin
MONGO_PASSWORD=SecurePassword123!
MONGO_DATABASE=medical_records
MONGO_URI=mongodb://admin:SecurePassword123!@mongodb:27017/medical_records?authSource=admin
```

---

## Authorization & RBAC

### Role-Based Access Control

**Role Hierarchy**:

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Admin** | Full database access | Database administration |
| **ReadWrite** | CRUD operations | Application service |
| **Read** | Query-only access | Analytics, reporting |

### User Creation

**1. Admin User** (Full Access):
```javascript
use admin
db.createUser({
  user: "admin",
  pwd: "AdminPassword123!",
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" },
    { role: "dbAdminAnyDatabase", db: "admin" }
  ]
})
```

**2. Application User** (ReadWrite):
```javascript
use medical_records
db.createUser({
  user: "app_user",
  pwd: "AppPassword123!",
  roles: [
    { role: "readWrite", db: "medical_records" }
  ]
})
```

**3. Analyst User** (Read-Only):
```javascript
use medical_records
db.createUser({
  user: "analyst",
  pwd: "AnalystPassword123!",
  roles: [
    { role: "read", db: "medical_records" }
  ]
})
```

### Custom Roles

**Create Custom Role** (e.g., Migration Service):
```javascript
use admin
db.createRole({
  role: "migrationService",
  privileges: [
    {
      resource: { db: "medical_records", collection: "healthcare_data" },
      actions: ["insert", "update", "createIndex"]
    }
  ],
  roles: []
})

// Assign to user
db.createUser({
  user: "migration_svc",
  pwd: "MigrationPassword123!",
  roles: [{ role: "migrationService", db: "admin" }]
})
```

### Principle of Least Privilege

**Implementation**:
- Application uses `readWrite` role, not `admin`
- Read-only users cannot modify data
- Each service has dedicated credentials
- No shared passwords between environments

---

## Network Security

### Local Environment

**Docker Network Isolation**:
```yaml
# docker-compose.yml
networks:
  healthcare_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.25.0.0/16

services:
  mongodb:
    networks:
      - healthcare_network
    # Only accessible within Docker network
```

**Firewall Rules** (Host machine):
```bash
# Block external access to MongoDB port
sudo ufw deny 27017

# Allow only local connections
sudo ufw allow from 127.0.0.1 to any port 27017
```

### AWS Cloud Environment

**VPC Isolation**:
```yaml
VPC Configuration:
  CIDR: 10.0.0.0/16
  
  Subnets:
    - Private Subnet 1: 10.0.1.0/24 (us-east-1a)
    - Private Subnet 2: 10.0.2.0/24 (us-east-1b)
    - Public Subnet: 10.0.100.0/24 (NAT Gateway only)
  
  Route Tables:
    - Private: No internet gateway route
    - Public: Internet gateway for NAT
```

**Security Groups**:

**1. DocumentDB Security Group**:
```bash
aws ec2 create-security-group \
  --group-name healthcare-docdb-sg \
  --description "DocumentDB security group" \
  --vpc-id vpc-xxxxx

# Allow from ECS tasks only
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 27017 \
  --source-group sg-ecs-tasks
```

**2. ECS Tasks Security Group**:
```bash
aws ec2 create-security-group \
  --group-name healthcare-ecs-sg \
  --description "ECS tasks security group" \
  --vpc-id vpc-xxxxx

# Allow outbound to DocumentDB
aws ec2 authorize-security-group-egress \
  --group-id sg-ecs-tasks \
  --protocol tcp \
  --port 27017 \
  --destination-group sg-docdb
```

**Network Diagram**:
```
┌─────────────────────────────────────────────────────────┐
│                    VPC (10.0.0.0/16)                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Public Subnet (10.0.100.0/24)          │    │
│  │              ┌──────────────┐                  │    │
│  │              │ NAT Gateway  │                  │    │
│  │              └──────┬───────┘                  │    │
│  └─────────────────────┼────────────────────────────┘  │
│                        │                                │
│  ┌─────────────────────┼────────────────────────────┐  │
│  │    Private Subnet 1 (10.0.1.0/24)              │  │
│  │         ┌───────────▼───────────┐              │  │
│  │         │    ECS Tasks          │              │  │
│  │         │  (Migration App)      │              │  │
│  │         └───────────┬───────────┘              │  │
│  └─────────────────────┼────────────────────────────┘  │
│                        │                                │
│  ┌─────────────────────┼────────────────────────────┐  │
│  │    Private Subnet 2 (10.0.2.0/24)              │  │
│  │         ┌───────────▼───────────┐              │  │
│  │         │   DocumentDB          │              │  │
│  │         │   (No public access)  │              │  │
│  │         └───────────────────────┘              │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### TLS/SSL Encryption

**Enable TLS in MongoDB**:
```bash
# Generate self-signed certificate (development only)
openssl req -newkey rsa:2048 -new -x509 -days 365 -nodes \
  -out mongodb-cert.crt -keyout mongodb-cert.key

# Combine certificate and key
cat mongodb-cert.key mongodb-cert.crt > mongodb.pem

# Start MongoDB with TLS
mongod --tlsMode requireTLS \
       --tlsCertificateKeyFile /etc/ssl/mongodb.pem
```

**Connect with TLS**:
```python
from pymongo import MongoClient

client = MongoClient(
    'mongodb://localhost:27017',
    tls=True,
    tlsCAFile='/path/to/ca.pem'
)
```

**DocumentDB TLS** (Always enabled):
```python
client = MongoClient(
    'mongodb://healthcare-cluster.cluster-xxxxx.us-east-1.docdb.amazonaws.com:27017',
    tls=True,
    tlsCAFile='rds-combined-ca-bundle.pem',
    replicaSet='rs0',
    readPreference='secondaryPreferred'
)
```

---

## Data Protection

### Encryption at Rest

**Local Environment** (LUKS encryption):
```bash
# Encrypt Docker volume
sudo cryptsetup luksFormat /dev/sdb1
sudo cryptsetup luksOpen /dev/sdb1 mongodb_data
sudo mkfs.ext4 /dev/mapper/mongodb_data
sudo mount /dev/mapper/mongodb_data /var/lib/docker/volumes/mongodb_data
```

**AWS DocumentDB**:
```bash
# Create encrypted cluster
aws docdb create-db-cluster \
  --db-cluster-identifier healthcare-cluster \
  --engine docdb \
  --master-username admin \
  --master-user-password SecurePassword123! \
  --storage-encrypted \
  --kms-key-id arn:aws:kms:us-east-1:123456789:key/xxxxx
```

**AWS KMS Key Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Allow DocumentDB to use key",
      "Effect": "Allow",
      "Principal": {
        "Service": "rds.amazonaws.com"
      },
      "Action": [
        "kms:Decrypt",
        "kms:GenerateDataKey"
      ],
      "Resource": "*"
    }
  ]
}
```

### Encryption in Transit

**All Connections Use TLS**:
- MongoDB connections: TLS 1.2+
- Application connections: HTTPS
- AWS service connections: SSL/TLS by default

### Data Masking (for non-production)

**Anonymize PHI for testing**:
```python
import hashlib

def mask_patient_name(name):
    """Hash patient names for test environments"""
    return hashlib.sha256(name.encode()).hexdigest()[:10]

def mask_sensitive_fields(df):
    """Mask sensitive fields in DataFrame"""
    df['patient_name'] = df['patient_name'].apply(mask_patient_name)
    df['ssn'] = '***-**-****'  # Completely mask SSN
    return df
```

### Backup Encryption

**Encrypt backups with GPG**:
```bash
# Create backup and encrypt
mongodump --uri="mongodb://localhost:27017" \
  --db=medical_records \
  --archive | gpg --encrypt --recipient ops@datasolutech.com > backup.gz.gpg

# Decrypt and restore
gpg --decrypt backup.gz.gpg | mongorestore --archive
```

**S3 Server-Side Encryption**:
```bash
# Upload with encryption
aws s3 cp backup.gz s3://healthcare-backups/ \
  --server-side-encryption aws:kms \
  --ssekms-key-id arn:aws:kms:us-east-1:123456789:key/xxxxx
```

---

## Audit & Logging

### MongoDB Audit Logging

**Enable Audit Log** (Enterprise Edition):
```yaml
# mongod.conf
auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.json
  filter: '{ "atype": { "$in": [ "authenticate", "createUser", "dropUser", "dropDatabase" ] } }'
```

**Audit Events Logged**:
- Authentication attempts (success/failure)
- User creation/deletion
- Role modifications
- Database drops
- Collection drops

### AWS CloudTrail

**Enable CloudTrail for AWS API calls**:
```bash
aws cloudtrail create-trail \
  --name healthcare-audit-trail \
  --s3-bucket-name healthcare-cloudtrail-logs \
  --is-multi-region-trail

aws cloudtrail start-logging \
  --name healthcare-audit-trail
```

**Events Logged**:
- DocumentDB cluster modifications
- Security group changes
- IAM policy modifications
- Secrets Manager access
- KMS key usage

### Application Logging

**Structured Logging** (Python):
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'user': getattr(record, 'user', 'system'),
            'action': getattr(record, 'action', 'unknown'),
            'message': record.getMessage()
        }
        return json.dumps(log_data)

# Configure logger
handler = logging.FileHandler('/var/log/healthcare-migration/audit.log')
handler.setFormatter(JSONFormatter())
logger = logging.getLogger('healthcare_audit')
logger.addHandler(handler)

# Log actions
logger.info('Data migration started', extra={'user': 'migration_svc', 'action': 'migrate_start'})
```

### Log Retention

**Retention Policy**:
```yaml
Log Types:
  Application Logs: 90 days
  Audit Logs: 7 years (HIPAA requirement)
  System Logs: 30 days
  CloudTrail: 1 year (compliance)
```

**S3 Lifecycle Policy**:
```json
{
  "Rules": [
    {
      "Id": "Move-audit-logs-to-Glacier",
      "Status": "Enabled",
      "Prefix": "audit/",
      "Transitions": [
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 2555
      }
    }
  ]
}
```

---

## Compliance Considerations

### HIPAA Eligibility

**AWS HIPAA Compliance**:
- DocumentDB is HIPAA eligible
- Must sign AWS Business Associate Agreement (BAA)
- Encryption required (at rest and in transit)
- Access logging required

**HIPAA Requirements Mapping**:

| Requirement | Implementation |
|-------------|----------------|
| **Access Control** | IAM + MongoDB RBAC |
| **Audit Controls** | CloudTrail + MongoDB audit logs |
| **Integrity Controls** | Checksums + data validation |
| **Transmission Security** | TLS 1.2+ for all connections |

### Data Retention

**HIPAA Requirement**: Retain records for 6 years

**Implementation**:
```yaml
Retention Policy:
  Active Database: Current patient data
  Archive (S3 Glacier): Data > 1 year old
  Deletion: After 7 years (6 years + 1 year buffer)
```

### Access Controls

**Physical Controls**:
- AWS data center security (physical access)
- Hardware encryption modules

**Technical Controls**:
- Multi-factor authentication (MFA)
- Principle of least privilege
- Regular access reviews

**Administrative Controls**:
- Security awareness training
- Incident response procedures
- Disaster recovery plan

### Breach Notification

**Incident Response Plan**:
1. Detect: Automated monitoring and alerts
2. Contain: Isolate affected systems
3. Investigate: Determine scope and impact
4. Notify: Within 60 days (HIPAA requirement)
5. Remediate: Fix vulnerabilities
6. Document: Maintain incident records

---

## Security Limitations

### Current Implementation Gaps

**What is NOT implemented**:
1. **Production TLS certificates**: Using self-signed certificates
2. **Multi-factor authentication**: Not configured for MongoDB
3. **Data loss prevention (DLP)**: No automated PHI detection
4. **Intrusion detection**: No IDS/IPS deployed
5. **Penetration testing**: Not performed
6. **Formal risk assessment**: Not conducted

### Recommended Next Steps

**For Production Deployment**:

1. **Obtain Valid TLS Certificates**
   - Use Let's Encrypt or commercial CA
   - Automate certificate renewal

2. **Implement MFA**
   - AWS IAM MFA for console access
   - Application-level MFA for sensitive operations

3. **Deploy Monitoring Tools**
   - AWS GuardDuty for threat detection
   - AWS Security Hub for compliance monitoring
   - Implement SIEM (e.g., Splunk, ELK stack)

4. **Conduct Security Assessments**
   - Penetration testing (annual)
   - Vulnerability scanning (monthly)
   - Code security review

5. **Establish Security Policies**
   - Password policy (complexity, rotation)
   - Access review process (quarterly)
   - Incident response procedures
   - Data classification policy

6. **Employee Training**
   - HIPAA awareness training (annual)
   - Security best practices
   - Phishing awareness

---

## Security Checklist

### Pre-Deployment Checklist

- [ ] All default passwords changed
- [ ] MongoDB authentication enabled
- [ ] TLS/SSL configured for all connections
- [ ] Firewall rules configured
- [ ] Backup encryption enabled
- [ ] Audit logging enabled
- [ ] IAM roles configured (principle of least privilege)
- [ ] Security groups properly configured
- [ ] Secrets stored in Secrets Manager
- [ ] CloudTrail enabled
- [ ] MFA enabled for privileged accounts
- [ ] Data retention policy documented
- [ ] Incident response plan documented
- [ ] BAA signed with AWS (for HIPAA)
- [ ] Security testing completed

### Ongoing Security Tasks

**Daily**:
- [ ] Review security alerts
- [ ] Monitor unusual access patterns

**Weekly**:
- [ ] Review access logs
- [ ] Check backup integrity

**Monthly**:
- [ ] Vulnerability scanning
- [ ] Access review
- [ ] Update security patches

**Quarterly**:
- [ ] Access audit
- [ ] Policy review
- [ ] Security training

**Annually**:
- [ ] Penetration testing
- [ ] Compliance audit
- [ ] Disaster recovery drill
- [ ] Risk assessment update

---

## Security Contact

**Security Issues**: Report to security@datasolutech.com  
**Escalation**: On-call security engineer (24/7)  
**Documentation**: Security policies at https://datasolutech.com/security

---

*This security guide is maintained as part of the Healthcare Data Migration Pipeline project. Last updated: January 2026*