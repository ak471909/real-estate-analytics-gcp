import functions_framework
from google.cloud import storage, bigquery
import pandas as pd
from transform import normalize_dataframe
from load import create_dimension_tables, load_fact_table
import os

# Initialize clients
storage_client = storage.Client()
bigquery_client = bigquery.Client()

PROJECT_ID = os.environ.get('PROJECT_ID')
DATASET_ID = os.environ.get('DATASET_ID')

@functions_framework.cloud_event
def process_csv(cloud_event):
    """
    Triggered by Cloud Storage event when CSV is uploaded.
    
    Process:
    1. Extract: Download and validate CSV
    2. Transform: Clean, normalize, create keys
    3. Load: Insert into BigQuery star schema
    """
    
    # Get event data
    data = cloud_event.data
    bucket_name = data['bucket']
    file_name = data['name']
    
    print(f"Processing file: {file_name} from bucket: {bucket_name}")
    
    # Validation
    if not file_name.endswith('.csv'):
        print(f"Skipping non-CSV file: {file_name}")
        return
    
    try:
        # EXTRACT
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)
        
        # Download to memory
        content = blob.download_as_text()
        df = pd.read_csv(io.StringIO(content))
        
        print(f"Loaded CSV with {len(df)} rows")
        
        # TRANSFORM
        normalized_df = normalize_dataframe(df)
        print(f"Normalized data: {len(normalized_df)} rows")
        
        # LOAD
        # First ensure dimension tables exist and are populated
        dim_tables = create_dimension_tables(normalized_df, bigquery_client, PROJECT_ID, DATASET_ID)
        
        # Then load fact table
        load_fact_table(normalized_df, dim_tables, bigquery_client, PROJECT_ID, DATASET_ID, file_name)
        
        print(f"Successfully processed {file_name}")
        return 'Success', 200
        
    except Exception as e:
        print(f"Error processing {file_name}: {str(e)}")
        raise e