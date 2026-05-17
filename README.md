# PacCafe Data Integration & ETL Pipeline

## Requirement Gathering

### Business Background

PacCafe is a growing cafe business with multiple store branches. The management team wants to perform analysis based on data and build a dashboard to monitor business performance. However, the data is scattered across multiple sources in different formats and systems, making it difficult and time consuming for the owner to access and analyze the data manually.

### Problem Statement

|  | Problem | Impact |
|---|---|---|
| 1 | Data scattered across multiple sources (PostgreSQL, Google Sheets) with no central repository | Owner must manually merge data from multiple tools to get complete analysis |
| 2 | No automated data pipeline; all consolidation done manually | High risk of human error, slow reporting cycle, wasted analyst time |
| 3 | Raw data contains inconsistencies, nulls, and duplicate records | Unreliable reports and incorrect business decisions |
| 5 | No logging and backup process for pipeline failures | Missing data in reports and difficult troubleshooting |

### Proposed Solutions

|  | Problem | Solution |
|---|---|---|
| 1 | Scattered data across sources | Build centralized staging layer in PostgreSQL to combine data from all sources into single schema |
| 2 | No automated pipeline | Develop ETL scripts for staging and warehouse layers |
| 3 | Inconsistent and dirty raw data | Apply data cleaning and validation (type casting, null handling, deduplication, standardization) |
| 5 | No logging and error fallback | Implement structured logging and store failed records in MinIO Object Storage |

---

## Data Sources & Sink

### Source Systems

- **PostgreSQL** : customers, employees, products, inventory_tracking, orders, order_details
- **Google Sheets** : store_branch

### Sink

- **staging** : Raw data from all source systems is loaded into the staging database without any modifications.
- **warehouse** : Data from the staging layer is then transformed based on business requirements.

### Error Storage

MinIO (S3-compatible object storage) is used as a fallback for failed records.

---

## Tech Stack

| Category | Tool | Purpose |
|---|---|---|
| Containerization | Docker Compose | Used to run PostgreSQL, MinIO, and source database services in containers |
| Pipeline Language | Python | Used to build the core logic for extracting, transforming, and loading data |
| Spreadsheet Connector | gspread + google-auth | Fetch data from Google Sheets via Service Account |
| Object Storage | MinIO | Stores failed records as JSON files for easier recovery |

---

## Pipeline Workflow

1. **Setting up** : Set up logger, load .env, validate DB and MinIO connections
2. **Extract — PostgreSQL** : Read all tables from source schema in PostgreSQL
3. **Extract — Google Sheets** : Fetch store data via Sheets API
4. **Load to Staging** : Insert/upsert all extracted records into staging schema
5. **Transform** : Transform based on business requirements such as handling null values
6. **Load to Warehouse** : Insert transformed data into warehouse database
7. **Error Handling** : If a failue occurs, log the error and store failed records in MinIO

---

## Contact & Questions

For any further question, feel free to reach out to me at [Linkedin](https://www.linkedin.com/in/adila-zahra-faradisa/)
