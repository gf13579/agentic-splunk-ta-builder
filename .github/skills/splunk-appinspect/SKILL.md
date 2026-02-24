---
name: splunk-appinspect
description: Validate Splunk app packages (.tar.gz or .spl) using the provided appinspect_validator.py script and summarize results.
---

# Splunk AppInspect Validation Skill

## Purpose
Use this skill to validate a packaged Splunk app before delivery or submission. It runs the included validator script and interprets the results.

## When to Use
- You have a built .tar.gz or .spl app package and need AppInspect results.
- You must confirm the app passes required checks before Splunkbase submission.
- You need a concise, actionable summary of errors, failures, warnings, and manual checks.

## Sample Prompts
- "Run AppInspect validation on the packaged TA and summarize any failures."
- "Validate this app package and tell me what I must fix before submission."
- "Use the AppInspect validator on the .tar.gz and save the report."

## What the Script Does
The appinspect_validator.py script:
- Authenticates to Splunk AppInspect (reads APPINSPECT_USERNAME and APPINSPECT_PASSWORD from .env, or prompts interactively if not found).
- Submits the package for validation.
- Polls status until completion (with a configurable max-attempts).
- Downloads the JSON report and saves it locally.
- Prints a human-readable summary and exits with a status code.

## How to Invoke
Run from the skill folder (or provide the full path).
Do not run from inside a generated TA folder unless you use the absolute script path.

Usage:

```bash
uv run --with requests --with python-dotenv python3 appinspect_validator.py /path/to/app.tar.gz
```

If you are already in a virtual environment with requests installed:

```bash
python3 appinspect_validator.py /path/to/app.tar.gz
```

Optional flags:
- `--max-attempts 20` to poll longer
- `--quiet` to show only the summary

.env file (optional):
- Add `APPINSPECT_USERNAME` and `APPINSPECT_PASSWORD` in `.env` at the repository root to avoid interactive prompts

## What to Do With the Output
- Review the printed summary and prioritize fixes: errors first, then failures, then warnings.
- **IGNORE** the warning about check_for_updates warning in default/app.conf and mako template warnings as these are expected in UCC-based add-ons.
- Open the saved JSON report for detailed messages and locations.
- Offer to re-run validation after fixes.

## Agent Behavior
- Always include the full printed summary from generate_summary in the chat output.
- Explicitly call out any errors and failures in the response, even if the summary already shows them.

## Exit Codes
- `0` pass (no errors or failures)
- `1` fail (errors or failures present)
- `2` script or API error
