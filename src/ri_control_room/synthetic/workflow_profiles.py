from __future__ import annotations


DEFAULT_WORKFLOW_PROFILE: dict[str, object] = {
    "current_stage_age_days": 2,
    "stage_path": (),
    "stage_segment_days": (),
    "routing_reason": "Initial queue placement under deterministic workflow rules.",
    "transition_reasons": (),
    "late_charge_days_after_service": 0,
    "final_bill_days_after_service": 1,
    "rebill_flag": False,
    "corrected_claim_flag": False,
}


SCENARIO_WORKFLOW_PROFILES: dict[str, dict[str, object]] = {
    "missing_stop_time": {
        "current_stage_age_days": 2,
        "stage_path": ("Documentation pending",),
        "stage_segment_days": (2,),
        "routing_reason": "Timed infusion cannot clear until stop time support is completed.",
        "transition_reasons": (
            "Timed infusion cannot clear until stop time support is completed.",
        ),
    },
    "waste_documented": {
        "current_stage_age_days": 2,
        "stage_path": ("Charge capture pending",),
        "stage_segment_days": (2,),
        "routing_reason": "Documented waste is waiting on charge-entry follow-through before bill drop.",
        "transition_reasons": (
            "Documented waste is waiting on charge-entry follow-through before bill drop.",
        ),
    },
    "waste_missing": {
        "current_stage_age_days": 5,
        "stage_path": (
            "Charge capture pending",
            "Documentation pending",
            "Coding pending",
            "Prebill edit / hold",
        ),
        "stage_segment_days": (1, 1, 2, 5),
        "routing_reason": "Undocumented waste escalated from coding review into modifier hold.",
        "transition_reasons": (
            "Charge reconciliation flagged missing waste support before bill drop.",
            "Department follow-through could not validate waste support after revenue-integrity handoff.",
            "Resolved waste support rerouted into coding review for modifier alignment.",
            "Residual waste-support risk remained after coding review and moved into prebill hold.",
        ),
    },
    "concurrent_infusion": {
        "current_stage_age_days": 1,
        "stage_path": ("Documentation pending", "Coding pending"),
        "stage_segment_days": (1, 1),
        "routing_reason": "Concurrent infusion requires coding distinctness review.",
        "transition_reasons": (
            "Concurrent infusion support was queued for documentation clarification before coding release.",
            "Documentation follow-through completed and rerouted into coding distinctness review.",
        ),
    },
    "late_charge_risk": {
        "current_stage_age_days": 6,
        "stage_path": ("Charge capture pending",),
        "stage_segment_days": (6,),
        "routing_reason": "Charge entry missed the local timing window after department handoff.",
        "transition_reasons": (
            "Charge entry missed the local timing window after department handoff.",
        ),
    },
    "laterality_missing": {
        "current_stage_age_days": 4,
        "stage_path": ("Documentation pending",),
        "stage_segment_days": (4,),
        "routing_reason": "Study laterality support is missing and keeps the case in documentation review.",
        "transition_reasons": (
            "Study laterality support is missing and keeps the case in documentation review.",
        ),
    },
    "device_link_gap": {
        "current_stage_age_days": 7,
        "stage_path": ("Documentation pending",),
        "stage_segment_days": (7,),
        "routing_reason": "IR device linkage failed across workflow handoff and aged past recovery window.",
        "transition_reasons": (
            "IR device linkage failed across workflow handoff and aged past recovery window.",
        ),
    },
    "distinctness_required": {
        "current_stage_age_days": 4,
        "stage_path": ("Documentation pending", "Coding pending"),
        "stage_segment_days": (1, 4),
        "routing_reason": "Distinctness review rerouted from documentation support to coding.",
        "transition_reasons": (
            "Same-day study distinctness needed documentation-side source clarification before coding release.",
            "Distinctness review rerouted from documentation support to coding.",
        ),
    },
    "late_post_risk": {
        "current_stage_age_days": 7,
        "stage_path": (
            "Charge capture pending",
            "Coding pending",
            "Prebill edit / hold",
        ),
        "stage_segment_days": (2, 2, 7),
        "routing_reason": "Late-posted activity arrived after bill-prep handoff and triggered a hold.",
        "transition_reasons": (
            "Late-post risk opened charge reconciliation after activity arrived outside the standard post window.",
            "Late-post review cleared charge capture but rerouted the account into coding for claim readiness review.",
            "Late-posted activity arrived after bill-prep handoff and triggered a hold.",
        ),
        "late_charge_days_after_service": 7,
    },
    "discontinued_partial": {
        "current_stage_age_days": 4,
        "stage_path": ("Documentation pending", "Coding pending", "Prebill edit / hold"),
        "stage_segment_days": (2, 2, 4),
        "routing_reason": "Discontinued case moved from coding review into prebill hold.",
        "transition_reasons": (
            "Discontinued procedure note was incomplete and routed to documentation support.",
            "Department support closed the note gap and sent the case to coding for discontinued-procedure review.",
            "Discontinued case moved from coding review into prebill hold.",
        ),
    },
    "timestamp_missing": {
        "current_stage_age_days": 6,
        "stage_path": ("Charge capture pending", "Documentation pending"),
        "stage_segment_days": (1, 6),
        "routing_reason": "Missing case timestamp kept the account in documentation review past the window.",
        "transition_reasons": (
            "Charge reconciliation opened first while procedural activity looked incomplete at initial review.",
            "Missing case timestamp kept the account in documentation review past the window.",
        ),
    },
    "correction_rebill_pending": {
        "current_stage_age_days": 6,
        "stage_path": (
            "Charge capture pending",
            "Coding pending",
            "Prebill edit / hold",
            "Correction / rebill pending",
        ),
        "stage_segment_days": (1, 2, 3, 6),
        "routing_reason": "Post-bill variance opened a correction / rebill workflow.",
        "transition_reasons": (
            "Post-procedure reconciliation opened on the original billing path before claim finalization.",
            "Original reconciliation findings rerouted into coding review for procedure and supply alignment.",
            "Coding review released into a prebill hold after bill-prep variance remained unresolved.",
            "Post-bill variance opened a correction / rebill workflow.",
        ),
        "rebill_flag": True,
        "corrected_claim_flag": True,
    },
    "incomplete_ir_case": {
        "current_stage_age_days": 4,
        "rebill_flag": False,
        "corrected_claim_flag": True,
    },
}


def get_workflow_profile(scenario_code: str) -> dict[str, object]:
    profile = DEFAULT_WORKFLOW_PROFILE.copy()
    profile.update(SCENARIO_WORKFLOW_PROFILES.get(str(scenario_code), {}))
    if not profile["stage_path"]:
        profile["stage_path"] = ()
    if not profile["stage_segment_days"]:
        profile["stage_segment_days"] = ()
    if not profile["transition_reasons"]:
        profile["transition_reasons"] = ()
    return profile
