from __future__ import annotations

from pathlib import Path

import pandas as pd

from ri_control_room.logic.build_exception_queue import (
    ACTIVE_STAGE_ISSUE_DOMAIN_MAP,
    ACTIVE_STAGE_QUEUE_MAP,
    OUTPUT_FILENAME as EXCEPTION_QUEUE_FILENAME,
    derive_stage_entry_ts,
    write_exception_queue_parquet,
)
from ri_control_room.synthetic.generate_documentation_events import (
    OUTPUT_FILENAME as DOCUMENTATION_FILENAME,
    write_documentation_events_parquet,
)
from ri_control_room.synthetic.generate_encounters import (
    OUTPUT_FILENAME as ENCOUNTERS_FILENAME,
    get_processed_dir,
    write_encounters_parquet,
)
from ri_control_room.synthetic.workflow_profiles import get_workflow_profile


OUTPUT_FILENAME = "queue_history.parquet"

QUEUE_OWNER_MAP = {
    "Charge Reconciliation Monitor": "Revenue Integrity operations",
    "Documentation Support Exceptions": "Department operations",
    "Coding Pending Review": "Coding team",
    "Modifiers / Edits / Prebill Holds": "Billing operations",
    "Correction / Rebill Pending": "Billing operations",
}

TRANSITION_EVENT_TYPE_BY_STAGE = {
    "Charge capture pending": "Initial queue placement",
    "Documentation pending": "Documentation reroute",
    "Coding pending": "Coding review handoff",
    "Prebill edit / hold": "Prebill hold escalation",
    "Correction / rebill pending": "Correction / rebill handoff",
}

BLOCKER_STATE_BY_STAGE = {
    "Charge capture pending": "Missing or late charge capture",
    "Documentation pending": "Documentation support incomplete",
    "Coding pending": "Coding or modifier review pending",
    "Prebill edit / hold": "Prebill edit or hold unresolved",
    "Correction / rebill pending": "Correction or rebill pending",
}


def _load_inputs(
    repo_root: Path | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    processed_dir = get_processed_dir(repo_root)
    exception_queue_path = processed_dir / EXCEPTION_QUEUE_FILENAME
    encounter_path = processed_dir / ENCOUNTERS_FILENAME
    documentation_path = processed_dir / DOCUMENTATION_FILENAME

    if not encounter_path.exists():
        write_encounters_parquet(repo_root)
    if not documentation_path.exists():
        write_documentation_events_parquet(repo_root)
    if not exception_queue_path.exists():
        write_exception_queue_parquet(repo_root)

    return (
        pd.read_parquet(exception_queue_path),
        pd.read_parquet(encounter_path),
        pd.read_parquet(documentation_path),
    )


def _stage_path_for_row(scenario_code: str, current_stage: str) -> tuple[str, ...]:
    configured_path = tuple(
        str(stage_name) for stage_name in get_workflow_profile(scenario_code)["stage_path"]
    )
    if not configured_path:
        return (current_stage,)
    if configured_path[-1] == current_stage:
        return configured_path
    if current_stage in configured_path:
        return configured_path[: configured_path.index(current_stage) + 1]
    return (*configured_path, current_stage)


def _stage_segment_days(
    workflow_profile: dict[str, object],
    stage_path: tuple[str, ...],
    current_stage_age_days: int,
) -> tuple[int, ...]:
    configured_days = tuple(int(value) for value in workflow_profile["stage_segment_days"])
    if len(configured_days) == len(stage_path):
        return configured_days
    if not stage_path:
        return ()
    return (*([1] * max(len(stage_path) - 1, 0)), current_stage_age_days)


def _routing_reasons(
    workflow_profile: dict[str, object],
    stage_path: tuple[str, ...],
) -> tuple[str, ...]:
    configured_reasons = tuple(
        str(value) for value in workflow_profile.get("transition_reasons", ())
    )
    if len(configured_reasons) == len(stage_path):
        return configured_reasons
    default_reason = str(workflow_profile["routing_reason"])
    return tuple(default_reason for _ in stage_path)


def _transition_entry_timestamps(
    current_queue_entry_ts: pd.Timestamp,
    stage_segment_days: tuple[int, ...],
) -> tuple[pd.Timestamp, ...]:
    if not stage_segment_days:
        return (current_queue_entry_ts,)
    first_queue_entry_ts = current_queue_entry_ts - pd.Timedelta(days=sum(stage_segment_days[:-1]))
    entries = [first_queue_entry_ts]
    running_days = 0
    for segment_days in stage_segment_days[:-1]:
        running_days += int(segment_days)
        entries.append(first_queue_entry_ts + pd.Timedelta(days=running_days))
    return tuple(entries)


def _transition_event_type(stage_name: str, transition_index: int) -> str:
    if transition_index == 0:
        return "Initial queue placement"
    return TRANSITION_EVENT_TYPE_BY_STAGE.get(stage_name, "Queue reroute")


def latest_queue_history_rows(queue_history: pd.DataFrame) -> pd.DataFrame:
    if queue_history.empty:
        return queue_history.copy()
    ordered = queue_history.copy()
    if "current_record_flag" not in ordered.columns:
        ordered["current_record_flag"] = False
    else:
        ordered["current_record_flag"] = ordered["current_record_flag"].fillna(False)
    if "transition_event_index" not in ordered.columns:
        ordered["transition_event_index"] = ordered.get("reroute_count", 0).fillna(0).astype(int) + 1
    ordered = ordered.sort_values(
        [
            "encounter_id",
            "current_record_flag",
            "transition_event_index",
            "reroute_count",
            "current_queue_entry_ts",
        ],
        ascending=[True, True, True, True, True],
    )
    return ordered.drop_duplicates("encounter_id", keep="last").reset_index(drop=True)


def build_queue_history_df(repo_root: Path | None = None) -> pd.DataFrame:
    exception_queue, encounters, documentation_events = _load_inputs(repo_root)
    if exception_queue.empty:
        return exception_queue.copy()

    encounter_lookup = encounters.set_index("encounter_id").to_dict("index")
    documentation_groups = {
        encounter_id: group.copy()
        for encounter_id, group in documentation_events.groupby("encounter_id")
    }

    rows: list[dict[str, object]] = []
    for _, queue_row in exception_queue.iterrows():
        encounter = pd.Series(encounter_lookup[queue_row["encounter_id"]])
        documentation_subset = documentation_groups.get(queue_row["encounter_id"], pd.DataFrame())
        workflow_profile = get_workflow_profile(str(encounter["scenario_code"]))
        stage_path = _stage_path_for_row(
            str(encounter["scenario_code"]),
            str(queue_row["current_prebill_stage"]),
        )
        queue_path = tuple(ACTIVE_STAGE_QUEUE_MAP[stage_name] for stage_name in stage_path)
        stage_segment_days = _stage_segment_days(
            workflow_profile,
            stage_path,
            int(queue_row["stage_age_days"]),
        )
        routing_reasons = _routing_reasons(workflow_profile, stage_path)
        current_queue_entry_ts = derive_stage_entry_ts(
            str(queue_row["current_prebill_stage"]),
            encounter,
            documentation_subset,
        )
        entry_timestamps = _transition_entry_timestamps(current_queue_entry_ts, stage_segment_days)
        first_queue_entry_ts = entry_timestamps[0]

        for transition_index, (stage_name, queue_name, routing_reason) in enumerate(
            zip(stage_path, queue_path, routing_reasons, strict=False)
        ):
            prior_stage = stage_path[transition_index - 1] if transition_index > 0 else ""
            prior_queue = queue_path[transition_index - 1] if transition_index > 0 else ""
            current_owner = QUEUE_OWNER_MAP.get(queue_name, "")
            prior_owner = QUEUE_OWNER_MAP.get(prior_queue, "")
            rows.append(
                {
                    "queue_history_id": f"QH-{queue_row['account_id']}-{transition_index + 1}",
                    "claim_id": queue_row["claim_id"],
                    "account_id": queue_row["account_id"],
                    "encounter_id": queue_row["encounter_id"],
                    "transition_event_index": transition_index + 1,
                    "transition_event_type": _transition_event_type(stage_name, transition_index),
                    "current_record_flag": transition_index == len(stage_path) - 1,
                    "current_prebill_stage": stage_name,
                    "prior_stage": prior_stage,
                    "current_queue": queue_name,
                    "prior_queue": prior_queue,
                    "reroute_count": transition_index,
                    "ever_rerouted_flag": transition_index > 0,
                    "first_queue_entry_ts": first_queue_entry_ts,
                    "current_queue_entry_ts": entry_timestamps[transition_index],
                    "latest_reroute_ts": (
                        entry_timestamps[transition_index] if transition_index > 0 else pd.NaT
                    ),
                    "stage_transition_path": " -> ".join(stage_path[: transition_index + 1]),
                    "queue_transition_path": " -> ".join(queue_path[: transition_index + 1]),
                    "prior_owner": prior_owner,
                    "current_owner": current_owner,
                    "owner_handoff_flag": bool(prior_owner and prior_owner != current_owner),
                    "days_in_prior_queue": (
                        int(stage_segment_days[transition_index - 1]) if transition_index > 0 else 0
                    ),
                    "routing_reason": routing_reason,
                    "current_primary_blocker_state": (
                        queue_row["current_primary_blocker_state"]
                        if transition_index == len(stage_path) - 1
                        else BLOCKER_STATE_BY_STAGE.get(stage_name, str(queue_row["current_primary_blocker_state"]))
                    ),
                    "issue_domain": ACTIVE_STAGE_ISSUE_DOMAIN_MAP.get(stage_name, queue_row["issue_domain"]),
                    "recoverability_status": queue_row["recoverability_status"],
                }
            )

    df = pd.DataFrame(rows).sort_values(
        ["encounter_id", "transition_event_index"]
    ).reset_index(drop=True)
    for column in ("first_queue_entry_ts", "current_queue_entry_ts", "latest_reroute_ts"):
        df[column] = pd.to_datetime(df[column])
    return df


def write_queue_history_parquet(repo_root: Path | None = None) -> Path:
    df = build_queue_history_df(repo_root)
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_queue_history_parquet()


if __name__ == "__main__":
    main()
