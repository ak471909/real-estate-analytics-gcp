import pandas as pd
import numpy as np
from datetime import datetime


def normalize_dataframe(df):
    """
    Transform and normalize raw real estate data.
    
    This function:
    1. Validates and standardizes data types
    2. Handles missing values
    3. Removes outliers
    4. Calculates derived fields
    5. Creates dimension keys for joining
    
    Args:
        df: Raw pandas DataFrame from CSV
        
    Returns:
        Normalized pandas DataFrame ready for loading
    """
    
    print("🔧 Starting data transformation...")
    
    # Create a copy to avoid modifying original
    df = df.copy()
    original_rows = len(df)
    
    # === STEP 1: Date Standardization ===
    print("  📅 Standardizing dates...")
    df['list_date'] = pd.to_datetime(df['list_date'], errors='coerce')
    
    # Remove rows with invalid dates
    invalid_dates = df['list_date'].isna().sum()
    if invalid_dates > 0:
        print(f"     ⚠️  Removing {invalid_dates} rows with invalid dates")
        df = df.dropna(subset=['list_date'])
    
    # === STEP 2: Handle Missing Values ===
    print("  🔍 Handling missing values...")
    
    # Numeric columns - use median imputation
    numeric_columns = ['price', 'sqft', 'bedrooms', 'bathrooms']
    for col in numeric_columns:
        if col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)
                print(f"     ℹ️  Filled {missing_count} missing values in {col} with median: {median_val}")
    
    # Categorical columns - use 'Unknown' or mode
    df['location'].fillna('Unknown', inplace=True)
    df['property_type'].fillna('Unknown', inplace=True)
    
    # === STEP 3: Standardize Text Formats ===
    print("  ✏️  Standardizing text formats...")
    df['location'] = df['location'].str.strip().str.title()
    df['property_type'] = df['property_type'].str.strip().str.title()
    
    # === STEP 4: Data Type Conversions ===
    print("  🔢 Converting data types...")
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['sqft'] = pd.to_numeric(df['sqft'], errors='coerce')
    df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce').astype('Int64')
    df['bathrooms'] = pd.to_numeric(df['bathrooms'], errors='coerce')
    
    # Remove rows where critical numeric fields are invalid
    critical_fields = ['price', 'sqft']
    df = df.dropna(subset=critical_fields)
    
    # === STEP 5: Remove Outliers (IQR Method for Price) ===
    print("  📊 Removing outliers...")
    Q1 = df['price'].quantile(0.25)
    Q3 = df['price'].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers_mask = (df['price'] < lower_bound) | (df['price'] > upper_bound)
    outliers_count = outliers_mask.sum()
    
    if outliers_count > 0:
        print(f"     ⚠️  Removing {outliers_count} price outliers")
        print(f"        Price range: ${lower_bound:,.0f} - ${upper_bound:,.0f}")
        df = df[~outliers_mask]
    
    # Also ensure reasonable minimums
    df = df[df['price'] > 0]
    df = df[df['sqft'] > 0]
    df = df[df['bedrooms'] >= 0]
    df = df[df['bathrooms'] > 0]
    
    # === STEP 6: Calculate Derived Fields ===
    print("  🧮 Calculating derived fields...")
    df['price_per_sqft'] = (df['price'] / df['sqft']).round(2)
    
    # === STEP 7: Create Dimension Keys ===
    print("  🔑 Creating dimension keys...")
    
    # Location key (will be replaced with actual IDs during load)
    df['location_key'] = df['location'].astype(str)
    
    # Property type key
    df['property_type_key'] = df['property_type'].astype(str)
    
    # Date key (format: YYYYMMDD as integer)
    df['date_key'] = df['list_date'].dt.strftime('%Y%m%d').astype(int)
    
    # === STEP 8: Add Metadata ===
    df['created_at'] = datetime.utcnow()
    df['updated_at'] = datetime.utcnow()
    
    # Add listing_status if not present
    if 'listing_status' not in df.columns:
        df['listing_status'] = 'Active'
    
    # Add lot_size if not present
    if 'lot_size' not in df.columns:
        df['lot_size'] = None
    
    # === STEP 9: Final Validation ===
    final_rows = len(df)
    rows_removed = original_rows - final_rows
    removal_pct = (rows_removed / original_rows * 100) if original_rows > 0 else 0
    
    print(f"\n  ✅ Transformation complete:")
    print(f"     Original rows: {original_rows}")
    print(f"     Final rows: {final_rows}")
    print(f"     Removed: {rows_removed} ({removal_pct:.1f}%)")
    
    # Ensure we have data left
    if final_rows == 0:
        raise ValueError("⚠️  All rows were filtered out during transformation!")
    
    return df