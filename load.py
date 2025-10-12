from google.cloud import bigquery
import pandas as pd

def create_dimension_tables(df, client, project_id, dataset_id):
    """
    Create and populate dimension tables.
    Returns dict of dimension dataframes with IDs.
    """
    
    dim_tables = {}
    
    # 1. Location Dimension
    locations = df[['location']].drop_duplicates()
    locations['location_id'] = range(1, len(locations) + 1)
    
    # Parse location if format is "City, State" or just "City"
    locations[['city', 'state']] = locations['location'].str.split(',', n=1, expand=True)
    locations['city'] = locations['city'].str.strip()
    locations['state'] = locations['state'].str.strip() if 'state' in locations else None
    
    locations['created_at'] = pd.Timestamp.utcnow()
    
    # Load to BigQuery (or update if exists)
    table_id = f"{project_id}.{dataset_id}.dim_location"
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # Or WRITE_APPEND for incremental
    )
    
    job = client.load_table_from_dataframe(locations, table_id, job_config=job_config)
    job.result()
    print(f"Loaded {len(locations)} locations to dim_location")
    
    dim_tables['location'] = locations
    
    # 2. Property Type Dimension
    property_types = df[['property_type']].drop_duplicates()
    property_types['property_type_id'] = range(1, len(property_types) + 1)
    property_types['type_name'] = property_types['property_type']
    
    # Categorize property types
    def categorize_property(type_name):
        if 'apartment' in type_name.lower() or 'flat' in type_name.lower():
            return 'Residential-Apartment'
        elif 'villa' in type_name.lower() or 'house' in type_name.lower():
            return 'Residential-House'
        elif 'townhouse' in type_name.lower():
            return 'Residential-Townhouse'
        else:
            return 'Other'
    
    property_types['category'] = property_types['type_name'].apply(categorize_property)
    property_types['created_at'] = pd.Timestamp.utcnow()
    
    table_id = f"{project_id}.{dataset_id}.dim_property_type"
    job = client.load_table_from_dataframe(property_types, table_id, job_config=job_config)
    job.result()
    print(f"Loaded {len(property_types)} property types to dim_property_type")
    
    dim_tables['property_type'] = property_types
    
    # 3. Date Dimension (create for all dates in data)
    dates = pd.DataFrame({'full_date': pd.date_range(df['list_date'].min(), df['list_date'].max())})
    dates['date_id'] = dates['full_date'].dt.strftime('%Y%m%d').astype(int)
    dates['year'] = dates['full_date'].dt.year
    dates['month'] = dates['full_date'].dt.month
    dates['month_name'] = dates['full_date'].dt.strftime('%B')
    dates['quarter'] = dates['full_date'].dt.quarter
    dates['day_of_week'] = dates['full_date'].dt.dayofweek
    dates['day_name'] = dates['full_date'].dt.strftime('%A')
    dates['is_weekend'] = dates['day_of_week'].isin([5, 6])
    
    table_id = f"{project_id}.{dataset_id}.dim_date"
    job = client.load_table_from_dataframe(dates, table_id, job_config=job_config)
    job.result()
    print(f"Loaded {len(dates)} dates to dim_date")
    
    dim_tables['date'] = dates
    
    return dim_tables


def load_fact_table(df, dim_tables, client, project_id, dataset_id, source_file):
    """
    Load fact table by joining with dimension tables to get IDs.
    """
    
    # Merge with dimension tables to get IDs
    fact_df = df.copy()
    
    # Join with location dimension
    fact_df = fact_df.merge(
        dim_tables['location'][['location', 'location_id']],
        on='location',
        how='left'
    )
    
    # Join with property type dimension
    fact_df = fact_df.merge(
        dim_tables['property_type'][['property_type', 'property_type_id']],
        left_on='property_type',
        right_on='property_type',
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
    
    # Select final columns for fact table
    fact_columns = [
        'location_id', 'property_type_id', 'date_id',
        'list_date', 'price', 'bedrooms', 'bathrooms', 
        'sqft', 'price_per_sqft', 'created_at'
    ]
    
    fact_df = fact_df[fact_columns]
    
    # Generate listing_id
    fact_df['listing_id'] = range(1, len(fact_df) + 1)
    
    # Load to BigQuery
    table_id = f"{project_id}.{dataset_id}.fact_listings"
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",  # Append new data
    )
    
    job = client.load_table_from_dataframe(fact_df, table_id, job_config=job_config)
    job.result()
    
    print(f"Loaded {len(fact_df)} listings from {source_file} to fact_listings")
    
    return len(fact_df)