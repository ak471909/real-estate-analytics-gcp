from google.cloud import bigquery
import pandas as pd
from datetime import datetime


def create_dimension_tables(df, client, project_id, dataset_id):
    """
    Create and populate dimension tables from normalized data.
    
    This function:
    1. Extracts unique dimension values
    2. Assigns IDs to each dimension record
    3. Loads/updates dimension tables in BigQuery
    4. Returns dimension dataframes with IDs for fact table joins
    
    Args:
        df: Normalized DataFrame
        client: BigQuery client
        project_id: GCP project ID
        dataset_id: BigQuery dataset ID
        
    Returns:
        dict: Dictionary of dimension DataFrames with IDs
    """
    
    dim_tables = {}
    
    # === DIMENSION 1: LOCATION ===
    print("  📍 Processing location dimension...")
    
    # Get unique locations
    locations = df[['location']].drop_duplicates().copy()
    
    # Parse location (format: "City, State" or just "City")
    if locations['location'].str.contains(',').any():
        locations[['city', 'state']] = locations['location'].str.split(',', n=1, expand=True)
        locations['city'] = locations['city'].str.strip()
        locations['state'] = locations['state'].str.strip()
    else:
        locations['city'] = locations['location']
        locations['state'] = None
    
    # Add default values
    locations['zip_code'] = None
    locations['region'] = 'UAE'  # Default for real estate data
    locations['created_at'] = datetime.utcnow()
    
    # Assign IDs
    locations['location_id'] = range(1, len(locations) + 1)
    
    # Select final columns
    locations = locations[['location_id', 'location', 'city', 'state', 'zip_code', 'region', 'created_at']]
    
    # Load to BigQuery
    table_id = f"{project_id}.{dataset_id}.dim_location"
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # Replace existing data
    )
    
    job = client.load_table_from_dataframe(locations, table_id, job_config=job_config)
    job.result()  # Wait for job to complete
    
    print(f"     ✅ Loaded {len(locations)} locations")
    dim_tables['location'] = locations
    
    
    # === DIMENSION 2: PROPERTY TYPE ===
    print("  🏠 Processing property type dimension...")
    
    # Get unique property types
    property_types = df[['property_type']].drop_duplicates().copy()
    property_types['type_name'] = property_types['property_type']
    
    # Categorize property types
    def categorize_property(type_name):
        """Categorize property into broader groups"""
        type_lower = type_name.lower()
        if 'apartment' in type_lower or 'flat' in type_lower or 'studio' in type_lower:
            return 'Residential-Apartment'
        elif 'villa' in type_lower or 'house' in type_lower:
            return 'Residential-House'
        elif 'townhouse' in type_lower:
            return 'Residential-Townhouse'
        elif 'penthouse' in type_lower:
            return 'Residential-Luxury'
        else:
            return 'Other'
    
    property_types['category'] = property_types['type_name'].apply(categorize_property)
    property_types['created_at'] = datetime.utcnow()
    
    # Assign IDs
    property_types['property_type_id'] = range(1, len(property_types) + 1)
    
    # Select final columns
    property_types = property_types[['property_type_id', 'property_type', 'type_name', 'category', 'created_at']]
    
    # Load to BigQuery
    table_id = f"{project_id}.{dataset_id}.dim_property_type"
    job = client.load_table_from_dataframe(property_types, table_id, job_config=job_config)
    job.result()
    
    print(f"     ✅ Loaded {len(property_types)} property types")
    dim_tables['property_type'] = property_types
    
    
    # === DIMENSION 3: DATE ===
    print("  📅 Processing date dimension...")
    
    # Create date range from data
    min_date = df['list_date'].min()
    max_date = df['list_date'].max()
    
    dates = pd.DataFrame({
        'full_date': pd.date_range(start=min_date, end=max_date, freq='D')
    })
    
    # Extract date components
    dates['date_id'] = dates['full_date'].dt.strftime('%Y%m%d').astype(int)
    dates['year'] = dates['full_date'].dt.year
    dates['month'] = dates['full_date'].dt.month
    dates['month_name'] = dates['full_date'].dt.strftime('%B')
    dates['quarter'] = dates['full_date'].dt.quarter
    dates['day_of_week'] = dates['full_date'].dt.dayofweek
    dates['day_name'] = dates['full_date'].dt.strftime('%A')
    dates['is_weekend'] = dates['day_of_week'].isin([5, 6])
    
    # Load to BigQuery
    table_id = f"{project_id}.{dataset_id}.dim_date"
    job = client.load_table_from_dataframe(dates, table_id, job_config=job_config)
    job.result()
    
    print(f"     ✅ Loaded {len(dates)} dates ({min_date.date()} to {max_date.date()})")
    dim_tables['date'] = dates
    
    return dim_tables


def load_fact_table(df, dim_tables, client, project_id, dataset_id, source_file):
    """
    Load fact table by joining with dimension tables to get foreign keys.
    
    Args:
        df: Normalized DataFrame with data
        dim_tables: Dictionary of dimension DataFrames with IDs
        client: BigQuery client
        project_id: GCP project ID
        dataset_id: BigQuery dataset ID
        source_file: Name of source CSV file (for logging)
        
    Returns:
        int: Number of rows loaded
    """
    
    print("  📊 Loading fact table...")
    
    # Start with normalized data
    fact_df = df.copy()
    
    # === JOIN WITH DIMENSIONS TO GET FOREIGN KEYS ===
    
    # Join with location dimension
    fact_df = fact_df.merge(
        dim_tables['location'][['location', 'location_id']],
        on='location',
        how='left'
    )
    
    # Join with property type dimension
    fact_df = fact_df.merge(
        dim_tables['property_type'][['property_type', 'property_type_id']],
        on='property_type',
        how='left'
    )
    
    # Join with date dimension
    fact_df['date_key'] = fact_df['list_date'].dt.strftime('%Y%m%d').astype(int)
    fact_df = fact_df.merge(
        dim_tables['date'][['date_id']],
        left_on='date_key',
        right_on='date_id',
        how='left'
    )
    
    # === SELECT FINAL COLUMNS FOR FACT TABLE ===
    fact_columns = [
        'location_id',
        'property_type_id', 
        'date_id',
        'list_date',
        'listing_status',
        'price',
        'bedrooms',
        'bathrooms',
        'sqft',
        'lot_size',
        'price_per_sqft',
        'created_at',
        'updated_at'
    ]
    
    fact_df = fact_df[fact_columns]
    
    # Generate unique listing_id (simple sequential for now)
    # In production, you'd use UUID or fetch max ID from existing data
    fact_df['listing_id'] = range(1, len(fact_df) + 1)
    
    # === LOAD TO BIGQUERY ===
    table_id = f"{project_id}.{dataset_id}.fact_listings"
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",  # Append new data
    )
    
    job = client.load_table_from_dataframe(fact_df, table_id, job_config=job_config)
    job.result()  # Wait for completion
    
    rows_loaded = len(fact_df)
    print(f"     ✅ Loaded {rows_loaded} listings from {source_file}")
    
    return rows_loaded