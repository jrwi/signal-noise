# Signal:Noise Learning Plan

## Project north star

You are going to create the ultimate music discovery tool for Jonathan, set into a data engineering ecosystem as a teaching exercise. The anchor of this will be creating a log of everything you have listened to so you can cross-reference your history against new music lists and remove songs you have already heard before. You will track the various music sources, spotify playlists, magazine's playlists like the Fader and Pitchfork, Album of the Year albums, and your friend's Hunter's playlists.

Collectively, you will create a page where you can go progress through listening to various new music sources to stay up to date.

Start with a simple code base and only add new folders when they are necessary and always do it one at a time.

## How to use this plan

Work through the phases in order. Each phase must produce a usable increment, written decisions, automated verification, and operational evidence. Move forward only after its checkpoint is met. Revisit tool choices as scale, reliability needs, cost, or team constraints change.

The tools listed in `PLAN.md` are candidates, not a checklist. Using fewer tools well is better engineering than assembling a fashionable stack without a concrete need.

## Operating principles

1. **Start from a user outcome.** Every component must improve discovery, deduplication, decision-making, reliability, or development speed.
2. **Earn complexity.** Introduce a distributed or managed system only after measuring the limitation it solves.
3. **Separate concepts from products.** Learn event streaming before comparing Kafka vendors; learn table formats before operating both Delta Lake and Iceberg.
4. **Preserve raw facts.** Keep source payloads or reproducible snapshots so transformations can be replayed and audited.
5. **Design for idempotency.** Retries must not duplicate tracks, listening events, or user decisions.
6. **Make contracts explicit.** Define schemas, ownership, freshness, quality rules, and compatibility expectations at boundaries.
7. **Observe before optimizing.** Establish service-level indicators, logs, metrics, traces, and cost measurements before changing architecture.
8. **Automate the repeatable.** Tests, local setup, schema migrations, deployments, and recovery exercises belong in code.
9. **Record decisions.** Use short architecture decision records (ADRs) that state context, options, decision, consequences, and reversal conditions.
10. **Prefer reversible choices.** Keep domain logic portable and avoid premature dependence on a vendor-specific feature.

For any proposed tool, answer:

- What measured problem exists now?
- What is the simplest alternative?
- What new failure modes and operating burden does this add?
- What will it cost at expected and 10× load?
- How will success be measured, and when will the decision be revisited?

## Phase 1 — Trustworthy Spotify listening history

### Goal

Build the first dependable data pipeline: ingest Jonathan's Spotify listening history into PostgreSQL so it can be rerun, resumed, tested, and inspected with confidence.

### Scope and deliverables

- Define listening-event and track models with source identifiers, playback time, ingestion time, and enough raw-source metadata to debug failures.
- Create PostgreSQL migrations with primary keys, uniqueness constraints, required fields, and useful indexes.
- Build a small Python ingestion job for Spotify's recently played history. Develop against saved Spotify response fixtures before relying on live API calls.
- Store an incremental checkpoint: the durable position from which the next run resumes. Start with a playback-time **watermark**, meaning the latest event time processed successfully.
- Make writes idempotent: replaying the same input produces the same stored state instead of duplicate listening events.
- Handle pagination, rate limits, expired credentials, transient failures, malformed records, and partial runs. Classify errors, retry only recoverable failures with bounded backoff, and retain diagnostic context for rejected records.
- Add unit tests for parsing and checkpoint logic and PostgreSQL integration tests for constraints, duplicates, reruns, incremental loads, and recovery after partial failure.
- Check invariants such as unique source event identity, valid timestamps, non-null track identity, monotonic checkpoints, and stored-row counts matching accepted fixture records.
- Provide simple SQL queries or a CLI inspection command that shows what was played, when, how many events loaded, and whether any records were rejected or duplicated.
- Document setup, a first ingestion, a safe rerun, common failures, and recovery in a short runbook.
- Write an ADR explaining why a Python job and PostgreSQL are sufficient for the first pipeline.

### Key concepts

Source-to-target modeling, primary and natural keys, transactions, constraints, idempotency, deduplication, incremental checkpoints and watermarks, pagination, error classification, partial-failure recovery, schema migrations, test fixtures, data invariants, and operational inspection.

### Recommended tools and rationale

- **Python:** keeps extraction, validation, and loading explicit and easy to test.
- **PostgreSQL:** provides durable storage, transactions, constraints, indexing, and direct SQL inspection in one mature system.
- **Docker Compose:** makes the job and database reproducible locally.
- **pytest, saved Spotify fixtures, and SQL assertions:** make normal, duplicate, malformed, paginated, and failure cases repeatable without depending on the network.
- **psql or a small CLI command:** exposes stored data without adding a serving layer.

FastAPI and any other API are explicitly deferred until a real consumer or integration need exists; an API is not foundational to the Phase 1 ingestion learning goal. Do not add Kafka, Spark, Airflow, DynamoDB, a lakehouse, Kubernetes, or ClickHouse either; none solves a Phase 1 requirement.

### Checkpoint

A fresh checkout can start PostgreSQL and run the pipeline from documented steps. A fixture load, identical rerun, incremental second load, and simulated partial failure all produce the expected rows and checkpoint. Quality checks pass, failures are diagnosable, SQL answers basic listening-history questions, and the design can be defended in a senior data-engineering interview: guarantees, failure modes, tradeoffs, and evidence that heavier tooling is unnecessary.

## Phase 2 — Real sources and trustworthy pipelines

### Goal

Connect Spotify listening history and at least one discovery source while making ingestion recoverable, observable, and safe to rerun.

### Scope and deliverables

- Implement a Spotify adapter with OAuth token handling, pagination, rate-limit handling, and incremental checkpoints.
- Implement an AOTY or other discovery adapter only if its access method and terms permit it.
- Reconcile candidates with listening history and remove or suppress already-heard tracks.
- Preserve raw source responses with ingestion metadata and retention rules.
- Define source-to-canonical schemas and explicit data contracts.
- Add retry/backoff, dead-letter or quarantine handling, reconciliation jobs, and data-quality checks.
- Measure freshness, volume, duplicates, failures, and reconciliation accuracy.
- Package genuinely shared client/domain code as `signal_noise_sdk` only after two consumers demonstrate the need.

### Key concepts

Batch and micro-batch ingestion, watermarks and cursors, late and missing data, replay, backfills, rate limits, secrets, lineage, contract evolution, quality dimensions, and source compliance.

### Recommended tools and rationale

- **Scheduled Python jobs:** simplest adequate orchestration while workflows remain small.
- **PostgreSQL raw and staging tables, or S3-compatible object storage:** choose object storage when payload volume, cheap retention, or independent replay justifies it.
- **Great Expectations or lightweight SQL checks:** adopt a framework only if tests need reusable suites, reporting, or ownership beyond ordinary test code.
- **OpenTelemetry-compatible instrumentation:** introduce consistent telemetry concepts without requiring a particular backend.

Airflow is not yet automatic. Adopt it only when dependency graphs, backfills, retries, scheduling visibility, or multiple operators make simpler scheduling painful.

### Checkpoint

The system can recover from an interrupted ingestion, replay a bounded interval, explain why a candidate was suppressed, alert on stale or malformed data, and rotate credentials without code changes.

## Phase 3 — Analytics and dimensional modeling

### Goal

Turn product events into reliable answers about discovery quality and user behavior.

### Scope and deliverables

- Define decision-oriented metrics such as acceptance rate, time-to-triage, source yield, repeat-listen proxy, freshness, and deduplication rate.
- Model facts and dimensions with documented grain, keys, and slowly changing attributes where justified.
- Build staging, intermediate, and mart models with tests and documentation.
- Create a dashboard that answers a short list of named product questions.
- Establish metric ownership and a process for changing definitions.
- Validate analytical results against operational records.

### Key concepts

OLTP versus OLAP, dimensional modeling, fact grain, conformed dimensions, slowly changing dimensions, semantic consistency, incremental models, data lineage, and stakeholder-oriented metric design.

### Recommended tools and rationale

- **dbt:** useful when SQL transformations form a dependency graph needing tests, documentation, lineage, and deployment discipline.
- **PostgreSQL analytics first:** adequate at modest scale and avoids premature duplication.
- **Streamlit or a lightweight dashboard:** rapidly exposes whether the models answer useful questions.
- **ClickHouse later:** add only after measured query latency, concurrency, data volume, or cost shows PostgreSQL is the bottleneck.

### Checkpoint

Every dashboard metric has a definition, owner, grain, lineage, test, and reconciliation example. A reviewer can trace a number back to source facts and understand its limitations.

## Phase 4 — Event-driven evolution

### Goal

Learn streaming by solving a demonstrated latency, decoupling, or fan-out requirement—not by replacing working batch pipelines for novelty.

### Entry evidence

Examples include multiple independent consumers of triage events, a real need for near-real-time queue updates, unacceptable polling load, or a replayable event log required for recovery.

### Scope and deliverables

- Define event contracts, keys, ordering requirements, retention, and compatibility rules.
- Publish one bounded event flow, such as triage decisions, and keep a reconciliation path to PostgreSQL.
- Implement idempotent consumers and test duplicates, reordering, poison messages, and downtime recovery.
- Document delivery semantics honestly; prefer at-least-once delivery with idempotency unless stricter semantics are proven necessary.
- Compare local Kafka, managed Kafka/MSK, and Confluent on operations, features, cost, portability, and support.
- Evaluate CDC with Debezium only for a specific downstream need; do not use CDC to avoid designing domain events.

### Key concepts

Logs and queues, partitions, ordering, consumer groups, offsets, retention, schema evolution, backpressure, delivery semantics, CDC, replay, and eventual consistency.

### Recommended tools and rationale

- **Kafka:** appropriate when durable replay, ordered partitions, independent consumers, and meaningful event volume justify its operating cost.
- **Debezium:** appropriate when consumers need database changes and application-owned events are unavailable or insufficient.
- **Managed Kafka:** appropriate when reduced operational labor outweighs cloud cost and local learning goals.

Modern Kafka can operate without ZooKeeper using KRaft; study ZooKeeper as architectural history or only if a chosen deployment still requires it.

### Checkpoint

Load and failure tests demonstrate lag recovery, duplicate safety, schema compatibility, and reconciliation. The design review includes a credible batch alternative and total-cost comparison.

## Phase 5 — Lakehouse and distributed processing experiments

### Goal

Learn large-scale storage and computation through controlled experiments, adopting them in the product only if scale or retention requires it.

### Scope and deliverables

- Define bronze/raw, silver/validated, and gold/serving responsibilities without treating layer names as a substitute for contracts.
- Land immutable, partitioned source data in S3-compatible storage with lifecycle and replay policies.
- Run a representative backfill using PySpark and measure runtime, shuffle, skew, small-file behavior, and cost.
- Compare Apache Iceberg and Delta Lake using the same workload: schema evolution, partition evolution, time travel, engine support, maintenance, and lock-in.
- Query the chosen format with Trino or Athena and document performance tuning.
- Select at most one table format for the main path; keep the other as a learning experiment unless a second requirement is proven.

### Key concepts

Distributed execution, partitioning, shuffle, skew, columnar formats, predicate pushdown, compaction, metadata scaling, schema and partition evolution, snapshots, and cost/performance testing.

### Recommended tools and rationale

- **S3 and Parquet:** durable, economical analytical storage with broad interoperability.
- **PySpark locally, then EMR Serverless if justified:** separates learning the engine from learning cloud operations and provides a pay-per-job option.
- **Iceberg or Delta Lake:** choose from engine compatibility and workload evidence, not brand preference.
- **Athena or Trino:** Athena favors low-operations ad hoc querying; Trino favors greater control and multi-source federation at the cost of operating a service.
- **AWS Glue:** consider for metadata cataloging or simple AWS-native ETL where its operational simplicity wins.

### Checkpoint

A benchmark report explains the dataset, workload, correctness, runtime, cost, operational burden, and decision. A replay from raw data reproduces a curated table.

## Phase 6 — Production platform and organizational scale

### Goal

Operate the system reliably and demonstrate platform judgment, security, governance, and technical leadership.

### Scope and deliverables

- Define service-level objectives (SLOs), error budgets, alerts, on-call expectations, and incident procedures.
- Run disaster-recovery and data-restoration exercises with recovery objectives.
- Model cloud cost at current, 10×, and 100× load; tag resources and set budgets.
- Threat-model authentication, authorization, secrets, network boundaries, dependencies, and personal data.
- Establish retention, deletion, least privilege, encryption, audit logging, ownership, catalog, and lineage policies.
- Use Terraform for reproducible cloud infrastructure and a primary CI/CD pipeline with promotion and rollback.
- Create a capacity plan and an architecture roadmap tied to product scenarios.
- Write and present a design proposal, run a review, record dissent and decisions, and produce an incident postmortem.

### Recommended tools and rationale

- **Terraform:** infrastructure review, repeatability, drift control, and recovery.
- **GitHub Actions:** one primary CI/CD system is sufficient. Jenkins or Buildkite should be isolated comparison exercises, not parallel production pipelines without an organizational need.
- **Prometheus/Grafana or Datadog:** choose based on build-versus-buy economics, team capacity, integrations, and operational ownership.
- **DataHub:** introduce when dataset count, ownership discovery, governance workflow, and cross-system lineage justify running a catalog.
- **Airflow/MWAA:** adopt when workflow complexity and operational ownership justify a full orchestrator.
- **EKS/Kubernetes:** adopt only when multiple services, deployment scale, portability, or platform standardization outweigh substantial operational complexity. A simpler container service may be the better production answer.
- **DynamoDB:** use only for an access pattern whose scale, latency, and key-value model materially outperform keeping triage events in PostgreSQL.

### Checkpoint

The system meets stated SLOs during failure drills, can be restored within recovery objectives, has a reviewed threat model and cost model, and can be operated by someone other than its author using the documentation.

## Architecture evolution

The architecture should evolve through evidence-backed transitions:

1. **Modular monolith:** source adapter → domain service → PostgreSQL → FastAPI/UI.
2. **Reliable ingestion:** scheduled connectors → raw/staging retention → canonical tables → reconciliation and quality checks.
3. **Analytical layer:** operational facts → dbt models → PostgreSQL marts → dashboard.
4. **Event-driven path, if earned:** application/CDC events → Kafka → idempotent consumers, with reconciliation retained.
5. **Lakehouse path, if earned:** raw events/files → S3/Parquet → Spark → one open table format → Athena or Trino.
6. **Scaled serving, if earned:** workload-specific stores such as ClickHouse or DynamoDB, each owned by a measured access pattern.

At every transition, maintain a source of truth, replay or reconciliation strategy, migration plan, rollback plan, ownership boundary, and observability. Avoid big-bang rewrites; migrate one bounded flow and compare correctness before expanding.

## Assessment and portfolio evidence

Each phase should leave evidence that another engineer can inspect:

- A working demo tied to a user outcome.
- Architecture diagram and data-flow diagram.
- ADRs showing alternatives, tradeoffs, and reversal triggers.
- Versioned schemas, contracts, and migrations.
- Automated unit, integration, contract, data-quality, and failure-path tests appropriate to the phase.
- Operational dashboard, alerts, runbook, and recovery evidence.
- Benchmark or load-test report with reproducible inputs.
- Cost estimate and security/privacy review.
- Design-review document and concise presentation for a technical and nontechnical audience.
- Retrospective: what was learned, what remains risky, and what should be simplified.

Use these recurring questions in reviews:

- Can the engineer explain the system's correctness boundaries and failure modes?
- Can they distinguish an observed constraint from a hypothetical one?
- Can they quantify latency, freshness, throughput, availability, recovery, and cost?
- Can they make a recommendation while presenting credible alternatives?
- Can another person operate, extend, and challenge the system from its artifacts?

## Staff-level themes to practice continuously

### System design and tradeoffs

Connect business outcomes to workload characteristics, define explicit requirements, compare alternatives, identify irreversible choices, and plan safe evolution. Staff judgment is often demonstrated by removing unnecessary systems.

### Reliability

Design for retries, partial failure, replay, reconciliation, backfills, graceful degradation, disaster recovery, and useful observability. Treat data correctness and freshness as service reliability.

### Cost and capacity

Estimate unit economics, storage growth, compute demand, network transfer, and operational labor. Benchmark before scaling and define thresholds that trigger architecture changes.

### Security and privacy

Apply least privilege, secrets management, encryption, dependency hygiene, auditability, retention, and deletion. Minimize stored personal data and document how Spotify-derived data is handled.

### Governance

Make ownership, contracts, classification, quality, lineage, lifecycle, and change management explicit. Governance should enable safe change, not become documentation theater.

### Technical leadership

Frame problems, set principles, create alignment, mentor through reviews, sequence migrations, manage risk, and make decisions under uncertainty. Practice disagree-and-commit and revisit decisions when their assumptions change.

### Communication

Write for the audience. Produce concise status updates, design documents, incident reports, executive summaries, and diagrams. State the recommendation first, quantify impact, expose uncertainty, and make the requested decision clear.

## Current next step

Start **Phase 1 only**. Before selecting another platform tool:

1. Write a one-page product brief defining the user, core workflow, success measure, and explicit non-goals.
2. Define the five core entities and their invariants, including the canonical track identity and deduplication policy.
3. Draw the modular-monolith data flow and write the PostgreSQL-first ADR.
4. Create a thin walking skeleton: one fixture-based candidate enters the database, appears through the API, receives a save/discard decision, and is not duplicated when ingestion reruns.
5. Add tests and a reproducible local command, then demo the complete path.

Do not begin Kafka, Spark, Kubernetes, lakehouse, or multi-database work until this slice is usable and the Phase 1 checkpoint is met. The next architecture decision should be driven by what the working product teaches us.
