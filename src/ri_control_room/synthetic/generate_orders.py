from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pandas as pd

from ri_control_room.synthetic.generate_encounters import (
    OUTPUT_FILENAME as ENCOUNTERS_FILENAME,
    get_processed_dir,
    write_encounters_parquet,
)


OUTPUT_FILENAME = "orders.parquet"


def load_encounters_df(repo_root: Path | None = None) -> pd.DataFrame:
    processed_dir = get_processed_dir(repo_root)
    path = processed_dir / ENCOUNTERS_FILENAME
    if not path.exists():
        write_encounters_parquet(repo_root)
    return pd.read_parquet(path)


def _order_blueprints(encounter: pd.Series) -> list[dict[str, object]]:
    scenario_code = str(encounter["scenario_code"])

    if encounter["department"].startswith("Outpatient Infusion"):
        blueprints = [
            {
                "activity_role": "primary_infusion",
                "procedure_description": "Primary therapeutic infusion administration",
            }
        ]
        if scenario_code == "hydration_conditional":
            blueprints.append(
                {
                    "activity_role": "hydration",
                    "procedure_description": "Same-day hydration administration",
                }
            )
        elif scenario_code == "sequential_infusion":
            blueprints.append(
                {
                    "activity_role": "sequential_infusion",
                    "procedure_description": "Sequential infusion add-on",
                }
            )
        elif scenario_code == "concurrent_infusion":
            blueprints.append(
                {
                    "activity_role": "concurrent_infusion",
                    "procedure_description": "Concurrent infusion add-on",
                }
            )
        elif scenario_code == "access_site_integral":
            blueprints.append(
                {
                    "activity_role": "access_site",
                    "procedure_description": "Separate access-site administration",
                }
            )
        elif scenario_code in {"waste_documented", "waste_missing"}:
            blueprints.append(
                {
                    "activity_role": "waste_review",
                    "procedure_description": "Drug waste review support",
                }
            )
        return blueprints

    if encounter["department"].startswith("Radiology"):
        blueprints = [
            {
                "activity_role": "primary_study",
                "procedure_description": "Primary completed imaging study",
            }
        ]
        if scenario_code == "distinctness_required":
            blueprints.append(
                {
                    "activity_role": "distinct_repeat",
                    "procedure_description": "Same-day repeat imaging study",
                }
            )
        elif scenario_code in {"contrast_linked_clean", "contrast_packaged"}:
            blueprints.append(
                {
                    "activity_role": "contrast_support",
                    "procedure_description": "Contrast administration support",
                }
            )
        elif scenario_code == "device_link_gap":
            blueprints.append(
                {
                    "activity_role": "device_linkage",
                    "procedure_description": "IR device linkage support",
                }
            )
        return blueprints

    blueprints = [
        {
            "activity_role": "primary_procedure",
            "procedure_description": "Primary outpatient procedure",
        }
    ]
    if scenario_code in {
        "implant_linked_clean",
        "implant_link_gap",
        "device_supply_clean",
        "supply_integral",
        "late_post_risk",
    }:
        blueprints.append(
            {
                "activity_role": "implant_supply",
                "procedure_description": "Implant or supply usage",
            }
        )
    return blueprints


def generate_orders_df(repo_root: Path | None = None) -> pd.DataFrame:
    encounters = load_encounters_df(repo_root)
    rows: list[dict[str, object]] = []

    for _, encounter in encounters.iterrows():
        blueprints = _order_blueprints(encounter)
        for order_index, blueprint in enumerate(blueprints):
            order_status = "completed"
            if encounter["scenario_code"] in {
                "incomplete_study_nonbillable",
                "incomplete_ir_case",
            }:
                order_status = "incomplete"
            if encounter["scenario_code"] in {
                "discontinued_partial",
                "discontinued_no_charge",
            }:
                order_status = "discontinued"

            order_type = "procedure"
            if encounter["department"].startswith("Outpatient Infusion"):
                order_type = "medication_administration"
            elif encounter["department"].startswith("Radiology"):
                order_type = "imaging_study"

            rows.append(
                {
                    "order_id": f"ORD-{encounter['encounter_id']}-{order_index + 1}",
                    "encounter_id": encounter["encounter_id"],
                    "department": encounter["department"],
                    "service_line": encounter["service_line"],
                    "scenario_code": encounter["scenario_code"],
                    "order_type": order_type,
                    "order_status": order_status,
                    "ordered_ts": encounter["scheduled_service_ts"] - timedelta(hours=4 - order_index),
                    "scheduled_service_ts": encounter["scheduled_service_ts"],
                    "procedure_code": f"{encounter['encounter_id'][:3]}-{order_index + 1:02d}",
                    "procedure_description": blueprint["procedure_description"],
                    "activity_role": blueprint["activity_role"],
                    "order_group": encounter["scenario_code"],
                    "laterality_required_flag": encounter["scenario_code"]
                    in {"laterality_missing", "site_specific_clean"},
                    "site_required_flag": encounter["scenario_code"]
                    in {"laterality_missing", "site_specific_clean"},
                    "distinctness_support_required_flag": encounter["scenario_code"]
                    in {"distinctness_required", "concurrent_infusion", "sequential_infusion"},
                    "contrast_or_device_expected_flag": encounter["scenario_code"]
                    in {
                        "contrast_linked_clean",
                        "contrast_packaged",
                        "device_link_gap",
                        "implant_linked_clean",
                        "implant_link_gap",
                        "device_supply_clean",
                        "late_post_risk",
                    },
                }
            )

    df = pd.DataFrame(rows).sort_values(["encounter_id", "order_id"]).reset_index(drop=True)
    df["ordered_ts"] = pd.to_datetime(df["ordered_ts"])
    df["scheduled_service_ts"] = pd.to_datetime(df["scheduled_service_ts"])
    return df


def write_orders_parquet(repo_root: Path | None = None) -> Path:
    df = generate_orders_df(repo_root)
    output_path = get_processed_dir(repo_root) / OUTPUT_FILENAME
    df.to_parquet(output_path, index=False)
    return output_path


def main() -> Path:
    return write_orders_parquet()


if __name__ == "__main__":
    main()
