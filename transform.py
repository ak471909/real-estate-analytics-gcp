import pandas as pd
import numpy as np
from datetime import datetime

def normalize_dataframe(df):
    """
    Clean and normalize raw real estate data.
    
    Steps:
    1. Validate required columns
    2. Handle missing values
    3. Standardize formats
    4. Calculate derived fields
    5. Remove outliers
    6. Create dimension keys
    """
    
    # Required columns
    required_cols = ['price', 'bedrooms', 'bathrooms', 'sqft', 'location', 'property_type', 'list_date']
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Create a copy
    df = df.copy()
    
    # 1. Date standardization
    df['list_date'] = pd.to_datetime(df['list_date'], errors='coerce')
    df = df.dropna(subset=['list_date'])  # Remove invalid dates
    
    # 2. Handle missing values
    # Numeric columns - use median
    df['price'].fillna(df['price'].median(), inplace=True)
    df['sqft'].fillna(df['sqft'].median(), inplace=True)
    df['bedrooms'].fillna(df['bedrooms'].mode()[0], inplace=True)
    df['bathrooms'].fillna(df['bathrooms'].median(), inplace=True)
    
    # Categorical - use mode or 'Unknown'
    df['location'].fillna('Unknown', inplace=True)
    df['property_type'].fillna('Unknown', inplace=True)
    
    # 3. Standardize formats
    df['location'] = df['location'].str.title().str.strip()
    df['property_type'] = df['property_type'].str.title().str.strip()
    
    # 4. Remove outliers (IQR method for price)
    Q1 = df['price'].quantile(0.25)
    Q3 = df['price'].quantile(0.75)
    IQR = Q3 - Q1
    df = df[~((df['price'] < (Q1 - 1.5 * IQR)) | (df['price'] > (Q3 + 1.5 * IQR)))]
    
    # 5. Calculate derived fields
    df['price_per_sqft'] = df['price'] / df['sqft']
    df['price_per_sqft'] = df['price_per_sqft'].round(2)
    
    # 6. Create dimension keys (will be replaced with actual IDs during load)
    # These are temporary for grouping
    df['location_key'] = df['location'].astype(str)
    df['property_type_key'] = df['property_type'].astype(str)
    df['date_key'] = df['list_date'].dt.strftime('%Y%m%d').astype(int)
    
    # 7. Add metadata
    df['created_at'] = datetime.utcnow()
    
    return df