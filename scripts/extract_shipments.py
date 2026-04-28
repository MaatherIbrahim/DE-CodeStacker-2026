import requests
import psycopg2
import os

def extract_shipments_from_api():
    print("Starting RAW shipment data extraction...")
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
    
        response = requests.get("http://api:8000/api/shipments", timeout=10)
        response.raise_for_status()
        shipments = response.json().get('data', [])
    
        # Create raw table
        cursor.execute("DROP TABLE IF EXISTS raw_data.shipments;")
        cursor.execute("""
            CREATE TABLE raw_data.shipments (
                shipment_id VARCHAR(50),
                customer_id VARCHAR(50),
                shipping_cost DECIMAL(10,2),
                shipment_date DATE,
                status VARCHAR(50),
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    
        for shipment in shipments:
            cursor.execute("""
                INSERT INTO raw_data.shipments (shipment_id, customer_id, shipping_cost, shipment_date, status)
                VALUES (%s, %s, %s, %s, %s);
            """, (
                shipment['shipment_id'], shipment['customer_id'], 
                shipment['shipping_cost'], shipment['shipment_date'], shipment['status']
            ))
    
        conn.commit()
        print("RAW shipment data saved successfully.")
    except Exception as e:
        if conn: conn.rollback()
        raise e
    finally:
        if conn:
            cursor.close()
            conn.close()