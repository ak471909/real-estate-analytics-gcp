"""
Real Estate Sample Data Generator

Generates realistic property listing data for testing the ETL pipeline.
Focus on UAE real estate market (Dubai, Abu Dhabi, Sharjah).
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

def generate_real_estate_data(num_records=1000):
    """
    Generate sample real estate listing data.
    
    Args:
        num_records: Number of listings to generate
        
    Returns:
        pandas DataFrame with realistic property data
    """
    
    print(f"🏗️  Generating {num_records} sample property listings...")
    
    # === LOCATIONS (UAE focused for Bayut/Dubizzle relevance) ===
    locations = [
        'Dubai Marina, Dubai',
        'Downtown Dubai, Dubai',
        'Jumeirah Beach Residence, Dubai',
        'Palm Jumeirah, Dubai',
        'Business Bay, Dubai',
        'Arabian Ranches, Dubai',
        'Dubai Silicon Oasis, Dubai',
        'International City, Dubai',
        'Al Reem Island, Abu Dhabi',
        'Al Raha Beach, Abu Dhabi',
        'Yas Island, Abu Dhabi',
        'Khalifa City, Abu Dhabi',
        'Al Majaz, Sharjah',
        'Al Khan, Sharjah',
        'Muwaileh, Sharjah',
    ]
    
    # Location weights (some areas more popular)
    location_weights = [0.15, 0.12, 0.10, 0.08, 0.09, 0.07, 0.06, 0.05,
                       0.08, 0.06, 0.04, 0.03, 0.03, 0.02, 0.02]
    
    # === PROPERTY TYPES ===
    property_types = ['Apartment', 'Villa', 'Townhouse', 'Penthouse', 'Studio']
    property_weights = [0.50, 0.25, 0.15, 0.05, 0.05]  # Apartments most common
    
    # === DATE RANGE (Last 6 months) ===
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    dates = pd.date_range(start=start_date, end=end_date, periods=num_records)
    
    # === GENERATE BASE DATA ===
    data = {
        'list_date': dates,
        'location': np.random.choice(locations, num_records, p=location_weights),
        'property_type': np.random.choice(property_types, num_records, p=property_weights),
        'bedrooms': np.random.choice([0, 1, 2, 3, 4, 5], num_records, 
                                     p=[0.05, 0.20, 0.35, 0.25, 0.10, 0.05]),
        'bathrooms': np.random.choice([1, 1.5, 2, 2.5, 3, 3.5, 4], num_records,
                                      p=[0.10, 0.10, 0.35, 0.15, 0.20, 0.05, 0.05]),
    }
    
    # === GENERATE SQUARE FOOTAGE (based on property type) ===
    sqft_by_type = {
        'Studio': (350, 600),
        'Apartment': (600, 2000),
        'Townhouse': (1500, 3000),
        'Villa': (2500, 8000),
        'Penthouse': (2000, 6000)
    }
    
    sqft_list = []
    for prop_type, beds in zip(data['property_type'], data['bedrooms']):
        min_sqft, max_sqft = sqft_by_type[prop_type]
        # Adjust for bedrooms
        if beds == 0:  # Studio
            sqft = np.random.normal(450, 100)
        elif beds == 1:
            sqft = np.random.normal(700, 150)
        elif beds == 2:
            sqft = np.random.normal(1100, 200)
        elif beds == 3:
            sqft = np.random.normal(1600, 300)
        elif beds == 4:
            sqft = np.random.normal(2500, 500)
        else:  # 5+
            sqft = np.random.normal(3500, 700)
        
        # Ensure within property type bounds
        sqft = np.clip(sqft, min_sqft, max_sqft)
        sqft_list.append(int(sqft))
    
    data['sqft'] = sqft_list
    
    # === GENERATE REALISTIC PRICES ===
    base_prices = {
        'Studio': 350000,
        'Apartment': 700000,
        'Townhouse': 1500000,
        'Villa': 2500000,
        'Penthouse': 3500000
    }
    
    # Location price multipliers (premium areas cost more)
    location_multipliers = {
        'Dubai Marina': 1.3,
        'Downtown Dubai': 1.4,
        'Jumeirah Beach Residence': 1.3,
        'Palm Jumeirah': 1.5,
        'Business Bay': 1.2,
        'Arabian Ranches': 1.1,
        'Dubai Silicon Oasis': 0.9,
        'International City': 0.7,
        'Al Reem Island': 1.2,
        'Al Raha Beach': 1.1,
        'Yas Island': 1.2,
        'Khalifa City': 0.9,
        'Al Majaz': 0.8,
        'Al Khan': 0.8,
        'Muwaileh': 0.7,
    }
    
    prices = []
    for prop_type, location, beds, sqft in zip(data['property_type'], 
                                                 data['location'], 
                                                 data['bedrooms'], 
                                                 data['sqft']):
        # Base price
        base = base_prices[prop_type]
        
        # Adjust for bedrooms
        base += beds * 120000
        
        # Adjust for size
        base += (sqft - 1000) * 250
        
        # Location multiplier
        city = location.split(',')[0].strip()
        multiplier = location_multipliers.get(city, 1.0)
        price = base * multiplier
        
        # Add randomness (±10%)
        price *= np.random.uniform(0.90, 1.10)
        
        # Ensure minimum price
        price = max(200000, price)
        
        # Round to nearest 5000
        price = round(price / 5000) * 5000
        
        prices.append(price)
    
    data['price'] = prices
    
    # === ADD LISTING STATUS ===
    data['listing_status'] = np.random.choice(
        ['Active', 'Pending', 'Sold'],
        num_records,
        p=[0.70, 0.20, 0.10]
    )
    
    # === CREATE DATAFRAME ===
    df = pd.DataFrame(data)
    
    # === ADD SOME REALISTIC MISSING VALUES (5%) ===
    missing_indices = np.random.choice(df.index, size=int(num_records * 0.05), replace=False)
    missing_columns = np.random.choice(['bathrooms', 'sqft'], size=len(missing_indices))
    
    for idx, col in zip(missing_indices, missing_columns):
        df.loc[idx, col] = np.nan
    
    # === ADD SOME OUTLIERS (2%) for testing outlier removal ===
    outlier_indices = np.random.choice(df.index, size=int(num_records * 0.02), replace=False)
    for idx in outlier_indices:
        df.loc[idx, 'price'] = df.loc[idx, 'price'] * np.random.uniform(3.0, 5.0)
    
    print(f"✅ Generated {len(df)} listings")
    print(f"   Date range: {df['list_date'].min().date()} to {df['list_date'].max().date()}")
    print(f"   Price range: ${df['price'].min():,.0f} - ${df['price'].max():,.0f}")
    print(f"   Locations: {df['location'].nunique()} unique")
    print(f"   Property types: {df['property_type'].nunique()} types")
    print(f"   Missing values: {df.isna().sum().sum()} cells ({df.isna().sum().sum() / df.size * 100:.1f}%)")
    
    return df


def main():
    """Main function to generate and save sample data."""
    
    print("=" * 70)
    print("REAL ESTATE SAMPLE DATA GENERATOR")
    print("=" * 70)
    print()
    
    # Generate data
    df = generate_real_estate_data(num_records=1000)
    
    # Display sample
    print("\n📊 Sample Records:")
    print(df.head(10).to_string())
    
    print("\n📈 Data Summary:")
    print(df.describe())
    
    # Save to CSV
    output_file = 'real_estate_sample_data.csv'
    df.to_csv(output_file, index=False)
    print(f"\n💾 Saved to: {output_file}")
    print(f"   File size: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    
    print("\n" + "=" * 70)
    print("✅ GENERATION COMPLETE!")
    print(f"   Ready to upload to GCS bucket for testing")
    print("=" * 70)


if __name__ == "__main__":
    main()