---
name: deploy-to-test-splunk
description: Deploy a Splunk TA package (.tar.gz) to a test Splunk instance using credentials in .env.
---

# Deploy to Test Splunk Skill

## Purpose
Deploy a built Splunk TA package to a test Splunk server via the Splunk REST API.
The script reads credentials and the target URL from `.env` in the repo root.

## Required Inputs
- Path to a TA package (`.tar.gz`)

## Environment (.env at repo root)
Provide these variables in `.env`:
- `SPLUNK_USERNAME`
- `SPLUNK_PASSWORD`
- `SPLUNK_API_URL` (example: `https://splunk-03:8089`)

## What It Does
- Loads `.env` from the repository root
- Uploads the package to `SPLUNK_API_URL/services/apps/local`
- Installs or updates the app on the server

## How to Invoke
Run from the repo root (recommended). Use `--insecure` for typical test instances with self-signed certs:

```bash
uv run --with requests --with python-dotenv python3 .github/skills/deploy-to-test-splunk/deploy_to_test_splunk.py /path/to/TA-myaddon-1.0.0.tar.gz --insecure
```

Optional flags:
- `--app-name <name>` to override the app name (default: inferred from filename)
- `--insecure` to disable TLS verification for self-signed test certs (recommended for test servers)

Example:

```bash
uv run --with requests --with python-dotenv python3 .github/skills/deploy-to-test-splunk/deploy_to_test_splunk.py TA-threat-intel/TA-threat-intel-1.0.0.tar.gz --insecure
```

## Exit Codes
- `0` success
- `1` request or upload error
- `2` missing input or environment variables
