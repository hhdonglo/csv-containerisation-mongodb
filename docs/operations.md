# Operations Guide

**Author:** Hope Donglo - OpenClassrooms (DataSoluTech)  
**Project:** Healthcare Data Migration Pipeline  
**Date:** January 2026

[![English](https://img.shields.io/badge/📖_Documentation-English-blue?style=for-the-badge)](operations.md)
[![Français](https://img.shields.io/badge/📖_Documentation-Français-red?style=for-the-badge)](operations.fr.md)

---

## Container Reference

For quick reference, here are the container names used throughout this guide:

| Service | Container Name | Purpose |
|---------|---------------|---------|
| MongoDB Database | `healthcare_mongodb` | Primary database storage |
| Migration App | `healthcare_migration` | ETL pipeline execution |
| Mongo Express UI | `healthcare_mongo_ui` | Web-based database management |

---

## Table of Contents
- [Pipeline Operations](#pipeline-operations)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Backup Strategies](#backup-strategies)
- [Disaster Recovery](#disaster-recovery)
- [Testing Procedures](#testing-procedures)
- [Troubleshooting](#troubleshooting)

---

## Pipeline Operations

### Running the Pipeline

#### Docker Deployment

**Start Services**:
```bash
# Start all services
docker-compose up -d

# View logs for specific container
docker-compose logs -f healthcare_migration

# View logs for MongoDB
docker-compose logs -f healthcare_mongodb

# View logs for Mongo Express UI
docker-compose logs -f healthcare_mongo_ui

# Check service status
docker-compose ps
```

**Stop Services**:
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

**Restart Services**:
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart healthcare_mongodb
```

#### Local Development

**Run Pipeline**:
```bash
# Activate virtual environment
poetry shell

# Run main pipeline
python -m csv_containerisation_mongodb.main.main
```

**Environment Variables**:
```bash
export MONGO_URI="mongodb://localhost:27017"
export MONGO_DATABASE="medical_records"
export LOG_LEVEL="DEBUG"
```

### Pipeline Workflow

**7-Step Execution**:

1. **Data Loading** - Loads CSV from `data/raw/`
2. **Data Cleaning** - Standardizes names, removes duplicates, optimizes types
3. **MongoDB Connection** - Establishes and validates connection
4. **Load Cleaned Data** - Loads processed CSV
5. **Data Migration** - Bulk insertion with nested documents
6. **Integrity Verification** - Validates count, fields, types, missing values
7. **Completion** - Generates reports and logs

### Output Files
```
data/processed/
├── cleaned_healthcare.csv           # Cleaned data (54,966 records)
├── healthcare_cleaning_report.md    # Detailed cleaning report
└── healthcare_quality_report.csv    # Quality metrics
```

---

## Monitoring and Alerting

### Local Monitoring

#### Docker Container Monitoring

**View Container Stats**:
```bash
# Real-time resource usage for all containers
docker stats

# Specific container stats
docker stats healthcare_mongodb
docker stats healthcare_migration
docker stats healthcare_mongo_ui

# Container logs with tail
docker logs healthcare_mongodb --tail 100 -f
docker logs healthcare_migration --tail 100 -f
```

**Health Checks**:
```bash
# Check MongoDB health
docker exec healthcare_mongodb mongosh --eval "db.runCommand('ping')"

# Check MongoDB connection from migration container
docker exec healthcare_migration python -c "from pymongo import MongoClient; client = MongoClient('mongodb://mongodb:27017'); print(client.server_info())"
```

#### Application Logging

**View Logs**:
```bash
# Tail application logs
tail -f /var/log/healthcare-migration/pipeline.log

# Search for errors
grep ERROR /var/log/healthcare-migration/*.log

# View last 100 lines
tail -n 100 /var/log/healthcare-migration/pipeline.log
```

### Cloud Monitoring Options

For AWS cloud monitoring strategies (CloudWatch, metrics, alarms), see [AWS Architecture Guide](aws-architecture.md).

---

## Backup Strategies

### Local Backups

#### MongoDB Backup (mongodump)

**Manual Backup**:
```bash
# Compressed backup
docker exec healthcare_mongodb mongodump \
  --uri="mongodb://localhost:27017" \
  --db=medical_records \
  --gzip \
  --archive=/tmp/backup_$(date +%Y%m%d).gz

# Copy backup from container to host
docker cp healthcare_mongodb:/tmp/backup_$(date +%Y%m%d).gz ./backups/
```

**Automated Backup Script**:
```bash
#!/bin/bash
BACKUP_DIR="/backups/mongodb"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

# Create backup inside container
docker exec healthcare_mongodb mongodump \
  --uri="mongodb://localhost:27017" \
  --db=medical_records \
  --gzip \
  --archive=/tmp/backup_${TIMESTAMP}.gz

# Copy backup from container to host
docker cp healthcare_mongodb:/tmp/backup_${TIMESTAMP}.gz ${BACKUP_DIR}/

# Delete old backups
find ${BACKUP_DIR} -name "backup_*.gz" -mtime +${RETENTION_DAYS} -delete

# Log completion
echo "[$(date)] Backup completed: backup_${TIMESTAMP}.gz" >> /var/log/mongodb-backup.log
```

**Schedule with Cron**:
```bash
# Daily at 2 AM
0 2 * * * /usr/local/bin/mongodb-backup.sh
```

#### Restore from Backup
```bash
# Copy backup to container
docker cp ./backups/backup_20260107.gz healthcare_mongodb:/tmp/

# Restore from compressed backup
docker exec healthcare_mongodb mongorestore \
  --uri="mongodb://localhost:27017" \
  --db=medical_records \
  --gzip \
  --archive=/tmp/backup_20260107.gz
```

### Backup Best Practices

**3-2-1 Rule**:
- 3 copies of data
- 2 different media types
- 1 offsite copy

**Implementation**:
- Test restore procedures monthly
- Encrypt backups at rest
- Document recovery procedures
- Monitor backup job success/failure

### Cloud Backup Options

For AWS backup strategies (DocumentDB automated backups, S3 storage, snapshots), see [AWS Architecture Guide](aws-architecture.md).

---

## Disaster Recovery

### Recovery Objectives

- **RTO (Recovery Time Objective)**: < 1 hour
- **RPO (Recovery Point Objective)**: < 5 minutes

### Local Disaster Scenarios

#### 1. Database Corruption

**Recovery Steps**:
```bash
# 1. Stop application
docker-compose stop healthcare_migration

# 2. Copy backup to container
docker cp ./backups/mongodb/backup_latest.gz healthcare_mongodb:/tmp/

# 3. Restore from backup
docker exec healthcare_mongodb mongorestore \
  --uri="mongodb://localhost:27017" \
  --db=medical_records \
  --gzip \
  --archive=/tmp/backup_latest.gz

# 4. Restart application
docker-compose start healthcare_migration

# 5. Verify data integrity
docker exec healthcare_migration python -m csv_containerisation_mongodb.test.test
```

**Recovery Time**: ~10 minutes

#### 2. Container Failure

**Recovery Steps**:
```bash
# Restart container
docker-compose restart healthcare_mongodb

# Verify connectivity
docker exec healthcare_mongodb mongosh --eval "db.runCommand('ping')"

# Check container health
docker inspect healthcare_mongodb --format='{{.State.Health.Status}}'
```

**Recovery Time**: < 2 minutes

#### 3. Accidental Data Deletion

**Recovery Steps**:
```bash
# 1. Stop writes immediately
docker-compose stop healthcare_migration

# 2. Copy backup to container
docker cp ./backups/mongodb/backup_latest.gz healthcare_mongodb:/tmp/

# 3. Restore from backup
docker exec healthcare_mongodb mongorestore \
  --uri="mongodb://localhost:27017" \
  --db=medical_records \
  --gzip \
  --archive=/tmp/backup_latest.gz

# 4. Verify restoration
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.healthcare_data.countDocuments()"

# 5. Restart application
docker-compose start healthcare_migration
```

**Recovery Time**: ~10 minutes

#### 4. Complete System Failure

**Recovery Steps**:
```bash
# 1. Reinstall Docker and Docker Compose

# 2. Clone repository
git clone https://github.com/hhdonglo/csv-containerisation-mongodb.git
cd csv-containerisation-mongodb

# 3. Restore environment configuration
cp .env.backup .env

# 4. Start services
docker-compose up -d

# 5. Wait for MongoDB to be healthy
docker ps

# 6. Copy backup to container
docker cp ./backups/mongodb/backup_latest.gz healthcare_mongodb:/tmp/

# 7. Restore data
docker exec healthcare_mongodb mongorestore \
  --uri="mongodb://localhost:27017" \
  --db=medical_records \
  --gzip \
  --archive=/tmp/backup_latest.gz

# 8. Verify all services
docker-compose ps
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.healthcare_data.countDocuments()"
```

**Recovery Time**: ~30 minutes

### Cloud Disaster Recovery Options

For AWS disaster recovery strategies (Multi-AZ failover, cross-region replication, point-in-time recovery), see [AWS Architecture Guide](aws-architecture.md).

---

## Testing Procedures

### Unit Tests

**Run All Tests**:
```bash
# Run with pytest
pytest tests/test_migration.py -v

# Run with coverage
pytest tests/test_migration.py --cov=csv_containerisation_mongodb --cov-report=html

# Run specific test
pytest tests/test_migration.py::TestDataIntegrity::test_document_count -v
```

### Data Integrity Tests

**Automated Validation**:
```bash
# Run all integrity checks
python -m csv_containerisation_mongodb.test.test

# Or from Docker container
docker exec healthcare_migration python -m csv_containerisation_mongodb.test.test
```

**Manual Validation**:
```javascript
// Connect to MongoDB
use medical_records

// Count documents (should be 54,966)
db.healthcare_data.countDocuments()

// Sample documents
db.healthcare_data.find().limit(5).pretty()

// Check for duplicates
db.healthcare_data.aggregate([
  { $group: { _id: "$patient_info.name", count: { $sum: 1 } } },
  { $match: { count: { $gt: 1 } } }
])

// Verify field structure
db.healthcare_data.findOne()

// Check indexes
db.healthcare_data.getIndexes()
```

**Run Manual Validation via Docker**:
```bash
docker exec -it healthcare_mongodb mongosh medical_records \
  --eval "db.healthcare_data.countDocuments()"
```

---

## Troubleshooting

### Common Issues

#### 1. MongoDB Connection Failed

**Symptoms**:
```
ERROR: MongoDB connection failed - Connection refused
pymongo.errors.ServerSelectionTimeoutError
```

**Solutions**:
```bash
# Check if MongoDB container is running
docker ps | grep healthcare_mongodb

# Check MongoDB logs
docker logs healthcare_mongodb --tail 50

# Verify connectivity from migration container
docker exec healthcare_migration ping mongodb

# Check MongoDB status
docker exec healthcare_mongodb mongosh --eval "db.runCommand('ping')"

# Restart MongoDB if needed
docker-compose restart healthcare_mongodb
```

#### 2. Out of Memory Error

**Symptoms**:
```
MemoryError: Unable to allocate array
docker: Error response from daemon: OOM command not allowed when used memory > 'maxmemory'
```

**Solutions**:
```bash
# Check available memory
docker stats healthcare_migration

# Increase Docker memory limit (docker-compose.yml)
services:
  migration_app:
    deploy:
      resources:
        limits:
          memory: 4g
        reservations:
          memory: 2g

# Restart services
docker-compose down
docker-compose up -d
```

#### 3. Duplicate Key Error

**Symptoms**:
```
pymongo.errors.DuplicateKeyError: E11000 duplicate key error
```

**Solutions**:
```bash
# Check for duplicates in source CSV
python -c "
import pandas as pd
df = pd.read_csv('data/raw/healthcare.csv')
print(f'Total rows: {len(df)}')
print(f'Duplicates: {df.duplicated().sum()}')
print(f'Unique rows: {len(df.drop_duplicates())}')
"

# Drop and recreate collection
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.healthcare_data.drop()"

# Rerun migration
docker-compose restart healthcare_migration
```

#### 4. Slow Migration Performance

**Symptoms**:
```
Migration taking > 2 minutes
High CPU/Memory usage
```

**Solutions**:
```bash
# Check system resources
docker stats

# Check MongoDB performance
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.currentOp()"

# Optimize: Increase bulk insert batch size in migration.py
# Default: 5000, Try: 10000

# Optimize: Disable indexes during migration, recreate after
# See migration.py for index management

# Check for slow queries
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.setProfilingLevel(2); db.system.profile.find().limit(5).pretty()"
```

#### 5. Port Already in Use

**Symptoms**:
```
Error starting userland proxy: listen tcp4 0.0.0.0:27017: bind: address already in use
Error starting userland proxy: listen tcp4 0.0.0.0:8081: bind: address already in use
```

**Solutions**:
```bash
# Check what's using the port
lsof -i :27017
lsof -i :8081

# Kill the process or change ports in docker-compose.yml
# For example, change MongoDB port:
ports:
  - "27018:27017"  # Use 27018 on host instead

# Restart services
docker-compose down
docker-compose up -d
```

#### 6. Container Keeps Restarting

**Symptoms**:
```
docker ps shows container restarting repeatedly
Status: Restarting (1) X seconds ago
```

**Solutions**:
```bash
# Check container logs
docker logs healthcare_mongodb --tail 100
docker logs healthcare_migration --tail 100

# Check for configuration errors
docker inspect healthcare_mongodb

# Common causes:
# - Invalid MongoDB credentials
# - Missing environment variables
# - Insufficient resources
# - Port conflicts

# Fix and restart
docker-compose down
# Fix the issue in docker-compose.yml or .env
docker-compose up -d
```

### Debug Mode

**Enable Debug Logging**:
```bash
# Set environment variable in .env file
LOG_LEVEL=DEBUG

# Or export directly
export LOG_LEVEL=DEBUG

# Run with verbose output
python -m csv_containerisation_mongodb.main.main --verbose

# Docker logs with timestamp
docker-compose logs -f --tail 1000 --timestamps

# Filter logs for specific container
docker-compose logs healthcare_migration | grep ERROR
```

**Interactive Debugging**:
```bash
# Enter MongoDB container shell
docker exec -it healthcare_mongodb bash

# Enter migration container shell
docker exec -it healthcare_migration bash

# Run Python interactively in migration container
docker exec -it healthcare_migration python

# Test MongoDB connection interactively
docker exec -it healthcare_mongodb mongosh medical_records
```

---

## Best Practices

### Operational Best Practices

1. **Regular Monitoring**: Check container stats daily using `docker stats`
2. **Backup Verification**: Test restores monthly to ensure backups work
3. **Update Dependencies**: Keep Poetry packages current with `poetry update`
4. **Security Patches**: Apply Docker and system updates promptly
5. **Documentation**: Keep runbooks updated with any configuration changes
6. **Change Management**: Document all changes in git commit messages
7. **Health Checks**: Monitor container health status regularly
8. **Resource Planning**: Monitor trends and plan for capacity increases

### Backup Best Practices

1. **Automate Everything**: Use cron jobs, no manual backups
2. **Test Restores Monthly**: Ensure backups are valid and restorable
3. **Multiple Locations**: Store backups on-site + off-site (e.g., S3)
4. **Encrypt Backups**: Protect sensitive healthcare data
5. **Monitor Jobs**: Set up alerts for backup failures
6. **Retention Policy**: Keep daily backups for 7 days, weekly for 4 weeks, monthly for 12 months
7. **Document Procedures**: Maintain clear backup and restore documentation
8. **Version Control**: Track backup script changes in git

### Security Best Practices

1. **Credential Management**: Use .env files, never commit credentials
2. **Network Isolation**: Use Docker networks to isolate services
3. **Regular Updates**: Keep all dependencies and images updated
4. **Access Control**: Implement least privilege access
5. **Audit Logs**: Enable and monitor MongoDB audit logs
6. **Encryption**: Use TLS for MongoDB connections in production

---

## Operational Metrics

### Key Performance Indicators

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Uptime** | 99.9% | 99.95% | PASS |
| **Migration Time** | < 1 min | 45 sec | PASS |
| **Test Pass Rate** | 100% | 100% | PASS |
| **Backup Success** | 100% | 100% | PASS |
| **Data Integrity** | 100% | 100% | PASS |
| **Records Processed** | 54,966 | 54,966 | PASS |

### Performance Baselines
```yaml
Pipeline Performance:
  - Data Loading: ~5 seconds
  - Data Cleaning: ~10 seconds (includes deduplication)
  - MongoDB Migration: ~25 seconds (bulk insert 5,000/batch)
  - Integrity Validation: ~5 seconds
  - Total Pipeline Time: ~45 seconds

Resource Usage (Docker):
  - CPU: 30-40% average during migration
  - Memory: 2-3 GB peak (MongoDB + Python)
  - Disk I/O: 50 MB/s during bulk insert
  - Network: 10 Mbps internal container communication

Data Metrics:
  - Initial Load: 55,500 rows
  - Duplicates Removed: 534 rows (0.96%)
  - Final Dataset: 54,966 rows
  - Memory Optimization: 20.96% reduction
  - Fields per Document: 15 columns
```

### Monitoring Checklist

**Daily**:
- [ ] Check container status: `docker ps`
- [ ] Review logs for errors: `docker-compose logs | grep ERROR`
- [ ] Verify disk space: `df -h`
- [ ] Check backup completion

**Weekly**:
- [ ] Review performance metrics
- [ ] Check for Docker/system updates
- [ ] Verify backup integrity
- [ ] Review security logs

**Monthly**:
- [ ] Test backup restore procedure
- [ ] Review and update documentation
- [ ] Performance optimization review
- [ ] Security audit

---

## Quick Reference Commands

### Common Docker Commands
```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View all logs
docker-compose logs -f

# View specific container logs
docker logs -f healthcare_mongodb

# Check container status
docker ps

# Check container stats
docker stats

# Enter container shell
docker exec -it healthcare_mongodb bash

# Run MongoDB shell
docker exec -it healthcare_mongodb mongosh medical_records

# Restart specific service
docker-compose restart healthcare_mongodb

# View container details
docker inspect healthcare_mongodb
```

### Common MongoDB Commands
```bash
# Count documents
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.healthcare_data.countDocuments()"

# Check database size
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.stats()"

# List collections
docker exec healthcare_mongodb mongosh medical_records \
  --eval "db.getCollectionNames()"

# Backup database
docker exec healthcare_mongodb mongodump \
  --db=medical_records --gzip --archive=/tmp/backup.gz

# Restore database
docker exec healthcare_mongodb mongorestore \
  --db=medical_records --gzip --archive=/tmp/backup.gz
```

---

## Contact and Support

For issues, questions, or contributions:

- **GitHub Issues**: [github.com/hhdonglo/csv-containerisation-mongodb/issues](https://github.com/hhdonglo/csv-containerisation-mongodb/issues)
- **Documentation**: See main [README.md](../README.md)
- **AWS Guide**: See [aws-architecture.md](aws-architecture.md)
- **Security Guide**: See [security.md](security.md)

---

*This operations guide is maintained as part of the Healthcare Data Migration Pipeline project. Last updated: January 2026*