# V1 Validation Checklist

Use this checklist to validate the frozen outpatient facility-side V1 build without expanding scope.

## Evidence Review

- Confirm each reviewed exception traces back to documented performed activity rather than inferred demand.
- Confirm the current blocker, current queue, and recoverability state are visible in the exported tables.
- Confirm at least one active post-window lost case and at least one financially closed but still compliance-relevant case are present.
- Confirm reroute history includes prior queue, current queue, and routing reason on rerouted cases.
- Confirm post-final-bill recoverable cases have matching correction-history support.

## Time-Window Review

- Review the current-state snapshot first, then compare the 30-day operating story against the same governed queues and recoverability rules.
- Use the same checklist shape for 60-day and 90-day follow-up only after the 30-day baseline is stable.

## Manual Audit Review

- Run manual sampled audit review against a mixed set of undercapture, unsupported, suppressed, correction-path, and already-lost cases.
- Verify the manual audit sample still reads like governed operational evidence rather than demo narration.
