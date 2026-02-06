# Splunk AppInspect Skill

A GitHub Copilot skill for validating Splunk app packages using the AppInspect REST API.

## Quick Start

```bash
# Make the script executable
chmod +x appinspect_validator.py

# Run validation
./appinspect_validator.py my_app.tar.gz

# Or with Python
python3 appinspect_validator.py my_app.tar.gz
```

## Authentication

### Option 1: Interactive (prompted each time)
```bash
./appinspect_validator.py my_app.tar.gz
# You'll be prompted for username and password
```

### Option 2: Environment Variable (recommended)
```bash
# Set the token once
export APPINSPECT_TOKEN="your_token_here"

# Then run without prompts
./appinspect_validator.py my_app.tar.gz
```

The script will display your token after first authentication so you can set it as an environment variable.

## Usage Examples

### Basic validation
```bash
./appinspect_validator.py my_app.tar.gz
```

### Quiet mode (summary only)
```bash
./appinspect_validator.py my_app.tar.gz --quiet
```

### Extended polling for large apps
```bash
./appinspect_validator.py my_app.tar.gz --max-attempts 20
```

### Use in CI/CD
```bash
#!/bin/bash
# In your CI pipeline

export APPINSPECT_TOKEN="${SECRET_APPINSPECT_TOKEN}"

if ./appinspect_validator.py dist/my_app.tar.gz; then
    echo "Validation passed! Proceeding with deployment..."
else
    echo "Validation failed! Fix issues before deploying."
    exit 1
fi
```

## Output

The script generates:

1. **Console output**: Formatted summary with color-coded issues
2. **JSON report**: `appinspect_report_<request_id>.json` with full details

### Exit Codes

- `0` - Validation passed (no errors or failures)
- `1` - Validation failed (errors or failures present)
- `2` - API error, timeout, or other issue

## Example Output

```
✓ Using token from APPINSPECT_TOKEN environment variable
Submitting package: my_app.tar.gz
✓ Package submitted successfully
  Request ID: 1234abcd-5678-efgh-9012-ijklmnopqrst

Polling validation status...
  [1/15] Status: PROCESSING
  [2/15] Status: PROCESSING
  [3/15] Status: SUCCESS
✓ Validation completed!

Retrieving validation report...
✓ Report saved to: appinspect_report_1234abcd-5678-efgh-9012-ijklmnopqrst.json

======================================================================
SPLUNK APPINSPECT VALIDATION SUMMARY
======================================================================

📊 Overview:
  ✓ Success:         145
  ✗ Failures:          2
  ⚠ Warnings:          5
  ❌ Errors:            0
  👁 Manual Checks:    1
  ⊘ Not Applicable:   50
  ⊗ Skipped:           0

✗ FAILURES - Must fix for Splunkbase submission (2):
----------------------------------------------------------------------

1. check_readme_exists
   Group: packaging_standards
   • README file not found in app root directory
     📄 File: N/A
     🔖 Code: MISSING_README

2. check_license_file
   Group: licensing
   • LICENSE or COPYING file not found
     🔖 Code: MISSING_LICENSE

⚠ WARNINGS - Recommended fixes for best practices (5):
----------------------------------------------------------------------

1. check_app_description
   Group: appapproval
   • App description in app.conf should be more detailed
     📄 File: default/app.conf (line 5)

...

======================================================================
❌ FAIL: 2 critical issue(s) must be resolved
   Fix all errors and failures before submitting to Splunkbase.
======================================================================
```

## Common Issues and Fixes

| Issue | Fix |
|-------|-----|
| Authentication failed | Verify credentials at splunk.com |
| File not found | Check package path and file extension |
| Validation timeout | Increase `--max-attempts` for large apps |
| Token expired | Remove and re-authenticate to get new token |

## Requirements

- Python 3.6+
- `requests` library: `pip install requests`
- Splunk.com account (free)

## For GitHub Copilot

This skill is automatically available when the `.github/skills/splunk-appinspect/` directory is present in your repository. Copilot will suggest using it when working with Splunk apps.

Ask Copilot:
- "Validate my Splunk app with AppInspect"
- "Check if my app passes AppInspect requirements"
- "Run AppInspect on the package"

## Resources

- [AppInspect API Documentation](https://dev.splunk.com/enterprise/docs/developapps/testvalidate/appinspect/useappinspectapi/)
- [Splunk Packaging Standards](https://dev.splunk.com/enterprise/docs/developapps/createapps/createpackaging/)
- [AppInspect CLI Alternative](https://dev.splunk.com/enterprise/docs/developapps/testvalidate/appinspect/)
