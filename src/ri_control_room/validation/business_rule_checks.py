from __future__ import annotations

from pathlib import Path

import pandas as pd

from ri_control_room.artifacts import load_existing_validation_tables
from ri_control_room.constants import RECOVERABILITY_STATES
from ri_control_room.logic.build_exception_queue import ACTIVE_STAGE_QUEUE_MAP

MISSING_TIMESTAMP_GAPS = {"missing_stop_time", "missing_case_timestamp"}


def _result_row(
    check_name: str,
    passed: bool,
    rows_examined: int,
    failure_count: int,
    detail: str,
) -> dict[str, object]:
    return {
        "check_name": check_name,
        "passed": bool(passed),
        "rows_examined": int(rows_examined),
        "failure_count": int(failure_count),
        "detail": detail,
    }


def _path_tokens(path_value: object) -> tuple[str, ...]:
    if pd.isna(path_value):
        return ()
    return tuple(
        token.strip()
        for token in str(path_value).split("->")
        if token.strip()
    )


def _has_adjacent_duplicates(tokens: tuple[str, ...]) -> bool:
    return any(left == right for left, right in zip(tokens, tokens[1:], strict=False))


def run_business_rule_checks_for_tables(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    statuses = tables["claims_or_account_status"]
    documentation_events = tables["documentation_events"]
    expected = tables["expected_charge_opportunities"]
    charge_events = tables["charge_events"]
    queue = tables["exception_queue"]
    queue_history = tables["queue_history"]

    results: list[dict[str, object]] = []

    order_only_failures = expected.loc[
        (expected["signal_basis"] != "documentation_event")
        | (~expected["documented_performed_activity_flag"].fillna(False))
        | (expected["documentation_event_id"].fillna("") == "")
    ]
    results.append(
        _result_row(
            "order_only_expectation_blocked",
            order_only_failures.empty,
            len(expected),
            len(order_only_failures),
            "Every expected opportunity is traceable to documented performed activity."
            if order_only_failures.empty
            else "Expected opportunities without documented performed support were found.",
        )
    )

    timestamp_gap_rows = documentation_events.loc[
        documentation_events["documentation_gap_type"].isin(MISSING_TIMESTAMP_GAPS),
        ["encounter_id", "documentation_event_id"],
    ].drop_duplicates()
    timestamp_gap_expectations = expected.merge(
        timestamp_gap_rows,
        on=["encounter_id", "documentation_event_id"],
        how="inner",
    )
    timestamp_failures = timestamp_gap_expectations.loc[
        (timestamp_gap_expectations["evidence_completeness_status"] == "complete")
        | (timestamp_gap_expectations["opportunity_status"].isin(["recoverable_missed_charge", "expected_charge_supported"]))
    ]
    results.append(
        _result_row(
            "timestamp_dependency_blocked",
            timestamp_failures.empty,
            len(timestamp_gap_expectations),
            len(timestamp_failures),
            "Missing timestamp support never becomes a clean or recoverable expected opportunity."
            if timestamp_failures.empty
            else "At least one missing-timestamp case was promoted into a clean or recoverable opportunity.",
        )
    )

    partial_docs = documentation_events.loc[
        documentation_events["documentation_status"].isin(["partial", "incomplete"])
        | (~documentation_events["supports_charge_flag"].fillna(False)),
        ["encounter_id", "documentation_event_id"],
    ].drop_duplicates()
    partial_doc_expectations = expected.merge(
        partial_docs,
        on=["encounter_id", "documentation_event_id"],
        how="inner",
    )
    partial_doc_failures = partial_doc_expectations.loc[
        (partial_doc_expectations["evidence_completeness_status"] == "complete")
        | partial_doc_expectations["opportunity_status"].isin(["expected_charge_supported", "recoverable_missed_charge"])
    ]
    results.append(
        _result_row(
            "partial_documentation_not_promoted",
            partial_doc_failures.empty,
            len(partial_doc_expectations),
            len(partial_doc_failures),
            "Partial or incomplete documentation stays out of clean expected-charge outcomes."
            if partial_doc_failures.empty
            else "Partial or incomplete documentation was promoted into a clean or recoverable outcome.",
        )
    )

    contradictory_support_rows = expected.loc[
        expected["charge_event_exists_flag"].fillna(False)
        & (expected["evidence_completeness_status"] != "complete")
        & (~expected["suppression_flag"].fillna(False))
    ]
    contradictory_support_failures = contradictory_support_rows.loc[
        ~contradictory_support_rows["opportunity_status"].isin(
            {"unsupported_charge_risk", "documentation_support_pending"}
        )
    ]
    results.append(
        _result_row(
            "contradictory_charge_support_flagged",
            contradictory_support_failures.empty,
            len(contradictory_support_rows),
            len(contradictory_support_failures),
            "Posted charges with weak support remain flagged as support risk, not cleanly resolved."
            if contradictory_support_failures.empty
            else "Contradictory posted-charge support cases were not flagged as support risk.",
        )
    )

    mapping_failures = queue.loc[
        queue["current_prebill_stage"].map(ACTIVE_STAGE_QUEUE_MAP) != queue["current_queue"]
    ]
    stage_queue_counts = queue.groupby("current_prebill_stage")["current_queue"].nunique()
    collapsed_workflow = bool(
        queue["current_queue"].nunique() != queue["current_prebill_stage"].nunique()
    )
    workflow_failure_count = int(len(mapping_failures) + (1 if collapsed_workflow else 0))
    workflow_detail = "Stage-specific queue routing remains distinct and governed."
    if not mapping_failures.empty:
        workflow_detail = "Active items violate the governed stage-to-queue mapping."
    elif collapsed_workflow or (stage_queue_counts > 1).any():
        workflow_detail = "Active stages have drifted into a collapsed or inconsistent queue model."
    results.append(
        _result_row(
            "universal_workflow_drift_blocked",
            mapping_failures.empty
            and not collapsed_workflow
            and not (stage_queue_counts > 1).any(),
            len(queue),
            workflow_failure_count,
            workflow_detail,
        )
    )

    suppressed = expected.loc[
        expected["opportunity_status"] == "packaged_or_nonbillable_suppressed"
    ].copy()
    suppressed_rule_failures = suppressed.loc[
        (~suppressed["suppression_flag"].fillna(False))
        | (suppressed["why_not_billable_explanation"].fillna("") == "")
    ]
    packaged_classifications = statuses.loc[
        statuses["issue_domain"]
        == "Packaged / non-billable / false-positive classification",
        "encounter_id",
    ]
    misrouted_packaged_classifications = queue.loc[
        queue["encounter_id"].isin(packaged_classifications)
    ]
    suppressed_in_reconciliation_queue = queue.loc[
        queue["encounter_id"].isin(suppressed["encounter_id"])
        & (queue["current_queue"] == "Charge Reconciliation Monitor")
    ]
    packaged_failure_count = int(
        len(suppressed_rule_failures)
        + len(misrouted_packaged_classifications)
        + len(suppressed_in_reconciliation_queue)
    )
    packaged_detail = "Suppressed packaged or non-billable cases stay explained and out of leakage routing."
    if packaged_failure_count > 0:
        packaged_detail = (
            "Suppressed cases are either missing explanation, misrouted as active false positives, "
            "or leaking into reconciliation work."
        )
    results.append(
        _result_row(
            "packaged_suppression_holds",
            packaged_failure_count == 0,
            len(expected),
            packaged_failure_count,
            packaged_detail,
        )
    )

    blocker_counts = queue.groupby("account_id")["current_primary_blocker_state"].nunique()
    multiple_blocker_accounts = blocker_counts.loc[blocker_counts != 1]
    results.append(
        _result_row(
            "multiple_current_blockers_blocked",
            multiple_blocker_accounts.empty and queue["account_id"].is_unique,
            len(queue),
            int(len(multiple_blocker_accounts)),
            "One current primary blocker is enforced per active account."
            if multiple_blocker_accounts.empty and queue["account_id"].is_unique
            else "One or more active accounts expose multiple current blockers.",
        )
    )

    unsupported_rows = expected.loc[expected["opportunity_status"] == "unsupported_charge_risk"]
    unsupported_failures = unsupported_rows.loc[
        (~unsupported_rows["charge_event_exists_flag"].fillna(False))
        | (unsupported_rows["charge_status_example"].fillna("") == "")
    ]
    results.append(
        _result_row(
            "unsupported_charge_risk_distinct_from_undercapture",
            unsupported_failures.empty,
            len(unsupported_rows),
            len(unsupported_failures),
            "Unsupported charge risk remains tied to posted-charge exposure rather than simple missing charge cases."
            if unsupported_failures.empty
            else "One or more unsupported-charge rows are missing the posted-charge evidence that should distinguish them from undercapture.",
        )
    )

    correction_statuses = statuses.loc[
        statuses["current_prebill_stage"] == "Correction / rebill pending"
    ]
    correction_status_failures = correction_statuses.loc[
        correction_statuses["final_bill_datetime"].isna()
        | (~correction_statuses["rebill_flag"].fillna(False))
        | (~correction_statuses["corrected_claim_flag"].fillna(False))
        | (
            correction_statuses["recoverability_status"]
            != "Post-final-bill recoverable by correction / rebill"
        )
    ]
    correction_queue_rows = queue.loc[
        queue["current_prebill_stage"] == "Correction / rebill pending"
    ]
    correction_queue_failures = correction_queue_rows.loc[
        (correction_queue_rows["current_queue"] != "Correction / Rebill Pending")
        | (
            correction_queue_rows["recoverability_status"]
            != "Post-final-bill recoverable by correction / rebill"
        )
    ]
    correction_failures = int(len(correction_status_failures) + len(correction_queue_failures))
    results.append(
        _result_row(
            "correction_rebill_requires_postbill_context",
            correction_failures == 0,
            len(correction_statuses) + len(correction_queue_rows),
            correction_failures,
            "Correction and rebill cases stay anchored to post-bill recoverability and true rebill context."
            if correction_failures == 0
            else "Correction or rebill rows are missing final-bill context or correct post-bill recoverability.",
        )
    )

    invalid_queue_recoverability = queue.loc[
        (queue["recoverability_status"].fillna("") == "")
        | (~queue["recoverability_status"].isin(RECOVERABILITY_STATES))
        | (~queue["recoverability_active_queue_allowed"].fillna(False))
    ]
    invalid_expected_recoverability = expected.loc[
        (expected["recoverability_status"].fillna("") == "")
        | (~expected["recoverability_status"].isin(RECOVERABILITY_STATES))
    ]
    invalid_status_recoverability = statuses.loc[
        (statuses["recoverability_status"].fillna("") == "")
        | (~statuses["recoverability_status"].isin(RECOVERABILITY_STATES))
    ]
    recoverability_failures = int(
        len(invalid_queue_recoverability)
        + len(invalid_expected_recoverability)
        + len(invalid_status_recoverability)
    )
    results.append(
        _result_row(
            "recoverability_logic_present",
            recoverability_failures == 0,
            len(queue) + len(expected) + len(statuses),
            recoverability_failures,
            "Recoverability is populated from the approved governed state set everywhere it is needed."
            if recoverability_failures == 0
            else "Recoverability coverage is missing or uses non-approved states.",
        )
    )

    suppressed_lookalikes = expected.loc[
        (expected["opportunity_status"] == "packaged_or_nonbillable_suppressed")
        & (
            (expected["evidence_completeness_status"] == "complete")
            | expected["charge_event_exists_flag"].fillna(False)
        )
    ]
    suppressed_lookalike_failures = suppressed_lookalikes.loc[
        suppressed_lookalikes["why_not_billable_explanation"].fillna("") == ""
    ]
    results.append(
        _result_row(
            "suppressed_billable_lookalikes_explained",
            suppressed_lookalike_failures.empty,
            len(suppressed_lookalikes),
            len(suppressed_lookalike_failures),
            "Suppressed-but-looks-billable cases stay explicitly explained."
            if suppressed_lookalike_failures.empty
            else "At least one suppressed lookalike case is missing an explicit why-not-billable explanation.",
        )
    )

    rerouted_cases = queue_history.loc[queue_history["reroute_count"] > 0]
    reroute_history_failures = rerouted_cases.loc[
        (rerouted_cases["prior_queue"].fillna("") == "")
        | (rerouted_cases["stage_transition_path"].fillna("") == "")
    ]
    results.append(
        _result_row(
            "rerouted_cases_have_history",
            reroute_history_failures.empty,
            len(rerouted_cases),
            len(reroute_history_failures),
            "Rerouted cases carry prior queue and transition-path history."
            if reroute_history_failures.empty
            else "At least one rerouted case is missing prior queue or transition path detail.",
        )
    )

    transition_failures = 0
    for row in queue_history.itertuples():
        stage_tokens = _path_tokens(row.stage_transition_path)
        queue_tokens = _path_tokens(row.queue_transition_path)
        invalid = (
            not stage_tokens
            or not queue_tokens
            or len(stage_tokens) != len(queue_tokens)
            or _has_adjacent_duplicates(stage_tokens)
            or _has_adjacent_duplicates(queue_tokens)
            or stage_tokens[-1] != row.current_prebill_stage
            or queue_tokens[-1] != row.current_queue
            or int(row.reroute_count) != len(stage_tokens) - 1
        )
        if invalid:
            transition_failures += 1
    results.append(
        _result_row(
            "duplicate_transition_paths_blocked",
            transition_failures == 0,
            len(queue_history),
            transition_failures,
            "Queue-history paths remain internally consistent and free of duplicate adjacent transitions."
            if transition_failures == 0
            else "Queue-history paths contain duplicate or inconsistent stage or queue transitions.",
        )
    )

    posted_charge_rows = charge_events.loc[
        charge_events["charge_status"].fillna("") != "missing"
    ]
    if posted_charge_rows.empty:
        unsupported_mix_failures = 1
    else:
        unsupported_mix_failures = 0
    results.append(
        _result_row(
            "posted_charge_population_present",
            unsupported_mix_failures == 0,
            len(charge_events),
            unsupported_mix_failures,
            "The artifact set includes posted-charge rows needed to exercise unsupported-charge validation."
            if unsupported_mix_failures == 0
            else "No posted-charge rows were present, reducing unsupported-charge realism.",
        )
    )

    return pd.DataFrame(results).sort_values(["passed", "check_name"]).reset_index(drop=True)


def run_business_rule_checks(repo_root: Path | None = None) -> pd.DataFrame:
    tables = load_existing_validation_tables(repo_root)
    return run_business_rule_checks_for_tables(tables)


def assert_business_rule_checks_pass(repo_root: Path | None = None) -> pd.DataFrame:
    results = run_business_rule_checks(repo_root)
    failures = results.loc[~results["passed"]]
    if not failures.empty:
        failure_summary = " | ".join(
            f"{row.check_name}:{row.detail}" for row in failures.itertuples()
        )
        raise AssertionError("Business rule checks failed: " + failure_summary)
    return results
