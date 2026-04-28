# Engineering Audit

## Instructions
Document all critical weaknesses you discovered in the current system.

For each issue, provide:
- **Severity:** High / Medium / Low
- **Description:** What is the problem?
- **Impact:** What could happen in production?
- **Mitigation:** How did you fix it?

---

## Issues Discovered

### Issue 1: Port Configuration Conflicts
- **Severity:** High
- **Description:** the mock API and airflow webserver were both configured to use port 8080. also the defult postgresql port 5432 conflicted with local host processes.
- **Impact:** containers failed to start, giving port already allocated error, preventing the entire pipline from launching
- **Mitigation:** remapped the host-side postgresql port to 5444 and the API to 8000 to ensure environment isolation

---


### Issue 2: Brittle Docker Configuration
- **Severity:** medium
- **Description:** the docker-compose.yml contained YAML syntax errors and lacked and automated database initialization service.
- **Impact:** new developers could not just run the system. manual intervention was required to initialize the airflow metadata database
- **Mitigation:** fixed YAML syntax and implemented an airflow-init service to automate database migrations and user creation

---

### Issue 3: Missing Service Health Checks

- **Severity:** medium
- **Description:** the API container lacked a health endpoint and the orchestration layer didn't verify if the database was ready before starting the webserver.
- **Impact:** airflow tasks would fail during cold starts because they attempted to connect to services that were still booting up
- **Mitigation:** added a health route to the flask API and implementted depends_on: condition: service_healthy across the stack

---

### Issue 4: Hardcoded Credentials & Vulnerable Queries

- **Severity:** high
- **Description:** database credentials were hardcoded in scripts. also SQL queries used f-strings for data insertion instead of parameterized inputs.
- **Impact:** potentail for credntial leakage in version control and a high risk of SQL injection attacks.
- **Mitigation:** moved all secrets to a .env file and refactored python scripts to use os.getenv() and parameterized queries(%s)

---

### Issue 5:Silent Transaction Failures 

- **Severity:** high
- **Description:** python ingestion scripts lacked conn.commit() calls.
- **Impact:** the pipeline reported success (green) in airflow but the database remained empty because transactions were automatically rolled back. this creates a false success state.
- **Mitigation:** implemented explicit conn.commit() calls and wrapped logic in try-except-finally blocks for atomic transaction

---

### Issue 6:Lack of Referential Integrity

- **Severity:** high
- **Description:** the original database had no primary keys, foreign keys, or schemas.
- **Impact:** the system allowed duplicate shipments and shipments for non-existent customers recoeds, leading to incorrect financial analytics
- **Mitigation:** Implemented Primary and Foreign key constraints within the existing schemas and updated the loading logic to handle duplicate values, nulls, and shipments without corresponding customer records

---

### Issue 7:Dirty Upstream Data Handling

- **Severity:** high
- **Description:** the API provided records with NULL customer IDs and nagative shipping costs
- **Impact:** raw data ingestion crashed due to primary key violations, and financial reports were corrupted by illogical negative spend values.
- **Mitigation:** added a python validation layer to filter out records with null identifiers or non-positive costs

---

### Issue 8: Missing Backups and Log Persistence
- **Severity:** medium
- **Description:** no strategy existed for database backups or persistent logging outside the containers.
- **Impact:** accidental deletion of docker volumes would result in a total loss of business data and historical audit logs.
- **Mitigation:** integrated an automated db-backup service and mounted local volumes for persistent log storage

---

### Issue 9: Webserver/Scheduler Race Condition in Airflow 2.7.3
- **Severity:** high
- **Description:** The webserver attempts to render DAG metadata before the scheduler has successfully serialized the DAG into the backend database, resulting in a NoneType AttributeError.
- **Impact:** accidental deletion of docker volumes would result in a total loss of business data and historical audit logs.
- **Mitigation:** Adjusted the Docker healthcheck with a longer start_period and ensured the scheduler has priority during startup to populate the metadata tables before the webserver begins health monitoring