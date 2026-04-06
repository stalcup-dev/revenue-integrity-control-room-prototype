# Decision Pack Freshness Patch

## Purpose

Tighten freshness and current-state framing for the Revenue Integrity Decision Pack so it reads as a bounded deterministic snapshot, not as a broader validation claim.

## Recommended disclaimer block near the top

Add this block immediately under the title:

```md
> Current deterministic snapshot of the governed app state for this build and current filtered slice.
> This memo is synthetic/public-safe, facility-side only, outpatient-first, and bounded to the currently implemented control-room scope.
> Validation status should be read exactly as shown from the current run manifest. If the manifest is not current, treat this as a snapshot sample rather than validation proof.
> Scenario values are what-if estimates, not forecasts. Denial signals remain downstream evidence only.
```

## Current-state wording to make the memo read as a deterministic snapshot

Preferred phrases:

- `current deterministic snapshot`
- `current governed slice`
- `current build state`
- `current filtered control-room view`
- `current what-if estimate`
- `thin downstream evidence layer`

Avoid phrases that imply:

- broader validation than the current manifest shows
- production readiness
- enterprise scope
- forecast certainty
- denials as an operating center

## Old wording -> new wording patches

| Old wording | Risk | New wording |
| --- | --- | --- |
| `Validation status: Not yet run` | Reads stale and undercuts governance if shown without context. | `Validation status from current run manifest: Not yet run. Treat this memo as a current snapshot sample until the manifest is refreshed.` |
| `Revenue Integrity Decision Pack` | Fine as a title, but needs bounded context immediately below it. | Keep the title, then add the disclaimer block above. |
| `Recoverable now vs already lost` | Fine, but can sound more universal than intended if unsupported by scope language. | `Recoverable now vs already lost in the current governed slice` |
| `Top owner queue` | Fine, but better if it reads as current-state, not as a general organizational truth. | `Top owner queue in the current slice` |
| `Top service line / department of concern` | Can sound like broad institutional ranking. | `Top service line / department in the current slice` |
| `The leading control failure is Documentation support failure...` | Can clash with the ranked queue section if the top queue is different. | `Current summary signal: documentation support failure is the leading issue-domain signal in this slice, while the top urgent queue grouping remains billing/edit work.` |
| `The current pattern is mostly documentation-related.` | Too broad and too final sounding. | `The current slice is documentation-heavy at the issue-domain level, but queue urgency is distributed across documentation, billing/edit, and coding work.` |
| `Scenario snapshot uses the current Scenario Lab v0 default lever targets for the same filtered slice.` | Good, but can still sound like a forecast if read quickly. | `Scenario snapshot uses the current Scenario Lab v0 default lever targets for the same filtered slice and should be read as a transparent what-if estimate only.` |
| `Denials are evidence-only, not the product center.` | Good guardrail, but could be made more explicit. | `Denial signals remain downstream evidence only and do not redefine the product center.` |

## Explicit caveats that should remain visible

- Synthetic/public-safe data only
- Current implemented scope only
- Facility-side only
- Outpatient-first
- Deterministic-first
- Scenario results are what-if estimates, not forecasts
- Denial signals are downstream evidence only

## Recommended top-of-memo structure

1. Title
2. Disclaimer block
3. Build timestamp and manifest-status line
4. Executive summary

That order keeps the memo from sounding smoother or more validated than the underlying manifest state.

## Note on avoiding stale-sounding language in demos

In the live demo, say:

- `This is a current deterministic snapshot.`
- `Validation should be read exactly from the current manifest.`
- `If the sample memo is older than the current build, use it only as a format example.`

Do not say:

- `This is the validated leadership pack`
- `This is the final export`
- `This proves the scenario`
- `This gives a forecast`
