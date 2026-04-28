# 🏗️ Rihal Data Engineering Challenge 2026: The Broken Pipeline

This repository contains a hardened, production-ready data pipeline transformed from a legacy "broken" state. The system ingests shipment data from a REST API and customer information from a CSV file to produce analytical reports on shipping spend.

## 🚀 Quick Start

### 1. Prerequisites
* Docker & Docker Compose
* Python 3.9+ (For local testing)

### 2. Environment Setup
Create a `.env` file from the provided template:
```
cp .env.example .env
```
Open the `.env` file and set your desired `DB_PASSWORD`. 

**Note:** The system is pre-configured with default values for Docker internal networking (`DB_HOST=postgres`, `DB_PORT=5432`). Do not change these unless you are modifying the Docker network.

### 3. Initialize Local Directories
Before launching, you must manually create the following directories to ensure correct Docker volume permissions for logging and backups:
```
mkdir logs
mkdir backups
```

### 4. Launch the Pipeline
Run the following command to build and start the entire stack:
```
docker-compose up -d
```
The system will automatically initialize the database, run migrations, and create an admin user.

### 5. Access the UI
* **Airflow:** http://localhost:8080 (Credentials: `admin` / `admin`)
* **API:** http://localhost:8000/api/shipments

---

## 🛠️ System Architecture

This pipeline implements a **Medallion (Multi-Tier) Architecture** to ensure data lineage and integrity:

1. **`raw_data` Schema:** Immutable landing zone. All data from API and CSV is stored here in its original state for auditing and reprocessing.
2. **`staging` Schema:** The "Cleaning" layer. Filters out invalid records (negative costs, null identifiers, duplicates) and enforces Primary/Foreign Key constraints.
3. **`analytics` Schema:** The "Reporting" layer. Pre-aggregated summaries optimized for business intelligence, providing **Total Shipping Spend per Tier per Month**.

---

## 🔒 Key Engineering Improvements

* **Security:** Moved from hardcoded strings to an environment-driven configuration (.env). Refactored all SQL logic to use parameterized queries to prevent SQL Injection.
* **Data Integrity:** Implemented Idempotency using TRUNCATE and ON CONFLICT (UPSERT) logic, ensuring the pipeline can be rerun safely without corrupting data.
* **Resilience:** Added try-except-finally blocks to all Python scripts for atomic transactions and resource cleanup.
* **Disaster Recovery:** Integrated an automated backup service that generates daily compressed SQL snapshots in the `./backups` directory.
* **Observability:** Persisted Airflow system logs to the host `./logs` directory for permanent auditability.

---

## 🧪 Testing

This project uses pytest and uv to validate critical business logic (such as data validation and filtering rules).

To run the tests locally:
```
uv run pytest
```

---

## 📊 Database Connection (External)
To explore the data using external tools (e.g., DbVisualizer, DBeaver), use the following credentials:
* **Host:** 127.0.0.1
* **Port:** 5444 (Mapped from internal 5432 to avoid host-level conflicts)
* **Database:** rihal_data
* **User:** airflow

---

## 📝 Documentation
For detailed insights into the engineering decisions and audit findings, please refer to:
* `ENGINEERING_AUDIT.md`: Detailed list of discovered weaknesses and their mitigations.
* `DESIGN_REFLECTION.md`: Reflection on trade-offs, scalability, and design patterns.

---

**Developed for the Rihal Data Engineering Talent Challenge 2026.**