---
name: validate-ucc-json
description: Validates a UCC globalConfig.json against the latest version of the UCC JSON schema from the official splunk/addonfactory-ucc-generator repository.
---

# UCC JSON Schema Validation Skill

## Purpose
This skill validates a Splunk UCC (Universal Configuration Console) `globalConfig.json` file against the official UCC JSON schema. It downloads the latest schema from the splunk/addonfactory-ucc-generator repository and provides clear, actionable validation results.

## When to Use
- You have a `globalConfig.json` file that needs validation against the UCC schema.
- You want to ensure the configuration file is valid before building or packaging the add-on.
- You need to identify schema violations, missing required fields, or type mismatches.
- You want to verify compatibility with the latest version of the UCC framework.

## Sample Prompts
- "Validate the globalConfig.json file against the UCC schema."
- "Check if the globalConfig.json in the TA package is valid according to the latest UCC schema."
- "Run the UCC schema validator on package/globalConfig.json and show me any issues."

## What the Script Does
The `validate_ucc_schema.py` script:
- Downloads the latest JSON schema from the official GitHub repository.
- Loads the `globalConfig.json` file to validate.
- Validates the configuration against the schema using jsonschema.
- Generates a detailed, human-readable report of validation results.
- Prints validation status with clear categorization of issues.
- Exits with appropriate status codes for automation.

## How to Invoke
Run from the skill folder (or provide the full path).
Do not run from inside a generated TA folder unless you use the absolute script path.

Usage:

```bash
uv run --with jsonschema,requests python3 validate_ucc_schema.py /path/to/globalConfig.json
```

If you are already in a virtual environment with dependencies installed:

```bash
python3 validate_ucc_schema.py /path/to/globalConfig.json
```

Optional flags:
- `--output json` to output results as JSON
- `--schema-url <url>` to use a custom schema URL (default: official GitHub URL)
- `--quiet` to show only pass/fail status

## What to Do With the Output
- If validation passes: the configuration is compatible with the UCC framework.
- If validation fails: review the validation errors for details on what needs to be fixed.
- Fix issues according to the detailed error messages and re-run validation.
- Alternatively, consult the UCC documentation or globalConfig.json examples for guidance.

## Agent Behavior
- Always include the full printed validation report in the chat output.
- Explicitly highlight any validation errors with their paths and descriptions.
- Suggest specific fixes based on the error types encountered.

## Exit Codes
- `0` pass (validation successful)
- `1` validation failed (schema violations found)
- `2` script or file error (file not found, network error, invalid JSON, etc.)
