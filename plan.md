That data ecosystem will be gathering differnt sources of new music from across the internet, presenting one interactive To-Listen-To thread where I can choose to save or discard the song, the ecosystem will listen to my entire spotify history by keeping a connection with the API and remove any songs from the aggregate To List to list, so I dont end up duplicating my listening time.

We need to use industry standard tools in order to teach me data engineering, here are some ideas but we should refine this, you help me do that:

Ingestion:
Kafka

Python SDK (signal_noise_sdk) — pip-installable internal package
Spotify API — recently played, playlist monitoring
AOTY scraper — new release discovery
Debezium — CDC, captures Postgres changes and streams into Kafka
Fivetran / Airbyte — managed ingestion (experiment)

Storage:
PostgreSQL — OLTP app database (tracks, queue, listening history)
DynamoDB — triage click events (high-volume, key-value)
S3 — raw data lake storage
Delta Lake — open table format on S3 (created by Databricks, open sourced)
Apache Iceberg — competing open table format (created by Netflix)

Streaming:
Kafka, both with and without MSK, or with and without Confluent, explain to me

Spark Structured streaming
Debezium, potentially
Zookeeper — Kafka coordination


Processing:
PySpark on EMR Serverless — Bronze→Silver batch jobs
AWS Glue — simpler ETL jobs
Query
Trino — distributed SQL engine, queries Delta Lake and Iceberg on S3
AWS Athena — serverless SQL on S3

Warehouse (OLAP):
ClickHouse — columnar analytical database, fast aggregations, feeds dashboards

Transformation:
dbt — Silver→Gold modelling, semantic layer

Orchestration:
Airflow (MWAA) — production orchestration

Application:
FastAPI — triage app backend
Streamlit — analytics dashboard on top of ClickHouse


Infrastructure:
Terraform — 100% IaC
Docker + docker-compose — full local dev stack
Kubernetes (EKS) — container orchestration for AWS deployment

CI/CD:
GitHub Actions — primary CI/CD pipeline
Jenkins — secondary CI/CD (comparison)
Buildkite — tertiary CI/CD (comparison)

Monitoring & Observability:
Datadog — APM and log management
Prometheus + Grafana — metrics and dashboards
OpenTelemetry — instrumentation standard

Quality & Governance:
Great Expectations — data quality tests
DataHub — data catalog and lineage

Cloud:
AWS (EMR Serverless, MSK, MWAA, RDS, S3, EKS, Athena, Glue)
testing
