
# Real Estate Analytics Pipeline - Complete Project Documentation

**Last Updated:** [Current Date]  
**Status:** In Progress  
**Completion:** 0%

---

## Project Overview

### Goal
Build an event-driven ETL pipeline for real estate listing analytics using GCP managed services.

### Why This Project?
- Demonstrates skills required for Bayut & Dubizzle Data Engineer Intern role
- Shows understanding of: ETL pipelines, cloud data warehousing, SQL, data modeling
- Similar architecture to production systems (Matillion + Redshift + S3)

### Timeline
- **Total Time:** 2 days
- **Day 1:** ETL Pipeline (6-8 hours)
- **Day 2:** Analytics & Visualization (6-8 hours)

### Tech Stack
- **Cloud Platform:** Google Cloud Platform (GCP)
- **Storage:** Cloud Storage (GCS buckets)
- **Compute:** Cloud Functions (Python 3.10, serverless)
- **Data Warehouse:** BigQuery
- **Visualization:** Looker Studio
- **Version Control:** GitHub

### Cost
**Target:** $0 using GCP Free Tier
- Cloud Storage: 5GB free (us-central1)
- Cloud Functions: 2M invocations/month free
- BigQuery: 10GB storage + 1TB queries/month free

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        SOURCE LAYER                             │
│  User uploads CSV → GCS Landing Bucket                          │
│  (real-estate-landing bucket)                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Storage Event Trigger
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INGESTION LAYER                             │
│  Cloud Function: ETL Function                                   │
│  - Validates CSV file (extension, size, schema)                 │
│  - Reads CSV into Pandas DataFrame                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                             │
│  Transformation Logic (within ETL Function)                     │
│  - Handle missing values                                        │
│  - Standardize formats (dates, text)                            │
│  - Remove outliers                                              │
│  - Calculate derived fields (price_per_sqft)                    │
│  - Create dimension keys                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   WAREHOUSING LAYER                             │
│  BigQuery: Star Schema Data Warehouse                           │
│                                                                 │
│  ┌─────────────────┐      ┌──────────────────┐                │
│  │  dim_location   │──┐   │ dim_property_type│──┐             │
│  │  - location_id  │  │   │ - property_type_id│ │             │
│  │  - city         │  │   │ - type_name       │ │             │
│  │  - state        │  │   │ - category        │ │             │
│  └─────────────────┘  │   └──────────────────┘  │             │
│                       │                          │             │
│  ┌─────────────────┐ │   ┌─────────────────────┐│             │
│  │   dim_date      │─┼───│  fact_listings      ││             │
│  │  - date_id      │ │   │  - listing_id (PK)  ││             │
│  │  - full_date    │ │   │  - location_id (FK) ││             │
│  │  - year, month  │ │   │  - property_type_id ││             │
│  │  - quarter      │ └───│  - date_id (FK)     ││             │
│  └─────────────────┘     │  - price            ││             │
│                          │  - bedrooms         ││             │
│                          │  - sqft             ││             │
│                          │  - price_per_sqft   ││             │
│                          └─────────────────────┘│             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Table Update Trigger (or Manual)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ANALYTICS LAYER                             │
│  Cloud Function: Analytics Function                             │
│  - Executes SQL queries on BigQuery                             │
│  - Calculates metrics and insights                              │
│  - Formats results                                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                            │
│  Outputs:                                                       │
│  1. GCS Reports Bucket (HTML + JSON reports)                    │
│  2. Looker Studio Dashboard (interactive visualizations)        │
└─────────────────────────────────────────────────────────────────┘
```

---

## GCP Project Setup

### Project Information
- **Project ID:** `[TO BE FILLED]`
- **Project Name:** `[TO BE FILLED]`
- **Region:** us-central1 (free tier eligible)
- **Billing Account:** [Required for Cloud Functions]

### APIs to Enable
```bash
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

---

## Cloud Storage Configuration

### Bucket 1: Landing Bucket (Raw Data)
```bash
Bucket Name: {project-id}-real-estate-landing
Location: us-central1
Storage Class: Standard
Access Control: Uniform (bucket-level)
Purpose: Receives raw CSV uploads, triggers ETL function
```

**Creation Command:**
```bash
export PROJECT_ID="your-project-id-here"
export BUCKET_LANDING="${PROJECT_ID}-real-estate-landing"
gsutil mb -l us-central1 gs://${BUCKET_LANDING}
```

### Bucket 2: Reports Bucket (Outputs)
```bash
Bucket Name: {project-id}-real-estate-reports
Location: us-central1
Storage Class: Standard
Access Control: Uniform
Purpose: Stores generated HTML and JSON reports
```

**Creation Command:**
```bash
export BUCKET_REPORTS="${PROJECT_ID}-real-estate-reports"
gsutil mb -l us-central1 gs://${BUCKET_REPORTS}
```

---

## BigQuery Configuration

### Dataset
```bash
Dataset ID: real_estate_dw
Location: us-central1
Default table expiration: None
Description: Real estate data warehouse
```

**Creation Command:**
```bash
bq mk --dataset \
  --location=us-central1 \
  --description="Real estate data warehouse" \
  ${PROJECT_ID}:real_estate_dw
```

### Star Schema Design

#### Table 1: dim_location (Dimension)
**Purpose:** Store unique locations (cities, states)

```sql
CREATE TABLE `{project_id}.real_estate_dw.dim_location` (
  location_id INT64 NOT NULL,
  city STRING,
  state STRING,
  zip_code STRING,
  region STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) OPTIONS(
  description="Location dimension table"
);
```

**Sample Data:**
| location_id | city | state | zip_code | region |
|------------|------|-------|----------|--------|
| 1 | Dubai Marina | Dubai | - | UAE |
| 2 | Downtown Dubai | Dubai | - | UAE |

---

#### Table 2: dim_property_type (Dimension)
**Purpose:** Store property types and categories

```sql
CREATE TABLE `{project_id}.real_estate_dw.dim_property_type` (
  property_type_id INT64 NOT NULL,
  type_name STRING NOT NULL,
  category STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) OPTIONS(
  description="Property type dimension table"
);
```

**Sample Data:**
| property_type_id | type_name | category |
|-----------------|-----------|----------|
| 1 | Apartment | Residential-Apartment |
| 2 | Villa | Residential-House |
| 3 | Townhouse | Residential-Townhouse |

---

#### Table 3: dim_date (Dimension)
**Purpose:** Date dimension for time-based analysis

```sql
CREATE TABLE `{project_id}.real_estate_dw.dim_date` (
  date_id INT64 NOT NULL,
  full_date DATE NOT NULL,
  year INT64,
  month INT64,
  month_name STRING,
  quarter INT64,
  day_of_week INT64,
  day_name STRING,
  is_weekend BOOL
) OPTIONS(
  description="Date dimension table"
);
```

**Sample Data:**
| date_id | full_date | year | month | month_name | quarter |
|---------|-----------|------|-------|------------|---------|
| 20240101 | 2024-01-01 | 2024 | 1 | January | 1 |
| 20240102 | 2024-01-02 | 2024 | 1 | January | 1 |

---

#### Table 4: fact_listings (Fact Table)
**Purpose:** Main transaction table with measurements

```sql
CREATE TABLE `{project_id}.real_estate_dw.fact_listings` (
  listing_id INT64 NOT NULL,
  location_id INT64,
  property_type_id INT64,
  date_id INT64,
  
  -- Transaction details
  list_date DATE,
  listing_status STRING,
  
  -- Measurements
  price FLOAT64,
  bedrooms INT64,
  bathrooms FLOAT64,
  sqft INT64,
  lot_size INT64,
  
  -- Calculated fields
  price_per_sqft FLOAT64,
  
  -- Metadata
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP
) OPTIONS(
  description="Fact table for real estate listings"
);
```

---

## Cloud Functions Configuration

### Function 1: ETL Function

**Basic Info:**
```yaml
Function Name: real-estate-etl-function
Runtime: Python 3.10
Entry Point: process_csv
Region: us-central1
Memory: 256 MB
Timeout: 60 seconds
```

**Trigger:**
```yaml
Trigger Type: Cloud Storage
Event Type: Finalize/Create
Bucket: {project-id}-real-estate-landing
```

**Environment Variables:**
```bash
PROJECT_ID=your-project-id
DATASET_ID=real_estate_dw
```

**Service Account Permissions Required:**
- Cloud Storage: Read (landing bucket)
- BigQuery: Data Editor, Job User

---

### Function 2: Analytics Function

**Basic Info:**
```yaml
Function Name: real-estate-analytics-function
Runtime: Python 3.10
Entry Point: generate_report
Region: us-central1
Memory: 512 MB
Timeout: 120 seconds
```

**Trigger:**
```yaml
Trigger Type: HTTP (for manual triggering)
OR
Trigger Type: Pub/Sub (for automated scheduling)
```

**Environment Variables:**
```bash
PROJECT_ID=your-project-id
DATASET_ID=real_estate_dw
REPORTS_BUCKET={project-id}-real-estate-reports
```

**Service Account Permissions Required:**
- BigQuery: Data Viewer, Job User
- Cloud Storage: Write (reports bucket)

---

## Sample Data Schema

### Input CSV Format
The ETL function expects CSV files with these columns:

```csv
listing_id,list_date,location,property_type,price,bedrooms,bathrooms,sqft
1,2024-01-15,"Dubai Marina, Dubai",Apartment,750000,2,2,1200
2,2024-01-16,"Downtown Dubai, Dubai",Villa,2500000,4,3.5,3500
```

**Required Columns:**
- `list_date` (DATE format: YYYY-MM-DD)
- `location` (STRING: "City, State" or "City")
- `property_type` (STRING: Apartment, Villa, Townhouse, etc.)
- `price` (NUMERIC: listing price)
- `bedrooms` (INTEGER)
- `bathrooms` (NUMERIC: can be decimal like 2.5)
- `sqft` (INTEGER: square footage)

**Optional Columns:**
- `listing_id` (will be auto-generated if missing)
- `lot_size` (INTEGER)
- `listing_status` (STRING)

---

## Analytical Queries

### Query Categories:

**1. Time Series Analysis**
- Monthly price trends
- Seasonal patterns
- Growth rates year-over-year

**2. Statistical Analysis**
- Price distributions
- Correlation analysis (price vs sqft, bedrooms)
- Outlier detection

**3. Business Intelligence**
- Location performance comparison
- Property type analysis
- Price per square foot benchmarks
- Top/bottom performers

---

## Implementation Checklist

### Phase 1: Setup (Day 1 Morning)
- [ ] Create GCP project
- [ ] Enable required APIs
- [ ] Create Cloud Storage buckets
- [ ] Create BigQuery dataset
- [ ] Create BigQuery tables (schema)

### Phase 2: ETL Function (Day 1 Afternoon)
- [ ] Create `cloud-functions/etl-function/main.py`
- [ ] Create `cloud-functions/etl-function/transform.py`
- [ ] Create `cloud-functions/etl-function/load.py`
- [ ] Create `cloud-functions/etl-function/requirements.txt`
- [ ] Deploy ETL function to GCP
- [ ] Test with sample CSV

### Phase 3: Analytics Function (Day 2 Morning)
- [ ] Create `cloud-functions/analytics-function/main.py`
- [ ] Write SQL analytical queries
- [ ] Implement HTML report generation
- [ ] Deploy analytics function
- [ ] Test report generation

### Phase 4: Visualization (Day 2 Afternoon)
- [ ] Connect Looker Studio to BigQuery
- [ ] Create dashboard with key metrics
- [ ] Add filters and interactivity
- [ ] Generate sample reports

### Phase 5: Documentation (Day 2 Evening)
- [ ] Write comprehensive README
- [ ] Document deployment steps
- [ ] Add architecture diagrams
- [ ] Include sample outputs
- [ ] Create GitHub repository
- [ ] Push all code

---

## Progress Log

### Session 1: [Date]
**Completed:**
- Created project structure
- Created PROJECT_PLAN.md

**Next Steps:**
- [To be filled as you progress]

**Blockers:**
- None yet

---

## Resources & References

### Documentation Links:
- [GCP Cloud Functions Python Guide](https://cloud.google.com/functions/docs/quickstart-python)
- [BigQuery Python Client](https://cloud.google.com/python/docs/reference/bigquery/latest)
- [Cloud Storage Python Client](https://cloud.google.com/python/docs/reference/storage/latest)
- [Looker Studio](https://lookerstudio.google.com/)

### Similar Projects:
- Lankapack Data Lake (reference for architecture patterns)
- [Link to your Lankapack project report]

### Job Description Reference:
- Role: Data Engineer Intern - Bayut & Dubizzle
- Key Skills: SQL, ETL (Matillion), BigQuery/Redshift, Cloud data warehousing
- Focus: Business intelligence, data visualization, working with business teams

---




