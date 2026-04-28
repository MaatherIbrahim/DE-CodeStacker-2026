import pandas as pd
import psycopg2
import os

def extract_customer_tiers_from_csv():
    print("Starting RAW customer tier extraction...")
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
        
        df = pd.read_csv(os.getenv("csv_path"))
        
        cursor.execute("DROP TABLE IF EXISTS raw_data.customer_tiers;")
        cursor.execute("""
            CREATE TABLE raw_data.customer_tiers (
                customer_id VARCHAR(50),
                customer_name VARCHAR(200),
                tier VARCHAR(50),
                tier_updated_date DATE
            );
        """)
        
        for _, row in df.iterrows():
            cursor.execute("""
                INSERT INTO raw_data.customer_tiers (customer_id, customer_name, tier, tier_updated_date)
                VALUES (%s, %s, %s, %s);
            """, (row['customer_id'], row['customer_name'], row['tier'], row['tier_updated_date']))
        
        conn.commit()
        print("RAW customer tier data saved successfully.")
    except Exception as e:
        if conn: conn.rollback()
        raise e
    finally:
        if conn:
            cursor.close()
            conn.close()