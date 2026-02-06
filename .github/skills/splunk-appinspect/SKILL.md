---
name: splunk-appinspect
description: Validate Splunk app packages (.tar.gz) using the Splunk AppInspect REST API. Submits packages for validation, polls for results, and provides detailed summaries of failures, warnings, and errors with actionable remediation guidance.
---

# Splunk AppInspect Validation Skill

This skill enables automated validation of Splunk app packages using the Splunk AppInspect REST API. It handles authentication, package submission, result polling, and generates comprehensive reports of validation issues.

## When to Use This Skill

Use this skill when:
- Validating a Splunk app package before submission to Splunkbase
- Checking app compliance with Splunk's packaging standards
- Troubleshooting app validation failures
- Running AppInspect checks as part of CI/CD pipelines
- Getting detailed explanations of validation errors and warnings

## Prerequisites

- A Splunk.com account (free to create at splunk.com)
- A packaged Splunk app in `.tar.gz` or `.spl` format
- Internet connectivity to reach appinspect.splunk.com

## Authentication

The skill will prompt for:
1. **Splunk.com username**: Your splunk.com email address
2. **Splunk.com password**: Your splunk.com password

Alternatively, you can set the `APPINSPECT_TOKEN` environment variable with a previously obtained bearer token to skip authentication.

## API Endpoints

```
Base URL: https://appinspect.splunk.com/v1
Login URL: https://api.splunk.com/2.0/rest/login/splunk
Validation: POST /app/validate
Status: GET /app/validate/status/{request_id}
Report: GET /app/report/{request_id}
```

## Workflow

1. **Authenticate**: Obtain bearer token from Splunk API
2. **Submit Package**: Upload .tar.gz file for validation
3. **Poll Status**: Check validation progress (max 15 attempts, 20s intervals)
4. **Retrieve Report**: Fetch JSON report with detailed results
5. **Parse & Summarize**: Analyze failures, errors, and warnings
6. **Generate Summary**: Provide actionable remediation guidance

## Implementation Guidelines

### 1. Authentication Flow

```python
import requests
from getpass import getpass
import os

def authenticate():
    """Get bearer token for AppInspect API"""
    token = os.getenv("APPINSPECT_TOKEN")
    if token:
        return token
    
    username = input("Splunk.com username: ")
    password = getpass("Splunk.com password: ")
    
    response = requests.get(
        "https://api.splunk.com/2.0/rest/login/splunk",
        auth=(username, password)
    )
    response.raise_for_status()
    
    token = response.json()["data"]["token"]
    print(f"\nAuthentication successful!")
    print(f"To skip this step in future, set:\nAPPINSPECT_TOKEN={token}")
    return token
```

### 2. Submit Package

```python
def submit_package(token, package_path):
    """Submit app package for validation"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Cache-Control": "no-cache"
    }
    
    with open(package_path, 'rb') as f:
        files = {"app_package": f}
        response = requests.post(
            "https://appinspect.splunk.com/v1/app/validate",
            headers=headers,
            files=files
        )
    
    response.raise_for_status()
    request_id = response.json()["request_id"]
    print(f"Package submitted. Request ID: {request_id}")
    return request_id
```

### 3. Poll for Status

```python
import time

def poll_status(token, request_id, max_attempts=15):
    """Poll validation status until complete"""
    headers = {"Authorization": f"Bearer {token}"}
    status_url = f"https://appinspect.splunk.com/v1/app/validate/status/{request_id}"
    
    for attempt in range(1, max_attempts + 1):
        print(f"Checking status... ({attempt}/{max_attempts})")
        response = requests.get(status_url, headers=headers)
        response.raise_for_status()
        
        status = response.json()["status"]
        
        if status == "SUCCESS":
            print("✓ Validation complete!")
            return True
        elif status == "FAILURE":
            print("✗ Validation failed")
            return False
        
        print(f"  Status: {status} - waiting 20s...")
        time.sleep(20)
    
    print("⚠ Timeout: validation did not complete")
    return False
```

### 4. Retrieve Report (JSON Format)

**IMPORTANT**: Request JSON format for programmatic parsing:

```python
def get_report(token, request_id):
    """Retrieve validation report in JSON format"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"  # Request JSON, not HTML
    }
    
    report_url = f"https://appinspect.splunk.com/v1/app/report/{request_id}"
    response = requests.get(report_url, headers=headers)
    response.raise_for_status()
    
    return response.json()
```

### 5. Parse and Summarize Results

The JSON report structure:

```json
{
  "request_id": "...",
  "summary": {
    "error": 2,
    "failure": 5,
    "warning": 12,
    "success": 145,
    "manual_check": 3,
    "not_applicable": 50,
    "skipped": 0
  },
  "reports": [
    {
      "app_name": "my_app",
      "app_version": "1.0.0",
      "groups": [
        {
          "name": "packaging_standards",
          "checks": [
            {
              "name": "check_app_conf_exists",
              "result": "success",
              "messages": []
            },
            {
              "name": "check_readme_exists",
              "result": "failure",
              "messages": [
                {
                  "message": "README file not found in app",
                  "code": "MISSING_README",
                  "filename": null,
                  "line": null
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

**Parsing Implementation**:

```python
def parse_report(report):
    """Parse report and extract actionable issues"""
    summary = report.get("summary", {})
    reports = report.get("reports", [])
    
    issues = {
        "errors": [],
        "failures": [],
        "warnings": [],
        "manual_checks": []
    }
    
    for app_report in reports:
        app_name = app_report.get("app_name", "unknown")
        
        for group in app_report.get("groups", []):
            group_name = group.get("name", "unknown")
            
            for check in group.get("checks", []):
                result = check.get("result", "")
                check_name = check.get("name", "")
                messages = check.get("messages", [])
                
                if result == "error":
                    issues["errors"].append({
                        "check": check_name,
                        "group": group_name,
                        "messages": messages
                    })
                elif result == "failure":
                    issues["failures"].append({
                        "check": check_name,
                        "group": group_name,
                        "messages": messages
                    })
                elif result == "warning":
                    issues["warnings"].append({
                        "check": check_name,
                        "group": group_name,
                        "messages": messages
                    })
                elif result == "manual_check":
                    issues["manual_checks"].append({
                        "check": check_name,
                        "group": group_name,
                        "messages": messages
                    })
    
    return summary, issues
```

### 6. Generate Summary

```python
def generate_summary(summary, issues):
    """Generate human-readable summary with remediation guidance"""
    
    print("\n" + "="*70)
    print("SPLUNK APPINSPECT VALIDATION SUMMARY")
    print("="*70)
    
    print(f"\n📊 Overview:")
    print(f"  ✓ Success:        {summary.get('success', 0)}")
    print(f"  ✗ Failures:       {summary.get('failure', 0)}")
    print(f"  ⚠ Warnings:       {summary.get('warning', 0)}")
    print(f"  ❌ Errors:         {summary.get('error', 0)}")
    print(f"  👁 Manual Checks: {summary.get('manual_check', 0)}")
    print(f"  ⊘ Not Applicable: {summary.get('not_applicable', 0)}")
    
    # Errors (critical)
    if issues["errors"]:
        print(f"\n❌ ERRORS ({len(issues['errors'])}) - Must fix:")
        print("-" * 70)
        for i, error in enumerate(issues["errors"], 1):
            print(f"\n{i}. {error['check']} [{error['group']}]")
            for msg in error["messages"]:
                print(f"   • {msg.get('message', 'No message')}")
                if msg.get('filename'):
                    print(f"     File: {msg['filename']}")
                if msg.get('line'):
                    print(f"     Line: {msg['line']}")
    
    # Failures (must fix for Splunkbase)
    if issues["failures"]:
        print(f"\n✗ FAILURES ({len(issues['failures'])}) - Must fix:")
        print("-" * 70)
        for i, failure in enumerate(issues["failures"], 1):
            print(f"\n{i}. {failure['check']} [{failure['group']}]")
            for msg in failure["messages"]:
                print(f"   • {msg.get('message', 'No message')}")
                if msg.get('filename'):
                    print(f"     File: {msg['filename']}")
                if msg.get('line'):
                    print(f"     Line: {msg['line']}")
    
    # Warnings (recommended fixes)
    if issues["warnings"]:
        print(f"\n⚠ WARNINGS ({len(issues['warnings'])}) - Recommended fixes:")
        print("-" * 70)
        for i, warning in enumerate(issues["warnings"], 1):
            print(f"\n{i}. {warning['check']} [{warning['group']}]")
            for msg in warning["messages"]:
                print(f"   • {msg.get('message', 'No message')}")
    
    # Manual checks
    if issues["manual_checks"]:
        print(f"\n👁 MANUAL CHECKS ({len(issues['manual_checks'])}) - Requires review:")
        print("-" * 70)
        for i, check in enumerate(issues["manual_checks"], 1):
            print(f"\n{i}. {check['check']} [{check['group']}]")
            for msg in check["messages"]:
                print(f"   • {msg.get('message', 'No message')}")
    
    # Overall verdict
    print("\n" + "="*70)
    total_issues = len(issues["errors"]) + len(issues["failures"])
    
    if total_issues == 0:
        print("✅ PASS: App meets all required validation checks!")
        if issues["warnings"]:
            print("   Consider addressing warnings for best practices.")
    else:
        print(f"❌ FAIL: {total_issues} critical issue(s) must be resolved")
        print("   Fix all errors and failures before submitting to Splunkbase.")
    
    print("="*70 + "\n")
```

## Common Validation Issues and Fixes

### Packaging Standards

| Issue | Fix |
|-------|-----|
| Missing README | Add `README.txt` or `README.md` to app root |
| Missing app.conf | Add `default/app.conf` with required fields |
| Invalid app.manifest | Ensure JSON is valid and includes required fields |
| Incorrect permissions | Set `.conf` files to 644, directories to 755 |

### Configuration Files

| Issue | Fix |
|-------|-----|
| Invalid .conf syntax | Check for proper stanza format `[stanza]` |
| Deprecated settings | Remove or update deprecated configuration options |
| Missing required fields | Add `label`, `version`, `author` to app.conf |

### Security

| Issue | Fix |
|-------|-----|
| Hardcoded credentials | Move to `local/` (not packaged) or use passwords.conf |
| Insecure permissions | Review and restrict file permissions |
| Unsafe Python code | Avoid `eval()`, `exec()`, sanitize inputs |

### Python/Modular Inputs

| Issue | Fix |
|-------|-----|
| Python 2 syntax | Update to Python 3 compatible code |
| Missing requirements | Add dependencies to `lib/` or document in README |
| Import errors | Ensure all modules are included or documented |

## Full Example Script

See `appinspect_validator.py` in this skill folder for a complete implementation.

## Exit Codes

- `0`: Validation passed (no errors or failures)
- `1`: Validation failed (errors or failures present)
- `2`: API error or timeout

## Tips for Success

1. **Test locally first**: Run basic checks before API validation
2. **Review Splunk docs**: Check packaging standards at dev.splunk.com
3. **Fix errors first**: Prioritize errors, then failures, then warnings
4. **Iterate quickly**: Use the token to avoid re-authenticating
5. **Save reports**: Keep JSON reports for tracking fixes over time

## References

- [AppInspect API Docs](https://dev.splunk.com/enterprise/docs/developapps/testvalidate/appinspect/useappinspectapi/)
- [Packaging Standards](https://dev.splunk.com/enterprise/docs/developapps/createapps/createpackaging/)
- [AppInspect CLI](https://dev.splunk.com/enterprise/docs/developapps/testvalidate/appinspect/installappinspect/)

## Troubleshooting

**Authentication fails**: Verify credentials at splunk.com, check 2FA settings

**Validation timeout**: Large apps may take longer; increase `max_attempts`

**403 Forbidden**: Token expired; re-authenticate

**SSL errors**: Check network proxy settings, update CA certificates

**File not found**: Verify package path and .tar.gz format
