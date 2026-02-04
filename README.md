
# 🏠 Real Estate Analytics Data Pipeline

End-to-end real estate analytics pipeline with automated ETL, BigQuery data warehouse, and interactive dashboards. Built with Python, Google Cloud Platform, and modern BI tools.

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![GCP](https://img.shields.io/badge/GCP-BigQuery-orange.svg)](https://cloud.google.com/bigquery)
[![Power BI](https://img.shields.io/badge/Power%20BI-Interactive-yellow.svg)](https://powerbi.microsoft.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Live Dashboards

### Power BI Dashboard (Interactive)
**[ View Live Power BI Dashboard](https://app.powerbi.com/groups/me/reports/50cc17b1-f3a8-49d5-b7ba-f2e0b6a5cb35/001f08d923813c040153?experience=power-bi)**

- 12+ interactive visualizations across 3 pages
- Real-time connection to BigQuery data warehouse
- DAX measures for advanced analytics
- Cross-filtering and drill-down capabilities
- Custom price segmentation and trend analysis

### Looker Studio Dashboard
**[ View Looker Studio Dashboard](#)** *(Add your Looker link)*

- Web-based collaborative analytics
- Live data from BigQuery
- Date range and location filters
- Mobile-responsive design

![Power BI Dashboard Preview](docs/screenshots/powerbi-dashboard-overview.png)

---

## Project Overview

This project demonstrates a production-grade data engineering pipeline that:

✅ **Automatically processes** property listing data from CSV uploads  
✅ **Validates and cleans** data with outlier detection and missing value handling  
✅ **Loads into BigQuery** using dimensional modeling (star schema)  
✅ **Generates automated reports** with comprehensive analytics  
✅ **Provides interactive dashboards** in both Power BI and Looker Studio  

**Business Context:** UAE real estate market analysis covering Dubai, Abu Dhabi, and Sharjah with 988+ property listings.

---

## Architecture

```
CSV Upload (GCS)
    ↓ [Cloud Storage Trigger]
ETL Cloud Function (Python)
    ├─ Extract: Read & validate CSV
    ├─ Transform: Clean, normalize, detect outliers
    └─ Load: BigQuery star schema
         ↓
BigQuery Data Warehouse
    ├─ dim_location (15 cities)
    ├─ dim_property_type (5 types)
    ├─ dim_date (181 dates)
    └─ fact_listings (988 records)
         ↓
Analytics Cloud Function (Python)
    ├─ Execute 8 SQL queries
    ├─ Generate HTML reports
    └─ Export JSON data
         ↓
Visualization Layer
    ├─ Power BI Dashboard (Interactive)
    ├─ Looker Studio Dashboard (Web-based)
    └─ Automated HTML Reports (GCS)
```

**Pipeline Processing Time:** ~2 minutes from upload to insights  
**Manual Intervention Required:** Zero (fully automated)

---

##  Tech Stack

### **Cloud Infrastructure**
- **Google Cloud Platform (GCP)**
  - Cloud Storage - Object storage for raw data and reports
  - Cloud Functions (2nd Gen) - Serverless compute for ETL and analytics
  - BigQuery - Columnar data warehouse (similar to Amazon Redshift)
  - Cloud Logging - Centralized logging and monitoring
  - IAM - Role-based access control

### **Data Engineering**
- **Python 3.10**
  - `pandas` - Data manipulation and transformation
  - `numpy` - Numerical operations (IQR outlier detection)
  - `google-cloud-bigquery` - BigQuery Python SDK
  - `google-cloud-storage` - GCS Python SDK
  - `pyarrow` - DataFrame serialization for BigQuery
  - `db-dtypes` - BigQuery data type handling

### **Data Warehouse**
- **BigQuery**
  - Star schema dimensional modeling
  - 3 dimension tables + 1 fact table
  - Optimized for analytical queries
  - Supports both DirectQuery and Import modes

### **Business Intelligence**
- **Power BI**
  - DirectQuery connection to BigQuery
  - DAX measures for calculated metrics
  - 12+ visualizations (cards, charts, tables, scatter plots)
  - Cross-filtering and interactive slicers
  - Published to Power BI Service with scheduled refresh

- **Looker Studio**
  - Google's native BI tool
  - Web-based collaborative dashboards
  - Real-time data connectivity
  - Mobile-responsive design

### **Analytics & Reporting**
- **SQL** - Complex analytical queries (JOINs, window functions, aggregations)
- **HTML/CSS** - Formatted report generation
- **JSON** - Structured data exports

---

##  Features

### **Automated ETL Pipeline**
- ✅ Event-driven architecture (Cloud Storage triggers)
- ✅ Schema validation on ingestion
- ✅ Data quality checks at multiple layers
- ✅ IQR-based outlier detection (removes 1.2% extreme values)
- ✅ Median imputation for missing values
- ✅ Star schema with proper foreign key relationships
- ✅ Idempotent operations (safe to retry)

**Data Quality Results:**
- Input: 1,000 raw records
- Output: 988 clean records (98.8% retention)
- Outliers removed: 12 (1.2%)
- Missing values imputed: 50 (5%)
- Processing time: 15-20 seconds

### **Analytics & Insights**
- ✅ 8 comprehensive SQL queries covering:
  - Summary statistics (totals, averages, ranges)
  - Monthly price trends and seasonality
  - Location-based performance analysis
  - Property type distribution and market share
  - Statistical correlations (price vs features)
  - Premium segment analysis (top 10 expensive)
  - Market segmentation by price brackets
  - Bedroom inventory distribution

### **Interactive Dashboards**

**Power BI Dashboard Features:**
-  **3 KPI Cards:** Total Listings, Average Price, Average Price/SqFt
-  **Line Chart:** Price trends over 6 months
-  **Bar Chart:** Listings distribution by city
-  **Pie Chart:** Property type composition
-  **Scatter Plot:** Price vs Square Footage (with trendline)
-  **Table:** Top 10 most expensive properties
-  **Funnel Chart:** Market segmentation by price brackets
-  **Matrix:** Bedroom distribution with metrics
-  **Slicers:** Date range, location, property type, bedrooms

**Looker Studio Dashboard Features:**
- Similar visualizations with Google's design language
- Shared collaboration features
- Embedded analytics capabilities

---

##  Project Structure

```
real-estate-analytics-gcp/
├── README.md                          # This file
├── .gitignore                         # Git exclusions
│
├── cloud-functions/
│   ├── etl-function/                  # ETL Pipeline
│   │   ├── main.py                    # Entry point & orchestration
│   │   ├── transform.py               # Data cleaning (200+ lines)
│   │   ├── load.py                    # BigQuery loading (200+ lines)
│   │   └── requirements.txt           # Python dependencies
│   │
│   └── analytics-function/            # Analytics Pipeline
│       ├── main.py                    # Report generation (400+ lines)
│       └── requirements.txt           # Python dependencies
│
├── sql/
│   ├── schema/
│   │   └── create_tables.sql          # BigQuery DDL
│   └── queries/
│       └── analytics_queries.sql      # 10 analytical queries
│
├── data/
│   └── sample/
│       ├── generate_data.py           # Synthetic data generator
│       └── real_estate_sample_data.csv # Test data (1000 records)
│
├── docs/
│   ├── PROJECT_PLAN.md                # Detailed documentation
│   ├── PROGRESS_LOG.md                # Development log
│   └── screenshots/
│       ├── powerbi/
│       │   ├── dashboard-overview.png
│       │   ├── location-analysis.png
│       │   └── property-analysis.png
│       └── looker/
│           └── dashboard.png
│
└── config/
    └── bucket-lifecycle.json          # GCS lifecycle policy
```

---

##  Setup & Deployment

### **Prerequisites**
- Google Cloud Platform account
- Python 3.10+
- gcloud CLI installed
- Power BI Desktop (for local development)

### **1. Clone Repository**
```bash
git clone https://github.com/YOUR-USERNAME/real-estate-analytics-gcp.git
cd real-estate-analytics-gcp
```

### **2. GCP Project Setup**
```bash
# Set project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
```

### **3. Create GCS Buckets**
```bash
# Landing bucket for raw data
gsutil mb -l us-central1 gs://${PROJECT_ID}-real-estate-landing

# Reports bucket
gsutil mb -l us-central1 gs://${PROJECT_ID}-real-estate-reports
```

### **4. Create BigQuery Dataset**
```bash
bq mk --location=US real_estate_dw
```

### **5. Deploy ETL Function**
```bash
cd cloud-functions/etl-function

gcloud functions deploy real-estate-etl-function \
  --gen2 \
  --runtime=python310 \
  --region=us-central1 \
  --source=. \
  --entry-point=process_csv \
  --trigger-bucket=${PROJECT_ID}-real-estate-landing \
  --set-env-vars PROJECT_ID=${PROJECT_ID},DATASET_ID=real_estate_dw \
  --memory=256MB \
  --timeout=60s
```

### **6. Deploy Analytics Function**
```bash
cd ../analytics-function

gcloud functions deploy real-estate-analytics-function \
  --gen2 \
  --runtime=python310 \
  --region=us-central1 \
  --source=. \
  --entry-point=generate_report \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars PROJECT_ID=${PROJECT_ID},DATASET_ID=real_estate_dw,REPORTS_BUCKET=${PROJECT_ID}-real-estate-reports \
  --memory=512MB \
  --timeout=120s
```

### **7. Test the Pipeline**
```bash
# Generate test data
cd ../../data/sample
python generate_data.py

# Upload to trigger pipeline
gsutil cp real_estate_sample_data.csv gs://${PROJECT_ID}-real-estate-landing/
```

### **8. Connect Power BI**

**Create service account for Power BI:**
```bash
gcloud iam service-accounts create powerbi-reader \
  --display-name="Power BI BigQuery Reader"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:powerbi-reader@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member="serviceAccount:powerbi-reader@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"
```

**In Power BI Desktop:**
1. Get Data → Google BigQuery
2. Authenticate with your Google account
3. Select project and dataset
4. Load tables (all 4)
5. Create visualizations
6. Publish to Power BI Service

---

##  Data Model

### **Star Schema Design**

```
           dim_date
          ┌─────────┐
          │ date_id │ PK
          │ full_date
          │ year
          │ month
          │ day_of_week
          └─────────┘
                ↑
                │
    ┌───────────┼───────────┐
    │           │           │
dim_location    │    dim_property_type
┌─────────┐    │    ┌──────────────┐
│location_id PK │    │property_type_id PK
│ city      │   │    │ type_name    │
│ state     │   │    └──────────────┘
└─────────┘    │           ↑
    ↑          │           │
    │          │           │
    │    fact_listings     │
    │   ┌──────────────┐   │
    └───┤ listing_id   │   │
        │ date_id      │───┘
        │ location_id  │
        │ property_type_id
        │ price        │
        │ bedrooms     │
        │ bathrooms    │
        │ sqft         │
        │ price_per_sqft
        └──────────────┘
```

**Fact Table:** 988 records  
**Dimensions:** 15 locations, 5 property types, 181 dates

---

##  Analytics Queries

The pipeline executes 8 comprehensive queries:

1. **Summary Statistics** - Totals, averages, min/max
2. **Monthly Trends** - Time series analysis
3. **Location Performance** - Geographic comparison
4. **Property Type Distribution** - Market composition
5. **Price Correlations** - Statistical relationships
6. **Premium Listings** - Top 10 expensive properties
7. **Bedroom Distribution** - Inventory segmentation
8. **Price Brackets** - Market segmentation (Budget to Ultra-Luxury)

**Sample Query:**
```sql
SELECT 
  l.city,
  COUNT(*) as listing_count,
  ROUND(AVG(f.price), 2) as avg_price,
  ROUND(AVG(f.price_per_sqft), 2) as avg_price_per_sqft
FROM `project.dataset.fact_listings` f
JOIN `project.dataset.dim_location` l ON f.location_id = l.location_id
GROUP BY l.city
ORDER BY avg_price DESC
```

---

##  Key Learning Outcomes

### **Data Engineering Skills**
- Event-driven ETL architecture
- Data quality management (validation, outlier detection, imputation)
- Dimensional modeling (star schema)
- Cloud data warehousing (BigQuery)
- Serverless computing (Cloud Functions)

### **Analytics Skills**
- Complex SQL queries (JOINs, aggregations, window functions)
- Statistical analysis (correlations, distributions)
- Business intelligence metrics
- Report automation

### **Visualization Skills**
- Power BI dashboard development
- DAX measures and calculated columns
- Interactive filtering and cross-filtering
- Looker Studio configuration

### **Cloud Engineering Skills**
- GCP service configuration
- IAM and security
- Cost optimization
- Infrastructure as code

---

##  Security & Governance

- **IAM:** Role-based access control for all GCP resources
- **Encryption:** Data encrypted at rest and in transit
- **Logging:** Comprehensive execution logs in Cloud Logging
- **Monitoring:** Function performance and error tracking
- **Cost Management:** Optimized for free tier usage (~$0/month for development)

---

##  Performance Metrics

| Metric | Value |
|--------|-------|
| Data Processed | 1,000 → 988 records |
| Data Quality Retention | 98.8% |
| Outliers Detected | 12 (1.2%) |
| Missing Values Handled | 50 (5%) |
| ETL Processing Time | 15-20 seconds |
| Analytics Execution | 10 seconds (8 queries) |
| End-to-End Latency | ~2 minutes |
| Storage Cost | <$0.01/month |
| Compute Cost (dev) | ~$0/month (free tier) |

---

##  Future Enhancements

- [ ] Incremental loading with CDC (Change Data Capture)
- [ ] Machine learning price prediction model (BigQuery ML)
- [ ] RESTful API for external data access
- [ ] Real-time streaming with Pub/Sub + Dataflow
- [ ] Data quality monitoring dashboard
- [ ] Airflow orchestration for complex workflows
- [ ] Multi-tenancy with row-level security
- [ ] Tableau/Qlik Sense integrations

---

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

##  Author

**Abhinandan Ajit Kumar**

- GitHub: [@YOUR-USERNAME](https://github.com/YOUR-USERNAME)
- Email: abhinandan19909@gmail.com
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/your-profile)
- Portfolio: [Your Website](https://yourwebsite.com)

---

##  Acknowledgments

- Built as a portfolio project demonstrating data engineering skills
- Designed with architecture patterns similar to Bayut/Dubizzle tech stack
- Uses GCP services analogous to AWS (BigQuery ≈ Redshift, Cloud Functions ≈ Lambda)
- Implements industry best practices for ETL and dimensional modeling

---

##  Contact

For questions or collaboration opportunities:
- Open an issue in this repository
- Email: abhinandan19909@gmail.com
- Connect on [LinkedIn](https://linkedin.com/in/your-profile)

---

** If you found this project helpful, please give it a star!**

```


