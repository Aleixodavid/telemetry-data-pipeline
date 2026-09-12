# Telemetry Data Pipeline

An asynchronous Extract, Transform, Load (ETL) pipeline designed for asset telemetry ingestion, data normalization, and analytical reporting.

## Overview

The Telemetry Data Pipeline receives sensor metrics (CPU usage, memory, temperature, network latency, disk I/O) from remote nodes, validates incoming JSON payloads against strict schemas, normalizes data, and persists events in an optimized SQLite database.

## Architecture

### ETL Engine (`etl_engine.py`)
- **Extract**: Ingests individual metric events or bulk batches via REST endpoints.
- **Transform**: Sanitizes inputs, normalizes units, applies UNIX timestamps, and enriches data with tags.
- **Load**: Persists structured metrics into SQLite.

### Schema Validator (`schema_validator.py`)
Enforces field presence (`source`, `event_type`, `metric_value`), domain constraints, and numeric range limits.

### Database Layer (`db_manager.py`)
Configured with SQLite **Write-Ahead Logging (WAL) mode** (`PRAGMA journal_mode=WAL`), optimistic locking, and composite indexes on `(source, event_type)` and `(event_timestamp DESC)` to deliver query latencies under 150ms.

## API Endpoints

- `POST /api/ingest` — Ingest a single telemetry event.
- `POST /api/ingest/batch` — Ingest a bulk array of metric events.
- `POST /api/generate-sample` — Populate synthetic metric load (50–1000 events) for testing.
- `GET /api/reports/summary` — Consolidated metric summary (counts, averages, min/max).
- `GET /api/reports/by-source` — Metrics aggregated by source node.
- `GET /api/reports/by-period?granularity=hour` — Time-series aggregation by hour or day.

## Running Tests

```bash
python -m pytest tests/ -v
```
