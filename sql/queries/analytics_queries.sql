-- sqlfluff:disable
-- This file uses Python string formatting with {project} and {dataset} placeholders
-- VSCode SQL linter will show false errors - ignore them


-- ============================================================
-- REAL ESTATE ANALYTICS QUERIES
-- Data Source: BigQuery Data Warehouse (real_estate_dw)
-- Purpose: Business intelligence and market insights
-- ============================================================

-- Query 1: Monthly Price Trends
-- Shows average prices and listing volumes by month
-- Use Case: Identify seasonal patterns, market growth

SELECT 
    d.year,
    d.month,
    d.month_name,
    COUNT(*) as listing_count,
    ROUND(AVG(f.price), 2) as avg_price,
    ROUND(AVG(f.price_per_sqft), 2) as avg_price_per_sqft,
    ROUND(MIN(f.price), 2) as min_price,
    ROUND(MAX(f.price), 2) as max_price,
    ROUND(STDDEV(f.price), 2) as price_std_dev
FROM `{project}.{dataset}.fact_listings` f
JOIN `{project}.{dataset}.dim_date` d ON f.date_id = d.date_id
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year DESC, d.month DESC;


-- Query 2: Location Performance Analysis
-- Compare different neighborhoods/cities by key metrics
-- Use Case: Identify premium vs budget markets

SELECT 
    l.city,
    l.state,
    COUNT(*) as listing_count,
    ROUND(AVG(f.price), 2) as avg_price,
    ROUND(AVG(f.bedrooms), 1) as avg_bedrooms,
    ROUND(AVG(f.sqft), 0) as avg_sqft,
    ROUND(AVG(f.price_per_sqft), 2) as avg_price_per_sqft,
    ROUND(MIN(f.price), 2) as min_price,
    ROUND(MAX(f.price), 2) as max_price
FROM `{project}.{dataset}.fact_listings` f
JOIN `{project}.{dataset}.dim_location` l ON f.location_id = l.location_id
GROUP BY l.city, l.state
ORDER BY avg_price DESC;


-- Query 3: Property Type Distribution & Analysis
-- Analyze different property types and their characteristics
-- Use Case: Understand product mix and pricing by type

SELECT 
    pt.type_name,
    pt.category,
    COUNT(*) as listing_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as pct_of_total,
    ROUND(AVG(f.price), 2) as avg_price,
    ROUND(AVG(f.bedrooms), 1) as avg_bedrooms,
    ROUND(AVG(f.sqft), 0) as avg_sqft,
    ROUND(AVG(f.price_per_sqft), 2) as avg_price_per_sqft,
    -- Luxury vs Standard count
    SUM(CASE WHEN f.price > 2000000 THEN 1 ELSE 0 END) as luxury_count,
    SUM(CASE WHEN f.price <= 2000000 THEN 1 ELSE 0 END) as standard_count
FROM `{project}.{dataset}.fact_listings` f
JOIN `{project}.{dataset}.dim_property_type` pt ON f.property_type_id = pt.property_type_id
GROUP BY pt.type_name, pt.category
ORDER BY listing_count DESC;


-- Query 4: Price Correlation Analysis
-- Statistical correlations between price and property attributes
-- Use Case: Understand what drives property values

SELECT 
    ROUND(CORR(price, sqft), 4) as price_sqft_correlation,
    ROUND(CORR(price, bedrooms), 4) as price_bedrooms_correlation,
    ROUND(CORR(price, bathrooms), 4) as price_bathrooms_correlation,
    ROUND(CORR(sqft, bedrooms), 4) as sqft_bedrooms_correlation,
    ROUND(CORR(price_per_sqft, sqft), 4) as price_per_sqft_size_correlation
FROM `{project}.{dataset}.fact_listings`;


-- Query 5: Top 10 Most Expensive Listings
-- Identify premium properties in the market
-- Use Case: Luxury segment analysis

SELECT 
    f.listing_id,
    l.city,
    pt.type_name,
    f.bedrooms,
    f.bathrooms,
    f.sqft,
    ROUND(f.price, 2) as price,
    ROUND(f.price_per_sqft, 2) as price_per_sqft,
    f.list_date
FROM `{project}.{dataset}.fact_listings` f
JOIN `{project}.{dataset}.dim_location` l ON f.location_id = l.location_id
JOIN `{project}.{dataset}.dim_property_type` pt ON f.property_type_id = pt.property_type_id
ORDER BY f.price DESC
LIMIT 10;


-- Query 6: Bottom 10 Most Affordable Listings  
-- Identify budget-friendly properties
-- Use Case: Entry-level market analysis

SELECT 
    f.listing_id,
    l.city,
    pt.type_name,
    f.bedrooms,
    f.bathrooms,
    f.sqft,
    ROUND(f.price, 2) as price,
    ROUND(f.price_per_sqft, 2) as price_per_sqft,
    f.list_date
FROM `{project}.{dataset}.fact_listings` f
JOIN `{project}.{dataset}.dim_location` l ON f.location_id = l.location_id
JOIN `{project}.{dataset}.dim_property_type` pt ON f.property_type_id = pt.property_type_id
ORDER BY f.price ASC
LIMIT 10;


-- Query 7: Bedroom Distribution Analysis
-- Analyze inventory by bedroom count
-- Use Case: Understand product mix and demand patterns

SELECT 
    f.bedrooms,
    COUNT(*) as listing_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as pct_of_total,
    ROUND(AVG(f.price), 2) as avg_price,
    ROUND(AVG(f.sqft), 0) as avg_sqft,
    ROUND(AVG(f.price_per_sqft), 2) as avg_price_per_sqft,
    ROUND(MIN(f.price), 2) as min_price,
    ROUND(MAX(f.price), 2) as max_price
FROM `{project}.{dataset}.fact_listings` f
GROUP BY f.bedrooms
ORDER BY f.bedrooms;


-- Query 8: Weekly Activity Patterns
-- Analyze listing activity by day of week
-- Use Case: Identify optimal listing days

SELECT 
    d.day_name,
    d.day_of_week,
    d.is_weekend,
    COUNT(*) as listing_count,
    ROUND(AVG(f.price), 2) as avg_price,
    ROUND(AVG(f.price_per_sqft), 2) as avg_price_per_sqft
FROM `{project}.{dataset}.fact_listings` f
JOIN `{project}.{dataset}.dim_date` d ON f.date_id = d.date_id
GROUP BY d.day_name, d.day_of_week, d.is_weekend
ORDER BY d.day_of_week;


-- Query 9: Price Range Distribution
-- Categorize listings into price brackets
-- Use Case: Market segmentation analysis

SELECT 
    CASE 
        WHEN price < 500000 THEN 'Budget (<500K)'
        WHEN price >= 500000 AND price < 1000000 THEN 'Mid-Range (500K-1M)'
        WHEN price >= 1000000 AND price < 2000000 THEN 'Premium (1M-2M)'
        WHEN price >= 2000000 AND price < 5000000 THEN 'Luxury (2M-5M)'
        ELSE 'Ultra-Luxury (5M+)'
    END as price_bracket,
    COUNT(*) as listing_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as pct_of_total,
    ROUND(AVG(price), 2) as avg_price,
    ROUND(AVG(sqft), 0) as avg_sqft,
    ROUND(AVG(bedrooms), 1) as avg_bedrooms
FROM `{project}.{dataset}.fact_listings`
GROUP BY price_bracket
ORDER BY 
    CASE 
        WHEN price_bracket = 'Budget (<500K)' THEN 1
        WHEN price_bracket = 'Mid-Range (500K-1M)' THEN 2
        WHEN price_bracket = 'Premium (1M-2M)' THEN 3
        WHEN price_bracket = 'Luxury (2M-5M)' THEN 4
        ELSE 5
    END;


-- Query 10: Location-Type Performance Matrix
-- Cross-analysis of location and property type
-- Use Case: Identify best-performing combinations

SELECT 
    l.city,
    pt.type_name,
    COUNT(*) as listing_count,
    ROUND(AVG(f.price), 2) as avg_price,
    ROUND(AVG(f.price_per_sqft), 2) as avg_price_per_sqft
FROM `{project}.{dataset}.fact_listings` f
JOIN `{project}.{dataset}.dim_location` l ON f.location_id = l.location_id
JOIN `{project}.{dataset}.dim_property_type` pt ON f.property_type_id = pt.property_type_id
GROUP BY l.city, pt.type_name
HAVING COUNT(*) >= 3  -- Only show combinations with 3+ listings
ORDER BY avg_price DESC
LIMIT 20;