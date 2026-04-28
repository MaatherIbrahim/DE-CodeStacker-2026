import psycopg2
import os

def transform_shipment_data():
    """
    Clean data from raw_data and move to staging.
    Logic: Filters out duplicates, nulls, negative costs, and shipments for unknown customers.
    """
    print("Cleaning data and moving to STAGING...")
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", 5432)
        )
        cursor = conn.cursor()

        # 1. CLEAN CUSTOMER TIERS (Dimension Table)
        cursor.execute("DROP TABLE IF EXISTS staging.customer_tiers CASCADE;")
        cursor.execute("""
            CREATE TABLE staging.customer_tiers (
                customer_id VARCHAR(50) PRIMARY KEY,
                customer_name VARCHAR(200),
                tier VARCHAR(50)
            );
        """)
        cursor.execute("""
            INSERT INTO staging.customer_tiers (customer_id, customer_name, tier)
            SELECT DISTINCT ON (customer_id) 
                customer_id, customer_name, tier
            FROM raw_data.customer_tiers
            WHERE customer_id IS NOT NULL
            ORDER BY customer_id;
        """)

        # 2. CLEAN SHIPMENTS (Fact Table)
        # Note: We now filter out any customer_id that is NOT in our staging.customer_tiers table.
        cursor.execute("DROP TABLE IF EXISTS staging.shipments CASCADE;")
        cursor.execute("""
            CREATE TABLE staging.shipments (
                shipment_id VARCHAR(50) PRIMARY KEY,
                customer_id VARCHAR(50) REFERENCES staging.customer_tiers(customer_id),
                shipping_cost DECIMAL(10,2),
                shipment_date DATE,
                status VARCHAR(50)
            );
        """)
        cursor.execute("""
            INSERT INTO staging.shipments (shipment_id, customer_id, shipping_cost, shipment_date, status)
            SELECT DISTINCT ON (shipment_id)
                shipment_id, customer_id, shipping_cost, shipment_date, status 
            FROM raw_data.shipments
            WHERE customer_id IS NOT NULL 
              AND shipping_cost > 0
              AND customer_id IN (SELECT customer_id FROM staging.customer_tiers) -- DELETE/SKIP unknowns
            ORDER BY shipment_id, extracted_at DESC;
        """)

        # 3. CREATE FINAL JOINED TABLE FOR ANALYTICS
        cursor.execute("DROP TABLE IF EXISTS staging.shipments_with_tiers;")
        cursor.execute("""
            CREATE TABLE staging.shipments_with_tiers AS
            SELECT s.*, t.tier, t.customer_name
            FROM staging.shipments s
            INNER JOIN staging.customer_tiers t ON s.customer_id = t.customer_id;
        """)

        conn.commit()
        print("Staging transformation completed successfully. Unknown customers removed.")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"CRITICAL ERROR IN TRANSFORMATION: {e}")
        raise e
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Database connection closed.")