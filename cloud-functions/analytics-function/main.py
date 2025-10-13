import functions_framework
from google.cloud import bigquery, storage
import os
import json
from datetime import datetime
import pandas as pd

# Initialize clients
bigquery_client = bigquery.Client()
storage_client = storage.Client()

# Get environment variables
PROJECT_ID = os.environ.get('PROJECT_ID')
DATASET_ID = os.environ.get('DATASET_ID')
REPORTS_BUCKET = os.environ.get('REPORTS_BUCKET')


@functions_framework.http
def generate_report(request):
    """
    Generate comprehensive analytics report from BigQuery data.
    
    Triggered via HTTP request (manual or scheduled).
    Executes analytical queries and generates formatted reports.
    
    Returns:
        JSON response with report URLs and status
    """
    
    print("=" * 70)
    print("ANALYTICS REPORT GENERATION STARTED")
    print("=" * 70)
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print(f"Reports Bucket: {REPORTS_BUCKET}")
    
    try:
        # Execute all analytical queries
        print("\n--- EXECUTING QUERIES ---")
        results = execute_analytical_queries()
        
        # Generate timestamp for file naming
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        
        # Generate HTML report
        print("\n--- GENERATING HTML REPORT ---")
        html_report = generate_html_report(results, timestamp)
        html_filename = f"reports/analytics_report_{timestamp}.html"
        
        # Upload HTML to GCS
        bucket = storage_client.bucket(REPORTS_BUCKET)
        html_blob = bucket.blob(html_filename)
        html_blob.upload_from_string(html_report, content_type='text/html')
        print(f"✅ HTML report saved: gs://{REPORTS_BUCKET}/{html_filename}")
        
        # Generate JSON report (structured data)
        print("\n--- GENERATING JSON REPORT ---")
        json_report = {
            'generated_at': timestamp,
            'project_id': PROJECT_ID,
            'dataset_id': DATASET_ID,
            'total_queries': len(results),
            'results': results
        }
        
        json_filename = f"reports/analytics_data_{timestamp}.json"
        json_blob = bucket.blob(json_filename)
        json_blob.upload_from_string(
            json.dumps(json_report, indent=2, default=str),
            content_type='application/json'
        )
        print(f"✅ JSON report saved: gs://{REPORTS_BUCKET}/{json_filename}")
        
        # Success response
        print("\n" + "=" * 70)
        print("✅ ANALYTICS REPORT GENERATION COMPLETE")
        print("=" * 70)
        
        return {
            'status': 'success',
            'timestamp': timestamp,
            'html_report': f"gs://{REPORTS_BUCKET}/{html_filename}",
            'json_report': f"gs://{REPORTS_BUCKET}/{json_filename}",
            'queries_executed': len(results),
            'public_html_url': f"https://storage.googleapis.com/{REPORTS_BUCKET}/{html_filename}"
        }, 200
        
    except Exception as e:
        print("\n" + "=" * 70)
        print(f"❌ ERROR: {str(e)}")
        print("=" * 70)
        return {
            'status': 'error',
            'error': str(e)
        }, 500


def execute_analytical_queries():
    """
    Execute all analytical queries against BigQuery.
    
    Returns:
        dict: Dictionary of query results
    """
    
    # Define all analytical queries
    queries = {
        'summary_stats': f"""
            SELECT 
                COUNT(*) as total_listings,
                ROUND(AVG(price), 2) as avg_price,
                ROUND(MIN(price), 2) as min_price,
                ROUND(MAX(price), 2) as max_price,
                ROUND(AVG(price_per_sqft), 2) as avg_price_per_sqft,
                ROUND(AVG(sqft), 0) as avg_sqft,
                ROUND(AVG(bedrooms), 1) as avg_bedrooms
            FROM `{PROJECT_ID}.{DATASET_ID}.fact_listings`
        """,
        
        'monthly_trends': f"""
            SELECT 
                d.year,
                d.month,
                d.month_name,
                COUNT(*) as listing_count,
                ROUND(AVG(f.price), 2) as avg_price,
                ROUND(AVG(f.price_per_sqft), 2) as avg_price_per_sqft
            FROM `{PROJECT_ID}.{DATASET_ID}.fact_listings` f
            JOIN `{PROJECT_ID}.{DATASET_ID}.dim_date` d ON f.date_id = d.date_id
            GROUP BY d.year, d.month, d.month_name
            ORDER BY d.year DESC, d.month DESC
        """,
        
        'location_analysis': f"""
            SELECT 
                l.city,
                COUNT(*) as listing_count,
                ROUND(AVG(f.price), 2) as avg_price,
                ROUND(AVG(f.bedrooms), 1) as avg_bedrooms,
                ROUND(AVG(f.sqft), 0) as avg_sqft,
                ROUND(AVG(f.price_per_sqft), 2) as avg_price_per_sqft
            FROM `{PROJECT_ID}.{DATASET_ID}.fact_listings` f
            JOIN `{PROJECT_ID}.{DATASET_ID}.dim_location` l ON f.location_id = l.location_id
            GROUP BY l.city
            ORDER BY avg_price DESC
        """,
        
        'property_type_distribution': f"""
            SELECT 
                pt.type_name,
                COUNT(*) as listing_count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as pct_of_total,
                ROUND(AVG(f.price), 2) as avg_price,
                ROUND(AVG(f.bedrooms), 1) as avg_bedrooms
            FROM `{PROJECT_ID}.{DATASET_ID}.fact_listings` f
            JOIN `{PROJECT_ID}.{DATASET_ID}.dim_property_type` pt ON f.property_type_id = pt.property_type_id
            GROUP BY pt.type_name
            ORDER BY listing_count DESC
        """,
        
        'price_correlations': f"""
            SELECT 
                ROUND(CORR(price, sqft), 4) as price_sqft_correlation,
                ROUND(CORR(price, bedrooms), 4) as price_bedrooms_correlation,
                ROUND(CORR(price, bathrooms), 4) as price_bathrooms_correlation
            FROM `{PROJECT_ID}.{DATASET_ID}.fact_listings`
        """,
        
        'top_10_expensive': f"""
            SELECT 
                f.listing_id,
                l.city,
                pt.type_name,
                f.bedrooms,
                f.bathrooms,
                f.sqft,
                ROUND(f.price, 2) as price,
                ROUND(f.price_per_sqft, 2) as price_per_sqft
            FROM `{PROJECT_ID}.{DATASET_ID}.fact_listings` f
            JOIN `{PROJECT_ID}.{DATASET_ID}.dim_location` l ON f.location_id = l.location_id
            JOIN `{PROJECT_ID}.{DATASET_ID}.dim_property_type` pt ON f.property_type_id = pt.property_type_id
            ORDER BY f.price DESC
            LIMIT 10
        """,
        
        'bedroom_distribution': f"""
            SELECT 
                f.bedrooms,
                COUNT(*) as listing_count,
                ROUND(AVG(f.price), 2) as avg_price,
                ROUND(AVG(f.sqft), 0) as avg_sqft
            FROM `{PROJECT_ID}.{DATASET_ID}.fact_listings` f
            GROUP BY f.bedrooms
            ORDER BY f.bedrooms
        """,
        
        'price_brackets': f"""
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
                ROUND(AVG(price), 2) as avg_price
            FROM `{PROJECT_ID}.{DATASET_ID}.fact_listings`
            GROUP BY price_bracket
            ORDER BY 
                CASE 
                    WHEN price_bracket = 'Budget (<500K)' THEN 1
                    WHEN price_bracket = 'Mid-Range (500K-1M)' THEN 2
                    WHEN price_bracket = 'Premium (1M-2M)' THEN 3
                    WHEN price_bracket = 'Luxury (2M-5M)' THEN 4
                    ELSE 5
                END
        """
    }
    
    # Execute each query and store results
    results = {}
    
    for query_name, query in queries.items():
        try:
            print(f"  ⏳ Executing: {query_name}...")
            query_job = bigquery_client.query(query)
            df = query_job.to_dataframe()
            
            # Convert DataFrame to list of dicts for JSON serialization
            results[query_name] = df.to_dict(orient='records')
            print(f"  ✅ {query_name}: {len(df)} rows")
            
        except Exception as e:
            print(f"  ❌ Error in {query_name}: {str(e)}")
            results[query_name] = {'error': str(e)}
    
    return results


def generate_html_report(results, timestamp):
    """
    Generate formatted HTML report from query results.
    
    Args:
        results: Dictionary of query results
        timestamp: Report generation timestamp
        
    Returns:
        str: HTML report content
    """
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Real Estate Analytics Report</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                color: #333;
            }}
            .container {{ 
                max-width: 1200px; 
                margin: 0 auto; 
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                overflow: hidden;
            }}
            .header {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                padding: 40px 30px;
                text-align: center;
            }}
            .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
            .header p {{ font-size: 1.1em; opacity: 0.9; }}
            .content {{ padding: 40px 30px; }}
            .section {{ 
                background: #f8f9fa; 
                margin: 30px 0; 
                padding: 25px; 
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }}
            .section h2 {{ 
                color: #667eea; 
                margin-bottom: 20px; 
                font-size: 1.8em;
                border-bottom: 2px solid #e9ecef;
                padding-bottom: 10px;
            }}
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                margin: 15px 0;
                background: white;
                border-radius: 8px;
                overflow: hidden;
            }}
            th {{ 
                background: #667eea; 
                color: white; 
                padding: 15px; 
                text-align: left;
                font-weight: 600;
            }}
            td {{ 
                padding: 12px 15px; 
                border-bottom: 1px solid #e9ecef;
            }}
            tr:hover {{ background: #f8f9fa; }}
            tr:last-child td {{ border-bottom: none; }}
            .metric-card {{
                display: inline-block;
                background: white;
                padding: 20px;
                margin: 10px;
                border-radius: 8px;
                border: 2px solid #e9ecef;
                min-width: 150px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .metric-card .value {{ 
                font-size: 2em; 
                font-weight: bold; 
                color: #667eea;
                margin: 10px 0;
            }}
            .metric-card .label {{ 
                font-size: 0.9em; 
                color: #6c757d;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #6c757d;
                font-size: 0.9em;
            }}
            .no-data {{ 
                color: #dc3545; 
                font-style: italic; 
                padding: 20px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏠 Real Estate Analytics Report</h1>
                <p>Generated: {datetime.strptime(timestamp, '%Y%m%d_%H%M%S').strftime('%B %d, %Y at %H:%M UTC')}</p>
                <p>Data Source: BigQuery Data Warehouse</p>
            </div>
            
            <div class="content">
    """
    
    # Summary Statistics
    if 'summary_stats' in results and results['summary_stats']:
        stats = results['summary_stats'][0]
        html += """
            <div class="section">
                <h2>📊 Summary Statistics</h2>
                <div style="text-align: center;">
        """
        
        metrics = [
            ('total_listings', 'Total Listings', ''),
            ('avg_price', 'Average Price', '$'),
            ('avg_price_per_sqft', 'Avg Price/SqFt', '$'),
            ('avg_sqft', 'Avg Square Feet', ''),
            ('avg_bedrooms', 'Avg Bedrooms', '')
        ]
        
        for key, label, prefix in metrics:
            value = stats.get(key, 0)
            formatted_value = f"{prefix}{value:,.0f}" if prefix else f"{value:,.1f}"
            html += f"""
                <div class="metric-card">
                    <div class="label">{label}</div>
                    <div class="value">{formatted_value}</div>
                </div>
            """
        
        html += "</div></div>"
    
    # Monthly Trends
    if 'monthly_trends' in results and results['monthly_trends']:
        html += """
            <div class="section">
                <h2>📈 Monthly Trends</h2>
                <table>
                    <tr>
                        <th>Month</th>
                        <th>Listings</th>
                        <th>Avg Price</th>
                        <th>Avg Price/SqFt</th>
                    </tr>
        """
        for row in results['monthly_trends']:
            html += f"""
                <tr>
                    <td>{row['month_name']} {row['year']}</td>
                    <td>{row['listing_count']:,}</td>
                    <td>${row['avg_price']:,.0f}</td>
                    <td>${row['avg_price_per_sqft']:,.2f}</td>
                </tr>
            """
        html += "</table></div>"
    
    # Location Analysis
    if 'location_analysis' in results and results['location_analysis']:
        html += """
            <div class="section">
                <h2>📍 Location Performance</h2>
                <table>
                    <tr>
                        <th>City</th>
                        <th>Listings</th>
                        <th>Avg Price</th>
                        <th>Avg Bedrooms</th>
                        <th>Avg SqFt</th>
                        <th>Avg Price/SqFt</th>
                    </tr>
        """
        for row in results['location_analysis']:
            html += f"""
                <tr>
                    <td>{row['city']}</td>
                    <td>{row['listing_count']:,}</td>
                    <td>${row['avg_price']:,.0f}</td>
                    <td>{row['avg_bedrooms']:.1f}</td>
                    <td>{row['avg_sqft']:,.0f}</td>
                    <td>${row['avg_price_per_sqft']:,.2f}</td>
                </tr>
            """
        html += "</table></div>"
    
    # Property Type Distribution
    if 'property_type_distribution' in results and results['property_type_distribution']:
        html += """
            <div class="section">
                <h2>🏘️ Property Type Distribution</h2>
                <table>
                    <tr>
                        <th>Type</th>
                        <th>Listings</th>
                        <th>% of Total</th>
                        <th>Avg Price</th>
                        <th>Avg Bedrooms</th>
                    </tr>
        """
        for row in results['property_type_distribution']:
            html += f"""
                <tr>
                    <td>{row['type_name']}</td>
                    <td>{row['listing_count']:,}</td>
                    <td>{row['pct_of_total']:.1f}%</td>
                    <td>${row['avg_price']:,.0f}</td>
                    <td>{row['avg_bedrooms']:.1f}</td>
                </tr>
            """
        html += "</table></div>"
    
    # Price Correlations
    if 'price_correlations' in results and results['price_correlations']:
        corr = results['price_correlations'][0]
        html += f"""
            <div class="section">
                <h2>📊 Price Correlation Analysis</h2>
                <p style="margin: 15px 0; line-height: 1.8;">
                    <strong>Price vs Square Footage:</strong> {corr['price_sqft_correlation']:.4f}<br>
                    <strong>Price vs Bedrooms:</strong> {corr['price_bedrooms_correlation']:.4f}<br>
                    <strong>Price vs Bathrooms:</strong> {corr['price_bathrooms_correlation']:.4f}
                </p>
                <p style="font-size: 0.9em; color: #6c757d; margin-top: 15px;">
                    <em>Note: Correlation ranges from -1 to 1. Values closer to 1 indicate strong positive correlation.</em>
                </p>
            </div>
        """
    
    # Top 10 Expensive
    if 'top_10_expensive' in results and results['top_10_expensive']:
        html += """
            <div class="section">
                <h2>💎 Top 10 Most Expensive Listings</h2>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>City</th>
                        <th>Type</th>
                        <th>Bedrooms</th>
                        <th>SqFt</th>
                        <th>Price</th>
                        <th>Price/SqFt</th>
                    </tr>
        """
        for row in results['top_10_expensive']:
            html += f"""
                <tr>
                    <td>{row['listing_id']}</td>
                    <td>{row['city']}</td>
                    <td>{row['type_name']}</td>
                    <td>{row['bedrooms']}</td>
                    <td>{row['sqft']:,}</td>
                    <td>${row['price']:,.0f}</td>
                    <td>${row['price_per_sqft']:,.2f}</td>
                </tr>
            """
        html += "</table></div>"
    
    # Price Brackets
    if 'price_brackets' in results and results['price_brackets']:
        html += """
            <div class="section">
                <h2>💰 Market Segmentation by Price</h2>
                <table>
                    <tr>
                        <th>Price Bracket</th>
                        <th>Listings</th>
                        <th>% of Total</th>
                        <th>Avg Price</th>
                    </tr>
        """
        for row in results['price_brackets']:
            html += f"""
                <tr>
                    <td>{row['price_bracket']}</td>
                    <td>{row['listing_count']:,}</td>
                    <td>{row['pct_of_total']:.1f}%</td>
                    <td>${row['avg_price']:,.0f}</td>
                </tr>
            """
        html += "</table></div>"
    
    # Bedroom Distribution
    if 'bedroom_distribution' in results and results['bedroom_distribution']:
        html += """
            <div class="section">
                <h2>🛏️ Inventory by Bedroom Count</h2>
                <table>
                    <tr>
                        <th>Bedrooms</th>
                        <th>Listings</th>
                        <th>Avg Price</th>
                        <th>Avg SqFt</th>
                    </tr>
        """
        for row in results['bedroom_distribution']:
            bedrooms_label = f"{row['bedrooms']} BR" if row['bedrooms'] > 0 else "Studio"
            html += f"""
                <tr>
                    <td>{bedrooms_label}</td>
                    <td>{row['listing_count']:,}</td>
                    <td>${row['avg_price']:,.0f}</td>
                    <td>{row['avg_sqft']:,.0f}</td>
                </tr>
            """
        html += "</table></div>"
    
    # Footer
    html += f"""
            </div>
            <div class="footer">
                <p>Real Estate Analytics Pipeline | Powered by Google Cloud Platform</p>
                <p>BigQuery Data Warehouse | Cloud Functions | Cloud Storage</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html