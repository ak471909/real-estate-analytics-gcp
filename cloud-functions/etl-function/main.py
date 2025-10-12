import functions_framework
from google.cloud import storage, bigquery
import pandas as pd
import io
import os
from datetime import datetime

# Import our helper modules (we'll create these next)
from transform import normalize_dataframe
from load import create_dimension_tables, load_fact_table

# Initialize GCP clients
storage_client = storage.Client()
bigquery_client = bigquery.Client()

# Get environment variables
PROJECT_ID = os.environ.get('PROJECT_ID')
DATASET_ID = os.environ.get('DATASET_ID')


@functions_framework.cloud_event
def process_csv(cloud_event):
    """
    Main entry point - triggered by Cloud Storage event.
    
    This function is automatically called when a file is uploaded
    to the landing bucket.
    
    Args:
        cloud_event: Cloud Storage event containing file metadata
    """
    
    print("=" * 60)
    print("ETL FUNCTION TRIGGERED")
    print("=" * 60)
    
    # === STEP 1: EXTRACT - Get file information from event ===
    data = cloud_event.data
    bucket_name = data['bucket']
    file_name = data['name']
    
    print(f"📁 Bucket: {bucket_name}")
    print(f"📄 File: {file_name}")
    
    # Validate file type
    if not file_name.lower().endswith('.csv'):
        print(f"⚠️  Skipping non-CSV file: {file_name}")
        return 'Not a CSV file', 200
    
    try:
        # === STEP 2: EXTRACT - Download and read CSV ===
        print("\n--- EXTRACTION PHASE ---")
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        
        # Download file content
        content = blob.download_as_text()
        print(f"✅ Downloaded file: {len(content)} characters")
        
        # Read CSV into DataFrame
        df = pd.read_csv(io.StringIO(content))
        print(f"✅ Loaded CSV into DataFrame: {len(df)} rows, {len(df.columns)} columns")
        print(f"   Columns: {list(df.columns)}")
        
        # Validate required columns
        required_columns = ['list_date', 'location', 'property_type', 'price', 'bedrooms', 'bathrooms', 'sqft']
        missing_columns = set(required_columns) - set(df.columns)
        
        if missing_columns:
            error_msg = f"❌ Missing required columns: {missing_columns}"
            print(error_msg)
            raise ValueError(error_msg)
        
        print(f"✅ Schema validation passed")
        
        # === STEP 3: TRANSFORM - Clean and normalize data ===
        print("\n--- TRANSFORMATION PHASE ---")
        normalized_df = normalize_dataframe(df)
        print(f"✅ Data normalized: {len(normalized_df)} rows (removed {len(df) - len(normalized_df)} invalid rows)")
        
        # === STEP 4: LOAD - Insert into BigQuery ===
        print("\n--- LOADING PHASE ---")
        
        # Create/update dimension tables
        dim_tables = create_dimension_tables(
            normalized_df, 
            bigquery_client, 
            PROJECT_ID, 
            DATASET_ID
        )
        print(f"✅ Dimension tables updated")
        
        # Load fact table
        rows_loaded = load_fact_table(
            normalized_df,
            dim_tables,
            bigquery_client,
            PROJECT_ID,
            DATASET_ID,
            file_name
        )
        print(f"✅ Loaded {rows_loaded} rows to fact_listings")
        
        # === SUCCESS ===
        print("\n" + "=" * 60)
        print(f"✅ SUCCESS: Processed {file_name}")
        print(f"   Total rows loaded: {rows_loaded}")
        print("=" * 60)
        
        return 'Success', 200
        
    except Exception as e:
        # === ERROR HANDLING ===
        print("\n" + "=" * 60)
        print(f"❌ ERROR processing {file_name}")
        print(f"   Error: {str(e)}")
        print("=" * 60)
        raise e