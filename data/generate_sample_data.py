import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

# Generate 1000 sample listings
n = 1000

# Date range (last 6 months)
end_date = datetime.now()
start_date = end_date - timedelta(days=180)
dates = pd.date_range(start=start_date, end=end_date, periods=n)

# Locations (Dubai focus for Dubizzle relevance)
locations = [
    'Dubai Marina, Dubai',
    'Downtown Dubai, Dubai',
    'Jumeirah Beach Residence, Dubai',
    'Palm Jumeirah, Dubai',
    'Business Bay, Dubai',
    'Arabian Ranches, Dubai',
    'Dubai Silicon Oasis, Dubai',
    'Abu Dhabi Marina, Abu Dhabi',
    'Al Reem Island, Abu Dhabi',
    'Sharjah Waterfront, Sharjah'
]

# Property types
property_types = ['Apartment', 'Villa', 'Townhouse', 'Penthouse', 'Studio']

# Generate data
data = {
    'listing_id': range(1, n+1),
    'list_date': dates,
    'location': np.random.choice(locations, n),
    'property_type': np.random.choice(
        property_types, 
        n, 
        p=[0.5, 0.25, 0.15, 0.05, 0.05]  # Apartments most common
    ),
    'bedrooms': np.random.choice([0, 1, 2, 3, 4, 5], n, p=[0.05, 0.2, 0.35, 0.25, 0.1, 0.05]),
    'bathrooms': np.random.choice([1, 1.5, 2, 2.5, 3, 4], n, p=[0.15, 0.1, 0.35, 0.15, 0.2, 0.05]),
    'sqft': np.random.normal(1200, 400, n).clip(400, 5000).astype(int),
}

# Generate realistic prices based on property characteristics
base_prices = {
    'Studio': 400000,
    'Apartment': 600000,
    'Townhouse': 1200000,
    'Villa': 2000000,
    'Penthouse': 3000000
}

prices = []
for ptype, beds, sqft in zip(data['property_type'], data['bedrooms'], data['sqft']):
    base = base_prices[ptype]
    # Adjust for bedrooms
    price = base + (beds * 150000)
    # Adjust for size
    price += (sqft - 1000) * 300
    # Add some randomness
    price *= np.random.uniform(0.9, 1.1)
    prices.append(max(200000, price))  # Minimum 200k

data['price'] = np.array(prices).round(-3)  # Round to nearest 1000

# Create DataFrame
df = pd.DataFrame(data)

# Add some missing values for realism (5% missing)
missing_indices = np.random.choice(df.index, size=int(n*0.05), replace=False)
df.loc[missing_indices, 'bathrooms'] = np.nan

# Save
df.to_csv('data/sample/real_estate_listings.csv', index=False)
print(f"Generated {n} sample listings")
print(df.head(10))
print("\nData Summary:")
print(df.describe())