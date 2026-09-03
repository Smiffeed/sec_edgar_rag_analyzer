import requests

auth_resp = requests.post(
    "http://localhost:8080/auth/token",
    json={"username": "airflow", "password": "airflow"}
)
token = auth_resp.json().get("access_token")

runs_resp = requests.get(
    "http://localhost:8080/api/v2/dags/sec_edgar_ingestion/dagRuns?state=running",
    headers={"Authorization": "Bearer " + token}
)
print(runs_resp.json())
