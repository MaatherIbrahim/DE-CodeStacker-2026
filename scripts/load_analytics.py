"""
Load analytics data - calculate total shipping spend per customer tier per month
"""
import psycopg2
from datetime import datetime
import os
def load_analytics_data():
    """
    Calculate and load final analytics: Total Shipping Spend per Customer Tier per Month
    """
    print("Starting analytics data load...")
    conn = None
    try:

        # Connect to database
        conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
        )
        cursor = conn.cursor()
    
        # Create analytics table if not exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics.shipping_spend_by_tier (
            tier VARCHAR(50),
            year_month VARCHAR(7),
            total_shipping_spend DECIMAL(12,2),
            shipment_count INTEGER,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    
        # Before the INSERT, clear the table to ensure a fresh summary
        cursor.execute("TRUNCATE TABLE analytics.shipping_spend_by_tier;")  





        # Calculate and load analytics
        cursor.execute("""
        INSERT INTO analytics.shipping_spend_by_tier (tier, year_month, total_shipping_spend, shipment_count)
        SELECT 
            COALESCE(tier, 'Unknown') as tier,
            TO_CHAR(shipment_date, 'YYYY-MM') as year_month,
            SUM(shipping_cost) as total_shipping_spend,
            COUNT(*) as shipment_count
        FROM staging.shipments_with_tiers
        GROUP BY tier, year_month
        ORDER BY year_month DESC, total_shipping_spend DESC;
        """)
    
        rows_inserted = cursor.rowcount
        print(f"Inserted {rows_inserted} rows into analytics table")
    
        conn.commit()
        print("analytics data load completed successfully.")
    except Exception as e:
        if conn:
            conn.rollback()
            print("ERROR: calculation failed. analytics table has been rolled back to its previous state.")    
            print(f"CRITICAL ERROR: {e}")
            raise e
    finally:
        if conn:
            cursor.close()
            conn.close()
    
            print("database connection closed.")
