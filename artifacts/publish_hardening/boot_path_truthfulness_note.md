# Boot Path Truthfulness Note

## What changed

- The docs now lead with the Windows double-click launcher and the portable no-Python package path.
- The docs now describe demo artifact handling as reuse-or-rebuild only.
- The docs now state explicitly that validation is not run during demo boot.
- The launcher now ends with a compact summary block after Streamlit is reachable.
- The runtime now opens the browser automatically when the local server is ready.

## Artifact-handling wording alignment

- Old wording: `validate or rebuild the synthetic demo artifacts`
- New wording: `reuse existing processed demo artifacts or rebuild them if they are missing or unreadable`

This wording is now aligned in:

- [`README.md`](../../README.md)
- [`docs/recruiter_quickstart.md`](../../docs/recruiter_quickstart.md)
- [`src/ri_control_room/demo.py`](../../src/ri_control_room/demo.py)

## Launch-path alignment

- Default Windows local path: [`Launch Hospital Charge Capture Demo.cmd`](../../Launch%20Hospital%20Charge%20Capture%20Demo.cmd)
- No-Python-required handoff build: [`scripts/build_windows_portable.py`](../../scripts/build_windows_portable.py)
- Terminal fallback bootstrap: [`scripts/run_demo.py`](../../scripts/run_demo.py)

This launch hierarchy is now reflected in:

- [`README.md`](../../README.md)
- [`docs/recruiter_quickstart.md`](../../docs/recruiter_quickstart.md)
- [`docs/README.md`](../../docs/README.md)
- [`docs/OPERATING_RUNBOOK.md`](../../docs/OPERATING_RUNBOOK.md)

## Python version message

- Supported Python: `3.12`-`3.13`
- Tested on: `3.13.3`
- The demo launcher now fails early outside that supported range with the same message used in the public docs.

Aligned in:

- [`scripts/run_demo.py`](../../scripts/run_demo.py)
- [`README.md`](../../README.md)
- [`docs/recruiter_quickstart.md`](../../docs/recruiter_quickstart.md)

## Backup-path wording improvement

- The manual path now starts with explicit venv creation.
- Windows PowerShell activation is shown directly.
- A Windows no-activation fallback using the venv executables is documented.

## Updated output proof

- Primary-path output proof: [`stranger_primary_boot.txt`](./stranger_primary_boot.txt)
- Focused boot-summary proof: [`demo_boot_output.txt`](./demo_boot_output.txt)
