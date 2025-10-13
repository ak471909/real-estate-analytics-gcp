CREATE TABLE `real-estate-analytics-474906.real_estate_dw.dim_location` (
  location_id INT64 NOT NULL,
  city STRING,
  state STRING,
  zip_code STRING,
  region STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) OPTIONS(
  description="Location dimension table - stores unique locations"
);

CREATE TABLE `real-estate-analytics-474906.real_estate_dw.dim_property_type` (
  property_type_id INT64 NOT NULL,
  type_name STRING NOT NULL,
  category STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
) OPTIONS(
  description="Property type dimension table - Apartment, Villa, etc"
);

CREATE TABLE `real-estate-analytics-474906.real_estate_dw.dim_date` (
  date_id INT64 NOT NULL,
  full_date DATE NOT NULL,
  year INT64,
  month INT64,
  month_name STRING,
  quarter INT64,
  day_of_week INT64,
  day_name STRING,
  is_weekend BOOL
) OPTIONS(
  description="Date dimension table for time-based analysis"
);

CREATE TABLE `real-estate-analytics-474906.real_estate_dw.fact_listings` (
  listing_id INT64 NOT NULL,
  location_id INT64,
  property_type_id INT64,
  date_id INT64,
  
  list_date DATE,
  listing_status STRING,
  
  price FLOAT64,
  bedrooms INT64,
  bathrooms FLOAT64,
  sqft INT64,
  lot_size INT64,
  
  price_per_sqft FLOAT64,
  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP
) OPTIONS(
  description="Fact table - main listings transaction table"
);