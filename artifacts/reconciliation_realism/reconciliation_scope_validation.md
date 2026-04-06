# Charge Reconciliation Monitor Realism Validation

## What changed

- `Aging By Service Line` now stays inside the same governed department/service-line filter slice as the rest of the page, while keeping recently worked-down in-scope reconciliation lines visible when recent queue history exists.
- `Control Completion Trend` no longer compares unlike measures.
- Old semantics: cumulative `completed_within_policy` versus point-in-time `open_unreconciled`.
- New semantics: point-in-time `open_unreconciled` versus point-in-time `overdue_unreconciled`.
- The latest trend point is calibrated to the current filtered backlog state so the endpoint stays honest in the page's current synthetic snapshot model.

## Scoping issue found

There was not a true cross-filter leak showing unrelated current service lines. The real problem was thinner and more confusing: the page only summarized the current open reconciliation queue, so broad views hid recently worked-down in-scope service lines and filtered OR views collapsed to an empty-looking service-line section even when recent reconciliation activity existed in queue history.

## Representative slice notes

- `All departments`: moving backlog. Infusion remains the current open backlog driver at `4` open / `2` overdue, while `Outpatient Surgery` stays visible as a recently worked-down in-scope line. The trend steps from `3` to `5`, works down to `4`, and closes at the current backlog state of `4` open / `2` overdue.
- `OR / procedural`: recent workdown, now clear. `Outpatient Surgery` is the only service line shown. The trend starts at `1` open and steps down to `0`, which tells the handoff-sensitive OR story without leaking Infusion.
- `Infusion`: recurring lag pattern. `Infusion` is the only service line shown. The trend builds from `0` to `2`, then to `4`, with overdue pressure appearing after the backlog sits long enough to cross policy timing.

## Browser proof

- Before: `charge_reconciliation_before.png`
- After, broad view: `charge_reconciliation_after_broad.png`
- After, OR / procedural: `charge_reconciliation_after_or.png`
- After, Infusion: `charge_reconciliation_after_infusion.png`

## Focused validation

- `python -m pytest tests/test_pages_remaining.py -q`
- Coverage added for:
  - latest reconciliation trend point matches the current filtered backlog
  - service-line rows stay scoped to representative filtered slices
  - broad slice shows more than one believable in-scope service line when recent filtered history supports it
