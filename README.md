# 🏠 Real Estate Analytics Pipeline

**An event-driven ETL pipeline for real estate listing analytics using Google Cloud Platform**

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/downloads/)
[![GCP](https://img.shields.io/badge/GCP-Cloud%20Functions-orange.svg)](https://cloud.google.com/functions)
[![BigQuery](https://img.shields.io/badge/BigQuery-Data%20Warehouse-green.svg)](https://cloud.google.com/bigquery)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Sample Data](#sample-data)
- [Analytics & Insights](#analytics--insights)
- [Dashboard](#dashboard)
- [Cost](#cost)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## 🎯 Overview

This project implements a **fully automated, event-driven data pipeline** for analyzing real estate listings. Built using Google Cloud Platform's managed services, it demonstrates modern data engineering practices including:

- **Serverless ETL** processing with Cloud Functions
- **Star schema** data warehouse design in BigQuery
- **Event-driven architecture** using Cloud Storage triggers
- **Automated analytics** and report generation
- **Interactive dashboards** with Looker Studio

### Why This Project?

Created to demonstrate skills relevant to **Data Engineer roles** at companies like Bayut, Dubizzle, and other real estate/classifieds platforms. The architecture mirrors production systems using:
- Matillion-style ETL patterns
- Amazon Redshift-equivalent data warehousing (BigQuery)
- S3 + Lambda-style event processing (GCS + Cloud Functions)

---

## 🏗️ Architecture

```
┌─────────────────┐
│   CSV Upload    │
│  (GCS Bucket)   │
└────────┬────────┘
         │ Storage Event Trigger
         ▼
┌─────────────────────────┐
│   Cloud Function: ETL   │
│  ┌──────────────────┐   │
│  │ 1. Validate      │   │
│  │ 2. Transform     │   │
│  │ 3. Normalize     │   │
│  └──────────────────┘   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│          BigQuery: Star Schema          │
│  ┌──────────┐  ┌──────────┐            │
│  │ dim_     │  │ dim_     │            │
│  │ location │  │ property │            │
│  └────┬─────┘  └────┬─────┘            │
│       │             │                   │
│       │    ┌────────┴────────┐         │
│       └────│ fact_listings   │         │
│            │  - price         │         │
│            │  - bedrooms      │         │
│            │  - sqft          │         │
│            └─────────────────┘         │
└────────┬────────────────────────────────┘
         │ Query Execution
         ▼
┌──────────────────────────────┐
│ Cloud Function: Analytics    │
│  - Monthly trends            │
│  - Location analysis         │
│  - Property distribution     │
│  - Price correlations        │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────┐
│    Presentation Layer        │
│  - HTML Reports (GCS)        │
│  - JSON Data (GCS)           │
│  - Looker Studio Dashboard   │
└──────────────────────────────┘
```

### Architecture Highlights

- **Event-Driven:** Automatic processing when files are uploaded
- **Serverless:** No infrastructure management required
- **Scalable:** Handles increasing data volumes automatically
- **Cost-Effective:** Runs on GCP free tier (~$0/month for development)

---

## ✨ Features

### ETL Pipeline
- ✅ Automated CSV ingestion from Cloud Storage
- ✅ Data validation (schema, data types, required fields)
- ✅ Data transformation and normalization
- ✅ Missing value handling
- ✅ Outlier detection and removal
- ✅ Derived field calculation (price per sqft)
- ✅ Star schema dimensional modeling

### Analytics
- ✅ Monthly price trend analysis
- ✅ Location-based performance metrics
- ✅ Property type distribution analysis
- ✅ Price correlation studies
- ✅ Top/bottom performers identification
- ✅ Statistical summaries

### Reporting
- ✅ Automated HTML report generation
- ✅ JSON data exports
- ✅ Interactive Looker Studio dashboards
- ✅ Visual data storytelling

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Cloud Platform** | Google Cloud Platform | Infrastructure |
| **Storage** | Cloud Storage (GCS) | Raw data & reports |
| **Compute** | Cloud Functions | Serverless ETL processing |
| **Data Warehouse** | BigQuery | Structured data storage |
| **Language** | Python 3.10 | ETL logic & transformations |
| **Data Processing** | Pandas, NumPy | Data manipulation |
| **Visualization** | Looker Studio | Interactive dashboards |
| **Version Control** | Git/GitHub | Code management |

### Python Libraries
- `google-cloud-storage` - GCS operations
- `google-cloud-bigquery` - BigQuery operations
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `functions-framework` - Cloud Functions local testing

---

## 📁 Project Structure

```
real-estate-analytics-gcp/
│
├── README.md                          # This file
├── .gitignore                         # Git ignore rules
│
├── cloud-functions/
│   ├── etl-function/                  # ETL Cloud Function
│   │   ├── main.py                    # Entry point (process_csv)
│   │   ├── transform.py               # Data transformation logic
│   │   ├── load.py                    # BigQuery loading logic
│   │   ├── requirements.txt           # Python dependencies
│   │   └── README.md                  # Deployment instructions
│   │
│   └── analytics-function/            # Analytics Cloud Function
│       ├── main.py                    # Entry point (generate_report)
│       ├── requirements.txt           # Python dependencies
│       └── README.md                  # Deployment instructions
│
├── sql/
│   ├── schema/                        # Table definitions
│   │   └── create_tables.sql          # BigQuery schema DDL
│   └── queries/                       # Analytical queries
│       └── analytics_queries.sql      # All analysis queries
│
├── data/
│   ├── sample/                        # Sample data (committed)
│   │   ├── generate_data.py           # Data generation script
│   │   └── sample_listings.csv        # Example dataset
│   └── raw/                           # Raw uploads (gitignored)
│
├── docs/
│   ├── PROJECT_PLAN.md                # Complete project documentation
│   ├── PROGRESS_LOG.md                # Session-by-session progress
│   ├── architecture/                  # Architecture diagrams
│   ├── screenshots/                   # Dashboard screenshots
│   └── setup/                         # Setup guides
│
└── config/
    └── bucket-lifecycle.json          # GCS lifecycle configuration
```

---

## 🚀 Getting Started

### Prerequisites

1. **GCP Account** with billing enabled (free tier eligible)
2. **gcloud CLI** installed and configured
3. **Python 3.10+** installed locally
4. **Git** for version control

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/YOUR-USERNAME/real-estate-analytics-gcp.git
cd real-estate-analytics-gcp
```

#### 2. Set Up GCP Project
```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

#### 3. Create Cloud Storage Buckets
```bash
# Landing bucket (for CSV uploads)
gsutil mb -l us-central1 gs://${PROJECT_ID}-real-estate-landing

# Reports bucket (for outputs)
gsutil mb -l us-central1 gs://${PROJECT_ID}-real-estate-reports
```

#### 4. Create BigQuery Dataset
```bash
bq mk --dataset --location=us-central1 ${PROJECT_ID}:real_estate_dw
```

#### 5. Create BigQuery Tables
```bash
bq query --use_legacy_sql=false < sql/schema/create_tables.sql
```

#### 6. Deploy Cloud Functions

**ETL Function:**
```bash
cd cloud-functions/etl-function

gcloud functions deploy real-estate-etl-function \
  --runtime python310 \
  --trigger-resource ${PROJECT_ID}-real-estate-landing \
  --trigger-event google.storage.object.finalize \
  --entry-point process_csv \
  --memory 256MB \
  --timeout 60s \
  --region us-central1 \
  --set-env-vars PROJECT_ID=${PROJECT_ID},DATASET_ID=real_estate_dw
```

**Analytics Function:**
```bash
cd ../analytics-function

gcloud functions deploy real-estate-analytics-function \
  --runtime python310 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point generate_report \
  --memory 512MB \
  --timeout 120s \
  --region us-central1 \
  --set-env-vars PROJECT_ID=${PROJECT_ID},DATASET_ID=real_estate_dw,REPORTS_BUCKET=${PROJECT_ID}-real-estate-reports
```

---

## 💡 Usage

### Upload Data

**Option 1: Via GCS Console**
1. Go to [GCS Console](https://console.cloud.google.com/storage)
2. Navigate to `{project-id}-real-estate-landing` bucket
3. Click "Upload Files"
4. Select your CSV file
5. ETL function will trigger automatically

**Option 2: Via Command Line**
```bash
gsutil cp data/sample/sample_listings.csv gs://${PROJECT_ID}-real-estate-landing/
```

### Generate Analytics Report

**Trigger via HTTP:**
```bash
curl https://us-central1-${PROJECT_ID}.cloudfunctions.net/real-estate-analytics-function
```

**Or via GCP Console:**
1. Go to Cloud Functions
2. Click on `real-estate-analytics-function`
3. Go to "Testing" tab
4. Click "Test the function"

### View Results

**BigQuery Data:**
```bash
# View fact table
bq query --use_legacy_sql=false \
  'SELECT * FROM `'${PROJECT_ID}'.real_estate_dw.fact_listings` LIMIT 10'
```

**Reports:**
- Navigate to `{project-id}-real-estate-reports` bucket
- Download HTML or JSON files

**Dashboard:**
- Open Looker Studio
- Connect to BigQuery dataset
- [Link to live dashboard - to be added]

---

## 📊 Sample Data

The `data/sample/` directory contains a script to generate realistic real estate data:

```bash
cd data/sample
python generate_data.py
```

**Generated Data Includes:**
- 1,000 property listings
- 10 locations (Dubai, Abu Dhabi, Sharjah)
- 5 property types (Apartment, Villa, Townhouse, Penthouse, Studio)
- Price range: $200K - $5M
- 6-month date range

---

## 📈 Analytics & Insights

The pipeline generates the following analytical insights:

### 1. Monthly Trends
- Average prices by month
- Listing volume trends
- Seasonal patterns

### 2. Location Analysis
- Top performing cities
- Price per sqft by location
- Inventory distribution

### 3. Property Type Distribution
- Apartment vs Villa vs Townhouse metrics
- Price ranges by type
- Size (sqft) distributions

### 4. Price Correlations
- Price vs Square Footage
- Price vs Bedrooms
- Size vs Bedrooms

### 5. Top Performers
- Most expensive listings
- Best value properties (price per sqft)
- Fastest moving inventory

---

## 📱 Dashboard

[Screenshot to be added]

**Interactive Features:**
- Date range filters
- Location drill-down
- Property type selection
- Price range sliders
- Dynamic charts and graphs

**Live Dashboard:** [Link to be added]

---

## 💰 Cost

**Development/Testing:** ~$0/month (free tier)

| Service | Free Tier | Typical Usage | Cost |
|---------|-----------|---------------|------|
| Cloud Storage | 5GB | ~100MB | $0 |
| Cloud Functions | 2M invocations | ~100/month | $0 |
| BigQuery | 10GB + 1TB queries | 5GB + 100GB | $0 |

**Production Scale:** ~$10-50/month depending on data volume

---

## 🚧 Future Enhancements

- [ ] Add Cloud Scheduler for automated daily reports
- [ ] Implement incremental loading (CDC)
- [ ] Add data quality monitoring
- [ ] Create API endpoints for external access
- [ ] Add machine learning price predictions
- [ ] Implement alerting for anomalies
- [ ] Add support for multiple data sources
- [ ] Create mobile-friendly dashboard

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Contact

**Your Name**
- GitHub: [@your-username](https://github.com/your-username)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/your-profile)
- Email: your.email@example.com

**Project Link:** [https://github.com/your-username/real-estate-analytics-gcp](https://github.com/your-username/real-estate-analytics-gcp)

---

## 🙏 Acknowledgments

- Built for demonstration of data engineering skills for Bayut & Dubizzle
- Inspired by production data lake architectures
- GCP documentation and best practices
- Real estate data analysis patterns

---

**⭐ If you found this project helpful, please consider giving it a star!**
```

---

