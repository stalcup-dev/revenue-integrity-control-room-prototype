# Denial Feedback + CDM Governance Monitor Audit Note

## Proof

- Thin monitor added as a standalone page: `Denial Feedback + CDM Governance Monitor`
- Downstream denial signal shown with:
  - denial category
  - denial reason group
  - payer group
  - denial amount
  - linked upstream issue domain
- CDM governance section shown with:
  - department
  - service line
  - expected code
  - expected modifier
  - default units
  - revenue code
  - active flag
  - rule status
- Selected-pattern linkage shown with:
  - downstream signal
  - upstream issue domain
  - likely root cause mechanism
  - likely owner / action path
  - why this matters operationally
  - suggested next step

## Data Used

- `denials_feedback.parquet` for downstream denial signals
- `claims_or_account_status.parquet` for upstream root-cause and owner linkage
- `expected_charge_opportunities.parquet` for expected code / modifier / units context
- `data/reference/cdm_reference.csv` for thin governed CDM / rule reference items
- `data/reference/department_charge_logic_map.csv` for department-specific operational validation context
- `kpi_snapshot.parquet` and `corrections_rebills.parquet` for referenced KPI-ready operational context

## Why This Remains In Scope

- Denials remain downstream evidence only; no appeals or adjudication workflow was added
- No queue routing logic changed
- No priority formula changed
- No predictive logic was introduced
- The page preserves separation among upstream issue domain, root cause mechanism, and owner / action hint

## Screenshot Artifacts

- `artifacts/denial_feedback_cdm_monitor/denial_feedback_cdm_top.png`
- `artifacts/denial_feedback_cdm_monitor/denial_feedback_cdm_detail.png`
