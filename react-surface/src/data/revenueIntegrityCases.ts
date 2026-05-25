import type { RevenueIntegrityCase } from './types'

export const revenueIntegrityCases: RevenueIntegrityCase[] = [
  {
    id: 'RI-OR-0017',
    department: 'OR / Hospital Outpatient Surgery / Procedural Areas',
    serviceLine: 'Outpatient Surgery',
    queue: 'Prebill edit / hold',
    owner: 'Prebill Edit RN',
    priority: 'Critical',
    issueDomain: 'Billing / claim-edit failure',
    rootCauseMechanism: 'Workflow / handoff',
    currentPrimaryBlocker:
      'Distinctness modifier unresolved between coding and prebill review.',
    agingDays: 13,
    recoverabilityStatus: 'Pre-final-bill recoverable',
    dollarsAtRisk: 28450,
    dollarsRecoverableNow: 28450,
    dollarsAlreadyLost: 0,
    expectedSummary:
      'Expected outpatient technical line with distinct procedural modifier support.',
    actualSummary:
      'Case held in prebill edit queue pending final modifier validation.',
    controlFailureNarrative:
      'Documented performed procedure is complete, but the billing edit requires modifier distinctness before release to final bill.',
    recommendedAction:
      'Escalate same-day coder-prebill huddle, finalize modifier support, and release once edit clears.',
    evidenceTrace: [
      {
        step: 'Documented performed activity',
        status: 'complete',
        detail: 'OR procedure log and room timestamps confirm completed outpatient case.',
      },
      {
        step: 'Expected facility charge or review event',
        status: 'complete',
        detail: 'Expected technical case line and distinctness review requirement.',
      },
      {
        step: 'Actual posted / missing / held state',
        status: 'blocked',
        detail: 'Primary line staged, but prebill edit hold remains active.',
      },
      {
        step: 'Classification',
        status: 'warning',
        detail: 'High-risk prebill delay with same-week cash flow impact.',
      },
      {
        step: 'Routing decision',
        status: 'complete',
        detail: 'Routed to Prebill Edit RN with coding escalation support.',
      },
      {
        step: 'Suppression or why-not-billable note if applicable',
        status: 'warning',
        detail: 'Not suppressed; billable once modifier requirement is validated.',
      },
    ],
  },
  {
    id: 'RI-IR-0031',
    department: 'Radiology / Interventional Radiology',
    serviceLine: 'Interventional Radiology',
    queue: 'Charge capture pending',
    owner: 'IR Charge Analyst',
    priority: 'High',
    issueDomain: 'Charge capture failure',
    rootCauseMechanism: 'System build / interface',
    currentPrimaryBlocker:
      'Procedure completion message did not trigger expected charge event.',
    agingDays: 8,
    recoverabilityStatus: 'Pre-final-bill recoverable',
    dollarsAtRisk: 16200,
    dollarsRecoverableNow: 16200,
    dollarsAlreadyLost: 0,
    expectedSummary:
      'Expected technical charge from completed IR embolization documented in procedure log.',
    actualSummary:
      'No charge line posted; interface drop routed to charge capture queue.',
    controlFailureNarrative:
      'Performed activity is documented and complete, but expected charge creation failed due to interface timing mismatch.',
    recommendedAction:
      'Post charge from validated encounter packet and open ticket for interface retry logic.',
    evidenceTrace: [
      {
        step: 'Documented performed activity',
        status: 'complete',
        detail: 'IR procedure and sedation milestones documented as complete.',
      },
      {
        step: 'Expected facility charge or review event',
        status: 'complete',
        detail: 'Expected IR technical charge should have posted within 24 hours.',
      },
      {
        step: 'Actual posted / missing / held state',
        status: 'blocked',
        detail: 'No posted line found in charge events.',
      },
      {
        step: 'Classification',
        status: 'blocked',
        detail: 'Deterministic charge capture miss.',
      },
      {
        step: 'Routing decision',
        status: 'complete',
        detail: 'Routed to IR Charge Analyst for manual posting and interface review.',
      },
      {
        step: 'Suppression or why-not-billable note if applicable',
        status: 'warning',
        detail: 'Not suppressed; documentation supports billable technical service.',
      },
    ],
  },
  {
    id: 'RI-INF-0044',
    department: 'Outpatient Infusion / Oncology Infusion',
    serviceLine: 'Oncology Infusion',
    queue: 'Documentation pending',
    owner: 'Infusion Documentation Liaison',
    priority: 'High',
    issueDomain: 'Documentation support failure',
    rootCauseMechanism: 'Documentation behavior',
    currentPrimaryBlocker:
      'Therapeutic infusion start-stop evidence incomplete for second-hour charging.',
    agingDays: 6,
    recoverabilityStatus: 'Pre-final-bill recoverable',
    dollarsAtRisk: 9800,
    dollarsRecoverableNow: 9800,
    dollarsAlreadyLost: 0,
    expectedSummary:
      'Expected infusion-hour charge opportunity based on documented administration activity.',
    actualSummary:
      'Charge entry deferred while nursing support elements are reconciled.',
    controlFailureNarrative:
      'Performed treatment exists, but required support for distinct billable infusion time is incomplete.',
    recommendedAction:
      'Complete infusion support addendum today and release charge after rule check.',
    evidenceTrace: [
      {
        step: 'Documented performed activity',
        status: 'complete',
        detail: 'Medication administration record confirms infusion delivered.',
      },
      {
        step: 'Expected facility charge or review event',
        status: 'warning',
        detail: 'Expected additional infusion-hour charge pending support validation.',
      },
      {
        step: 'Actual posted / missing / held state',
        status: 'blocked',
        detail: 'Charge not posted due to documentation support gate.',
      },
      {
        step: 'Classification',
        status: 'warning',
        detail: 'Potential miss until support elements are finalized.',
      },
      {
        step: 'Routing decision',
        status: 'complete',
        detail: 'Routed to Documentation Liaison with nursing follow-up.',
      },
      {
        step: 'Suppression or why-not-billable note if applicable',
        status: 'warning',
        detail: 'If support remains incomplete, opportunity becomes non-billable by rule.',
      },
    ],
  },
  {
    id: 'RI-OR-0052',
    department: 'OR / Hospital Outpatient Surgery / Procedural Areas',
    serviceLine: 'Procedural Recovery',
    queue: 'Correction / rebill pending',
    owner: 'Revenue Integrity Corrections',
    priority: 'High',
    issueDomain: 'Charge integrity / configuration failure',
    rootCauseMechanism: 'CDM / rule configuration',
    currentPrimaryBlocker:
      'Prior bill released with stale CDM mapping on supply line.',
    agingDays: 21,
    recoverabilityStatus: 'Post-final-bill recoverable by correction / rebill',
    dollarsAtRisk: 23700,
    dollarsRecoverableNow: 18100,
    dollarsAlreadyLost: 5600,
    expectedSummary:
      'Expected corrected technical line with updated CDM mapping and rebill path.',
    actualSummary:
      'Final billed with under-reported supply component; correction ticket opened.',
    controlFailureNarrative:
      'Case passed final bill before updated CDM rule propagated, requiring correction and rebill recovery.',
    recommendedAction:
      'Complete corrected line replacement and push rebill before payer window closes.',
    evidenceTrace: [
      {
        step: 'Documented performed activity',
        status: 'complete',
        detail: 'Procedure and supply usage confirmed in operative records.',
      },
      {
        step: 'Expected facility charge or review event',
        status: 'complete',
        detail: 'Expected updated CDM rule to produce corrected line value.',
      },
      {
        step: 'Actual posted / missing / held state',
        status: 'warning',
        detail: 'Original billed line posted; correction workflow in progress.',
      },
      {
        step: 'Classification',
        status: 'warning',
        detail: 'Recoverable through correction / rebill with time-window dependency.',
      },
      {
        step: 'Routing decision',
        status: 'complete',
        detail: 'Routed to Revenue Integrity Corrections team.',
      },
      {
        step: 'Suppression or why-not-billable note if applicable',
        status: 'warning',
        detail: 'Not suppressed; line is billable but requires corrected submission.',
      },
    ],
  },
  {
    id: 'RI-IR-0064',
    department: 'Radiology / Interventional Radiology',
    serviceLine: 'Diagnostic Imaging',
    queue: 'Ready to final bill',
    owner: 'Radiology Revenue Integrity',
    priority: 'Medium',
    issueDomain: 'Packaged / non-billable / false-positive classification',
    rootCauseMechanism: 'Payer-policy variance',
    currentPrimaryBlocker:
      'Contrast administration appears separately but is packaged for this encounter class.',
    agingDays: 3,
    recoverabilityStatus: 'Financially closed but still compliance-relevant',
    dollarsAtRisk: 3200,
    dollarsRecoverableNow: 0,
    dollarsAlreadyLost: 0,
    expectedSummary:
      'Expected review event only; separate facility line not required under packaged logic.',
    actualSummary:
      'Potential miss candidate deterministically suppressed as non-billable by policy.',
    controlFailureNarrative:
      'Performed contrast activity is valid clinically but does not create a separately payable outpatient line in this payment context.',
    recommendedAction:
      'Retain suppression, monitor policy drift quarterly, and keep rationale attached for audit traceability.',
    suppressionNote:
      'Suppressed by packaged / integral logic; no separately billable line expected.',
    evidenceTrace: [
      {
        step: 'Documented performed activity',
        status: 'complete',
        detail: 'Contrast event and imaging completion are both documented.',
      },
      {
        step: 'Expected facility charge or review event',
        status: 'suppressed',
        detail: 'Expected policy review event, not a separately payable line.',
      },
      {
        step: 'Actual posted / missing / held state',
        status: 'suppressed',
        detail: 'No separate line posted, consistent with packaged policy.',
      },
      {
        step: 'Classification',
        status: 'suppressed',
        detail: 'False-positive suppression by deterministic billing policy.',
      },
      {
        step: 'Routing decision',
        status: 'complete',
        detail: 'Routed to monitoring lane for policy governance only.',
      },
      {
        step: 'Suppression or why-not-billable note if applicable',
        status: 'suppressed',
        detail: 'Charge treated as integral to primary study and not separately payable.',
      },
    ],
  },
  {
    id: 'RI-INF-0075',
    department: 'Outpatient Infusion / Oncology Infusion',
    serviceLine: 'Infusion Follow-up',
    queue: 'Final billed',
    owner: 'Infusion Revenue Manager',
    priority: 'Critical',
    issueDomain: 'Charge capture failure',
    rootCauseMechanism: 'People / training',
    currentPrimaryBlocker:
      'Miss discovered after payer timely filing window expired.',
    agingDays: 49,
    recoverabilityStatus: 'Post-window financially lost',
    dollarsAtRisk: 14400,
    dollarsRecoverableNow: 0,
    dollarsAlreadyLost: 14400,
    expectedSummary:
      'Expected administration line based on documented therapy completion.',
    actualSummary:
      'No line posted before final bill; recovery window has passed.',
    controlFailureNarrative:
      'Deterministic review identified a real missed charge, but delayed detection moved the case beyond financial recovery.',
    recommendedAction:
      'Treat as training and queue-governance defect; implement same-week reconciliation control.',
    evidenceTrace: [
      {
        step: 'Documented performed activity',
        status: 'complete',
        detail: 'Therapy administration and completion evidence are present.',
      },
      {
        step: 'Expected facility charge or review event',
        status: 'complete',
        detail: 'Expected administration charge should have posted pre-final bill.',
      },
      {
        step: 'Actual posted / missing / held state',
        status: 'blocked',
        detail: 'Missed line not posted before billing finalization.',
      },
      {
        step: 'Classification',
        status: 'blocked',
        detail: 'Financial loss due to timing window expiration.',
      },
      {
        step: 'Routing decision',
        status: 'complete',
        detail: 'Routed to Infusion Revenue Manager for RCA and education plan.',
      },
      {
        step: 'Suppression or why-not-billable note if applicable',
        status: 'warning',
        detail: 'Not suppressed; case was billable but no longer recoverable.',
      },
    ],
  },
  {
    id: 'RI-IR-0088',
    department: 'Radiology / Interventional Radiology',
    serviceLine: 'Interventional Coding',
    queue: 'Coding pending',
    owner: 'Radiology Coding Lead',
    priority: 'Medium',
    issueDomain: 'Coding failure',
    rootCauseMechanism: 'Coding practice',
    currentPrimaryBlocker:
      'Procedure documentation complete but coding validation not finalized.',
    agingDays: 9,
    recoverabilityStatus: 'Pre-final-bill recoverable',
    dollarsAtRisk: 11750,
    dollarsRecoverableNow: 11750,
    dollarsAlreadyLost: 0,
    expectedSummary:
      'Expected technical coding package for completed IR-guided procedure.',
    actualSummary:
      'Charge composition pending coder sign-off.',
    controlFailureNarrative:
      'Control failure is a coding queue bottleneck, not missing clinical performance.',
    recommendedAction:
      'Prioritize coding completion within 24 hours and auto-release to prebill checks.',
    evidenceTrace: [
      {
        step: 'Documented performed activity',
        status: 'complete',
        detail: 'Procedure documentation supports technical coding assignment.',
      },
      {
        step: 'Expected facility charge or review event',
        status: 'complete',
        detail: 'Expected coded line package with standard IR revenue mapping.',
      },
      {
        step: 'Actual posted / missing / held state',
        status: 'warning',
        detail: 'No final coded release yet; case remains in coding queue.',
      },
      {
        step: 'Classification',
        status: 'warning',
        detail: 'Operational delay with recoverable exposure.',
      },
      {
        step: 'Routing decision',
        status: 'complete',
        detail: 'Routed to Radiology Coding Lead for expedited closure.',
      },
      {
        step: 'Suppression or why-not-billable note if applicable',
        status: 'warning',
        detail: 'Not suppressed; expected to bill after coding completion.',
      },
    ],
  },
  {
    id: 'RI-IR-0106',
    department: 'Radiology / Interventional Radiology',
    serviceLine: 'Diagnostic Imaging',
    queue: 'Final billed',
    owner: 'Radiology Documentation Auditor',
    priority: 'High',
    issueDomain: 'Documentation support failure',
    rootCauseMechanism: 'Documentation behavior',
    currentPrimaryBlocker:
      'Required physician supervision attestation was completed after billing finalization.',
    agingDays: 34,
    recoverabilityStatus: 'Post-window financially lost',
    dollarsAtRisk: 7600,
    dollarsRecoverableNow: 0,
    dollarsAlreadyLost: 7600,
    expectedSummary:
      'Expected imaging support packet with complete physician supervision and exam linkage.',
    actualSummary:
      'Case final billed before late attestation was added, resulting in post-window loss.',
    controlFailureNarrative:
      'The performed study is documented, but required support completion lagged until after the payer timely filing window.',
    recommendedAction:
      'Treat as documentation-control defect, hard-stop finalization when supervision attestation is incomplete.',
    evidenceTrace: [
      {
        step: 'Documented performed activity',
        status: 'complete',
        detail: 'Completed imaging study and technical execution are documented.',
      },
      {
        step: 'Expected facility charge or review event',
        status: 'complete',
        detail: 'Expected support validation before final bill release.',
      },
      {
        step: 'Actual posted / missing / held state',
        status: 'blocked',
        detail: 'Final bill released before required attestation was finalized.',
      },
      {
        step: 'Classification',
        status: 'blocked',
        detail: 'Documentation support failure with post-window financial loss.',
      },
      {
        step: 'Routing decision',
        status: 'complete',
        detail: 'Routed to Documentation Auditor for policy and workflow remediation.',
      },
      {
        step: 'Suppression or why-not-billable note if applicable',
        status: 'warning',
        detail: 'Not suppressed; billability was valid but support timing failed.',
      },
    ],
  },
  {
    id: 'RI-OR-0099',
    department: 'OR / Hospital Outpatient Surgery / Procedural Areas',
    serviceLine: 'Post-bill Monitoring',
    queue: 'Closed / monitored through denial feedback only',
    owner: 'Denial Feedback Analyst',
    priority: 'Low',
    issueDomain: 'Denial feedback signal',
    rootCauseMechanism: 'Billing edit management',
    currentPrimaryBlocker:
      'Repeat denial pattern indicates stale edit logic despite corrected case.',
    agingDays: 27,
    recoverabilityStatus: 'Financially closed but still compliance-relevant',
    dollarsAtRisk: 4100,
    dollarsRecoverableNow: 0,
    dollarsAlreadyLost: 0,
    expectedSummary:
      'Expected denial feedback monitoring event tied to closed correction pathway.',
    actualSummary:
      'Case financially closed; signal retained for governance and edit tuning.',
    controlFailureNarrative:
      'No immediate dollars recoverable, but downstream denial pattern highlights a control needing refinement.',
    recommendedAction:
      'Revise denial-to-edit feedback rule and validate trend change over next 30 days.',
    evidenceTrace: [
      {
        step: 'Documented performed activity',
        status: 'complete',
        detail: 'Original procedure and billing evidence already finalized.',
      },
      {
        step: 'Expected facility charge or review event',
        status: 'complete',
        detail: 'Expected downstream denial-monitoring event after closure.',
      },
      {
        step: 'Actual posted / missing / held state',
        status: 'warning',
        detail: 'No active hold; repeat denial signal still present.',
      },
      {
        step: 'Classification',
        status: 'warning',
        detail: 'Compliance-relevant closed signal.',
      },
      {
        step: 'Routing decision',
        status: 'complete',
        detail: 'Routed to Denial Feedback Analyst for policy-change governance.',
      },
      {
        step: 'Suppression or why-not-billable note if applicable',
        status: 'suppressed',
        detail: 'Financially closed case; no active billing action expected.',
      },
    ],
  },
]
