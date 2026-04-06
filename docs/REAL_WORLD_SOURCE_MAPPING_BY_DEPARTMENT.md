# Real-World Source Mapping By Department

Date: 2026-03-26

## Purpose

This document adds department-specific mapping notes for the three frozen V1 service-line stories. It is a realism bridge: it shows how each department would map from documented performed activity to expected facility charge logic in a real environment without pretending one generic source pattern fits the whole hospital.

## Current Implementation Reminder

The current repo already uses department-specific logic for:

- expected-charge opportunity generation
- suppression and why-not-billable logic
- current blocker classification
- owner queue routing
- queue-history churn patterns

This document explains how those same department stories would map to likely source evidence later.

## Common Mapping Rule

For every frozen V1 department, the expected-charge path should be:

1. confirm the activity actually happened
2. confirm it reached the department-specific performed state that matters for facility charging
3. confirm required support is present
4. apply packaging, integral, discontinued, distinctness, or other department-native rules
5. compare the valid opportunity to posted charge, claim-line, and edit reality
6. route only the current actionable blocker into the queue

## Outpatient Infusion / Oncology Infusion

### Likely real source domains

- MAR administration records
- infusion start and stop times
- nursing administration documentation
- pharmacy prep or dispense records
- waste support documentation
- vascular access documentation where relevant

### Key mapping rule

The anchor event is documented administration, not the treatment-plan order by itself.

### What matters most

- infusion hierarchy and timing
- sequential versus concurrent distinction
- hydration conditionality
- waste support
- separate-access support where allowed

### Common real-world failure patterns

- missing stop time
- documented administration that supports only a lesser service than initially expected
- hydration that is supportive or overlapping rather than separately billable
- waste inferred but not explicitly supported
- access work that is operationally real but integral to the visit

## Radiology / Interventional Radiology

### Likely real source domains

- performed-exam or study-completion feeds
- modality status events
- accession and exam records
- technologist workflow status
- IR procedure logs
- contrast, device, and supply linkage records

### Key mapping rule

The anchor event is completed study or completed intervention state, not the order alone.

### What matters most

- completed versus incomplete study state
- laterality and site specificity
- same-day distinctness support
- contrast linkage
- device and supply linkage for IR

### Common real-world failure patterns

- order exists but study never reaches completed state
- laterality inconsistent across documentation and coding
- contrast documented but weakly linked to the final study
- IR device or supply usage present clinically but not financially linked
- same-day repeat service that looks distinct until reviewed more carefully

## OR / Hospital Outpatient Surgery / Procedural Areas

### Likely real source domains

- case log and case state
- room and procedure timestamps
- operative or procedural documentation milestones
- implant, device, and supply usage logs
- case reconciliation records
- discontinued or aborted case status

### Key mapping rule

The anchor event is case state plus documented performed procedure activity, not the scheduled case alone.

### What matters most

- completed versus discontinued case logic
- implant and supply linkage
- timestamp-defensible case evidence
- late manual reconciliation
- more handoff-heavy workflow than simpler ambulatory settings

### Common real-world failure patterns

- scheduled case without valid completed state
- discontinued procedure misread as a full missed charge
- late supply reconciliation after apparent case closure
- inconsistent timestamps
- supplies that look chargeable but are actually integral or packaged

## Cross-Department Guardrails

- Start from performed activity, not from order count.
- Keep suppression logic as visible as missed-charge logic.
- Preserve one current blocker per active unit even when many issues exist underneath.
- Keep `denials_feedback` downstream and thin.
- Do not flatten department-native workflows into one generic source story.

## Bottom Line

Infusion depends on timed administration and support detail. Radiology / IR depends on completed-study reality plus distinctness and linkage. OR / procedural work depends on case state, supply linkage, and heavier handoff timing. That department-specific mapping discipline is what keeps the current control room hospital-native instead of generic.
