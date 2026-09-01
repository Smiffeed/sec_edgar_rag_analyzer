# Project Technical Debt & TODOs

## Architecture & Infrastructure
- [ ] **Migrate Telemetry from SQLite to PostgreSQL**: Replace local file-based `telemetry.db` with the existing PostgreSQL container to prevent "readonly" permission errors, avoid database locking when Airflow and Streamlit write concurrently, and align with enterprise microservice best practices.
