# Revenue Integrity Decision Pack Audit Note

## Trigger

Triggered from the `Revenue Integrity Decision Pack` expander on `Control Room Summary`.

## Data sources feeding the memo

- `data/processed/priority_scores.parquet` for the current governed queue slice, ownership, recoverability, and dollars at risk.
- `data/processed/kpi_snapshot.parquet` for the already-lost KPI framing.
- `data/processed/claims_or_account_status.parquet` and `data/processed/expected_charge_opportunities.parquet` for scoped control-room denominator and suppression context already used by the summary view.
- `data/processed/intervention_tracking.parquet` and `data/processed/corrections_rebills.parquet` for the intervention follow-through example and downstream outcome signal.
- `data/processed/queue_history.parquet` plus current Scenario Lab defaults for the what-if snapshot.
- `data/processed/run_manifest.json` for build timestamp and validation status.

## Included sections

- Executive summary.
- Top priority work queues.
- Control story.
- Intervention update.
- Scenario snapshot.
- Guardrails / caveats.

## Why this stays in scope

This artifact packages existing governed outputs into a single reviewer-ready memo without changing queue routing, priority logic, intervention logic, or adding predictive content. The pack stays facility-side, outpatient-first, deterministic-first, and keeps scenario content explicitly framed as what-if only.
