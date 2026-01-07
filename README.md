# Healthcare Data Migration Pipeline
## NoSQL Database Migration with MongoDB, Docker & AWS

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-8.2-green.svg)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![Poetry](https://img.shields.io/badge/Poetry-Dependency%20Management-purple.svg)](https://python-poetry.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **OpenClassrooms Data Engineering Project 5** | DataSoluTech Medical Data Migration Solution

---

## Executive Summary

Production-ready ETL pipeline migrating **54,966 medical records** from CSV to MongoDB with automated data quality assurance, Docker containerization, and comprehensive AWS deployment research. Built for a healthcare provider experiencing scalability issues with traditional relational databases.

**Key Achievements**: Zero data integrity issues, 21% memory optimization, 100% test pass rate, 45-second processing time.

---

## Table of Contents
- [Problem Statement & Solution](#problem-statement--solution)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Database Schema](#database-schema)
- [Data Quality](#data-quality)
- [Technologies](#technologies)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## Problem Statement & Solution

**Client Challenge**: Healthcare provider experiencing scalability issues with daily patient record management using traditional relational database.

**Solution Delivered**: 
- Automated CSV-to-MongoDB migration pipeline with 7-step ETL workflow
- Dockerized infrastructure for portability and scalability
- AWS deployment research (DocumentDB, ECS, S3 cost analysis)
- Production-ready documentation and security guidelines

---

## Key Features

### ETL Automation
- 7-step orchestrated workflow from raw CSV to validated MongoDB documents
- Automated data cleaning (name standardization, duplicate removal)
- Memory optimization (21% reduction via categorical types, datetime conversion)
- Comprehensive quality reporting (markdown + CSV formats)

### Data Quality & Validation
- 5-tier integrity testing suite (document count, field structure, data types, missing values, duplicates)
- Automated pytest validation with 100% pass rate
- Real-time quality metrics and anomaly detection

### Containerized Deployment
- Full Docker + Docker Compose orchestration
- MongoDB 8.2 with health checks and auto-restart policies
- Mongo Express web UI for database management (port 8081)
- Environment-based configuration for credential security

### Cloud-Ready Architecture
- AWS deployment research (DocumentDB vs Atlas vs EC2 vs ECS)
- Cost analysis (~$247/month production, reduces to $62/month with Reserved Instances)
- Disaster recovery planning (RTO <1hr, RPO <5min)
- HIPAA compliance considerations

---

## Architecture

### ETL Pipeline Flow

![ETL Pipeline Flow](docs/images/etl_pipeline_flow.png)

**Pipeline Stages**:

**[1] Load Raw CSV** - Ingests 55,500 patient records from source CSV file

**[2] Data Cleaning** - Processes data through 4 parallel operations:
- **Name Std.**: Standardizes patient names (title case, whitespace trimming)
- **Dup. Removal**: Removes 534 duplicate records (-0.96%)
- **Type Opt.**: Optimizes data types for 20.96% memory reduction
- **Quality Reports**: Generates detailed metrics and validation reports

**[3] MongoDB Connection** - Establishes authenticated database connection with health validation

**[4] Load Cleaned Data** - Loads processed dataset (54,966 rows, 15 columns)

**[5] Bulk Insert** - Performs batch insertion to MongoDB (5,000 documents per batch)

**[6] Integrity Validation** - Executes 5-tier validation suite (100% pass rate)

**[7] Success** - Pipeline completion with summary statistics

**Processing Time**: ~45 seconds (5s load + 10s clean + 25s migrate + 5s validate)

---

### Docker Infrastructure

![Docker Infrastructure](docs/images/docker_infrastructure.png)

**Container Architecture**:

**healthcare_mongo_ui** (Mongo Express)
- Web-based MongoDB management interface
- Port 8081 (accessible at http://localhost:8081)
- Provides visual database exploration and query tools

**healthcare_migration** (Python 3.13)
- Executes the ETL migration pipeline
- Connects to MongoDB via `mongodb://27017`
- Runs automated data processing and validation

**healthcare_mongodb** (MongoDB 8.2)
- Primary database container
- Port 27017 (internal network)
- Persistent data storage via mounted volume

**healthcare_network** (Bridge Network)
- Isolated Docker network for inter-container communication
- Secure internal DNS resolution
- Network isolation from host

**mongo_data** (Docker Volume)
- Persistent storage for MongoDB data files
- Survives container restarts and updates
- Enables backup and recovery operations

**Connection Flow**:
- Migration app → MongoDB: `mongodb://27017` (database operations)
- Mongo Express → MongoDB: `http://27017` (management interface)
- All containers communicate through the dedicated bridge network
- Volume ensures data persistence across container lifecycle

---

### Pipeline Components

| Component | Responsibility | Output |
|-----------|---------------|---------|
| **load_data.py** | CSV ingestion with validation | DataFrame |
| **cleaning.py** | Data standardization & quality checks | Cleaned CSV + Reports |
| **migration.py** | MongoDB connection & bulk insertion | Structured documents |
| **test.py** | Data integrity validation | Test reports |
| **pipeline.py** | Orchestration and error handling | Pipeline status |

---

## Quick Start

### Prerequisites

- **Python** 3.13+
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **Poetry** 1.7+ (or pip)

### Installation

**1. Clone Repository**
```bash
git clone https://github.com/yourusername/healthcare-data-migration.git
cd healthcare-data-migration
```

**2. Install Dependencies**
```bash
# Using Poetry (Recommended)
poetry install
poetry shell

# Or using pip
pip install -r requirements.txt
```

**3. Configure Environment**
```bash
cp .env.example .env
nano .env
```

**.env Configuration**:
```env
MONGO_USERNAME=your_username
MONGO_PASSWORD=your_secure_password
MONGO_DATABASE=medical_records
MONGO_URI=mongodb://your_username:your_password@mongodb:27017/medical_records?authSource=admin
```

**4. Prepare Data**
```bash
mkdir -p data/raw
cp your_healthcare_data.csv data/raw/healthcare.csv
```

### Run the Pipeline

**Docker Deployment (Recommended)**:
```bash
# Start entire stack
docker-compose up -d

# View logs in real-time
docker-compose logs -f migration_app

# Access Mongo Express UI
# http://localhost:8081

# Stop services
docker-compose down
```

**Local Development**:
```bash
# Run pipeline
python -m csv_containerisation_mongodb.main.main

# Run tests
pytest tests/test_migration.py -v
```

### Verify Success

**Check Pipeline Output**:
```
data/processed/
├── cleaned_healthcare.csv           # Cleaned data (54,966 rows)
├── healthcare_cleaning_report.md    # Detailed cleaning report
└── healthcare_quality_report.csv    # Quality metrics
```

**Verify MongoDB Data**:
```bash
# Via Mongo Express UI: http://localhost:8081

# Or via CLI
docker exec -it healthcare_mongodb mongosh medical_records \
  -u your_username -p your_password --authenticationDatabase admin \
  --eval "db.healthcare_data.countDocuments()"
```

---

## Database Schema

### Document Structure (Nested Design)
```javascript
{
  "patient_info": {
    "name": String,
    "age": Integer,
    "gender": String,
    "blood_type": String
  },
  "medical_details": {
    "medical_condition": String,  // Indexed
    "medication": String,
    "test_results": String
  },
  "admission_details": {
    "admission_date": ISODate,    // Indexed
    "admission_type": String,
    "room_number": Integer,
    "discharge_date": ISODate
  },
  "hospital_info": {
    "hospital": String,           // Indexed (compound)
    "doctor": String
  },
  "billing": {
    "insurance_provider": String,
    "billing_amount": Double
  },
  "metadata": {
    "created_at": ISODate,
    "updated_at": ISODate,
    "data_source": "CSV_migration",
    "migrated_by": "Hope - OpenClassroom-project"
  }
}
```

### Indexing Strategy
```javascript
// Optimized indexes for common queries
db.healthcare_data.createIndex({ "patient_info.name": 1 })
db.healthcare_data.createIndex({ "admission_details.admission_date": 1 })
db.healthcare_data.createIndex({
  "medical_details.medical_condition": 1,
  "hospital_info.hospital": 1
})
```

**Design Rationale**:
- Nested documents eliminate complex joins
- Indexes optimize patient lookups, date-range queries, and hospital analytics
- Logical grouping improves read performance and developer experience

For detailed schema documentation and query examples, see [Operations Guide](docs/operations.md).

---

## Data Quality

### Automated Testing Suite

| Test | Validation | Pass Criteria |
|------|-----------|---------------|
| **Document Count** | Total records match | CSV rows = MongoDB docs |
| **Field Structure** | Schema completeness | All CSV columns present |
| **Missing Values** | Null handling | Missing % match (<0.01% diff) |
| **Data Types** | Type correctness | Types match schema |
| **Duplicates** | Duplicate preservation | Duplicate count match |

**Test Coverage**: 100% (5/5 tests passing)

### Quality Metrics

**Pipeline Results**:
```
Initial Load:    55,500 rows, 15 columns
Duplicates:      534 rows removed (0.96%)
Final Dataset:   54,966 rows, 15 columns
Memory Before:   37.97 MB
Memory After:    30.01 MB
Memory Saved:    7.96 MB (20.96% reduction)
Processing Time: ~45 seconds
Test Results:    5/5 passed (100%)
```

**Run Tests**:
```bash
pytest tests/test_migration.py -v
```

For complete testing procedures and quality assurance documentation, see [Operations Guide](docs/operations.md).

---

## Technologies

### Core Stack
- **Python 3.13**: Primary language
- **MongoDB 8.2**: NoSQL database
- **Docker & Docker Compose**: Containerization
- **Poetry**: Dependency management

### Key Libraries
```toml
[tool.poetry.dependencies]
python = "^3.13"
pandas = "^2.2.0"              # Data manipulation
pymongo = "^4.6.1"             # MongoDB driver
pytest = "^7.4.3"              # Testing framework
python-dotenv = "^1.0.0"       # Environment management
```

### Development Tools
- **pytest**: Automated testing
- **Black**: Code formatting
- **Ruff**: Linting
- **Mongo Express**: Database GUI

---

## Project Structure
```
healthcare-data-migration/
├── src/csv_containerisation_mongodb/    # Python application code
│   ├── main/                            # Entry point and orchestration
│   ├── data/                            # Data loading and cleaning
│   ├── migration/                       # MongoDB operations
│   ├── test/                            # Integrity validation
│   └── utils/                           # Utility functions
├── tests/                               # Test suite
├── data/
│   ├── raw/                             # Source CSV files
│   └── processed/                       # Cleaned data and reports
├── docs/
│   ├── aws-architecture.md              # Cloud deployment research
│   ├── operations.md                    # Operations and monitoring
│   ├── security.md                      # Security and compliance
│   └── images/                          # Architecture diagrams
├── docker/
│   └── Dockerfile                       # Application container
├── docker-compose.yml                   # Service orchestration
├── pyproject.toml                       # Dependencies
└── README.md                            # Main documentation
```

---

## Documentation

Comprehensive documentation organized by audience and use case:

### Documentation Suite

| Document | Audience | Purpose |
|----------|---------|---------|
| **[README.md](README.md)** | All stakeholders | Overview and quick start |
| **[AWS Architecture](docs/aws-architecture.md)** | Cloud engineers, architects | Deployment options, cost analysis, service comparisons |
| **[Operations Guide](docs/operations.md)** | DevOps, SRE teams | Pipeline operations, monitoring, backups, disaster recovery |
| **[Security Guide](docs/security.md)** | Security engineers, auditors | Authentication, authorization, HIPAA compliance |

### Additional Resources

- [MongoDB Best Practices](https://www.mongodb.com/docs/manual/administration/production-notes/)
- [Docker Documentation](https://docs.docker.com/)
- [AWS DocumentDB Guide](https://docs.aws.amazon.com/documentdb/)
- [Poetry Documentation](https://python-poetry.org/docs/)

### Generated Reports

All pipeline runs generate:
- **Cleaning Report**: `data/processed/healthcare_cleaning_report.md`
- **Quality CSV**: `data/processed/quality_report_healthcare.csv`
- **Test Results**: pytest terminal output with detailed validation

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Standards
- Follow PEP 8 style guide
- Add docstrings to all functions
- Include unit tests for new features
- Update documentation as needed

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**Hope Donglo**  
*Data Engineering Student | OpenClassrooms*

- **Organization**: DataSoluTech
- **Project**: OpenClassrooms Data Engineering Path - Project 5
- **Certification**: Data Engineering (October 2025 - October 2026)
- **GitHub**: [github.com/hhdonglo](https://github.com/hhdonglo)

---

## Acknowledgments

- **OpenClassrooms**: Educational framework and project guidance
- **DataSoluTech**: Professional project scenario and requirements
- **MongoDB Community**: Excellent documentation and tools
- **Docker**: Containerization platform

---

## Project Status

**Status**: ✅ Completed  
**Version**: 1.0.0  
**Last Updated**: January 2026

### Pipeline Statistics
- **Records Processed**: 54,966 (from 55,500 raw)
- **Duplicates Removed**: 534 (0.96%)
- **Memory Optimization**: 20.96% reduction
- **Processing Time**: ~45 seconds
- **Test Coverage**: 100% (5/5 tests passing)
- **Data Integrity**: Zero issues detected

---

**⭐ If you find this project useful, please give it a star!**

---

*This project was developed as part of the OpenClassrooms Data Engineering certification program, demonstrating practical expertise in NoSQL databases, ETL pipeline development, Docker containerization, and cloud architecture research.*