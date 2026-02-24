# Splunk AppInspect Skill

Validate a packaged Splunk app by running the provided appinspect_validator.py script and summarizing results.

Used over `ucc-gen validate` as a) that requires libmagic and b) that uses local appinspect, which may not provide as complete/up-to-date testing as the REST API.

## Quick Start

```bash
# Recommended: run with uv (no local install required)
uv run --with requests python3 appinspect_validator.py /path/to/app.tar.gz

# Or run inside a venv with requests installed
python3 appinspect_validator.py /path/to/app.tar.gz
```

## Authentication

The script reads credentials from the `.env` file in the repository root:
- `APPINSPECT_USERNAME` - Your Splunk.com username
- `APPINSPECT_PASSWORD` - Your Splunk.com password

If the `.env` file is missing or credentials are not found, the script will prompt you interactively for your Splunk.com username and password.

## Usage

```bash
# Basic validation
python3 appinspect_validator.py /path/to/app.tar.gz

# Quiet summary only
python3 appinspect_validator.py /path/to/app.tar.gz --quiet

# Poll longer for large apps
python3 appinspect_validator.py /path/to/app.tar.gz --max-attempts 20
```

## Output

The script:
- Prints a summary of errors, failures, warnings, and manual checks.
- Saves a JSON report as `appinspect_report_<request_id>.json`.

Agent workflow:
- Copy the full printed summary into the chat response.
- Call out any errors and failures explicitly, even if they appear in the summary.

### What to do next

1. Fix all errors and failures first.
2. Review warnings and manual checks.
3. Re-run validation until the package passes.

## Exit Codes

- `0` pass (no errors or failures)
- `1` fail (errors or failures present)
- `2` script or API error

## Sample Copilot Prompts

- "Run AppInspect validation on the packaged TA and summarize failures."
- "Validate this app package and tell me what must be fixed before submission."
- "Use the AppInspect validator on the .tar.gz and save the report."
