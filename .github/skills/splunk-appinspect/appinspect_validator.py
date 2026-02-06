#!/usr/bin/env python3
"""
Splunk AppInspect Validator
Validates Splunk app packages using the AppInspect REST API.
"""

import os
import sys
import time
import requests
from getpass import getpass
import argparse
import json
from typing import Dict, List, Tuple, Any

# Splunk API endpoints
BASE_URL = "https://appinspect.splunk.com/v1"
LOGIN_URL = "https://api.splunk.com/2.0/rest/login/splunk"
VALIDATE_URL = f"{BASE_URL}/app/validate"
STATUS_URL = f"{BASE_URL}/app/validate/status"
REPORT_URL = f"{BASE_URL}/app/report"


def authenticate() -> str:
    """
    Authenticate with Splunk API and return bearer token.
    
    Returns:
        str: Bearer token for API authentication
    """
    token = os.getenv("APPINSPECT_TOKEN")
    if token:
        print("✓ Using token from APPINSPECT_TOKEN environment variable")
        return token

    print("APPINSPECT_TOKEN not found. Please provide credentials.\n")
    username = input("Splunk.com username: ")
    password = getpass("Splunk.com password: ")

    print("\nAuthenticating...")
    try:
        response = requests.get(LOGIN_URL, auth=(username, password))
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            print("❌ Authentication failed: Invalid username or password")
        else:
            print(f"❌ Authentication failed: {e}")
        sys.exit(2)
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error during authentication: {e}")
        sys.exit(2)

    data = response.json()
    token = data["data"]["token"]
    
    print("✓ Authentication successful!\n")
    print("To skip authentication in future runs, set this environment variable:")
    print(f"  export APPINSPECT_TOKEN={token}\n")
    
    return token


def submit_app(token: str, app_package_path: str) -> str:
    """
    Submit an app package for validation.
    
    Args:
        token: Bearer token for authentication
        app_package_path: Path to the .tar.gz app package
        
    Returns:
        str: Request ID for the validation job
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Cache-Control": "no-cache"
    }
    
    print(f"Submitting package: {app_package_path}")
    
    try:
        with open(app_package_path, "rb") as f:
            files = {"app_package": f}
            response = requests.post(VALIDATE_URL, headers=headers, files=files)
        response.raise_for_status()
    except FileNotFoundError:
        print(f"❌ Error: Package file not found: {app_package_path}")
        sys.exit(2)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error submitting package: {e}")
        sys.exit(2)

    data = response.json()
    request_id = data["request_id"]
    print(f"✓ Package submitted successfully")
    print(f"  Request ID: {request_id}\n")
    
    return request_id


def poll_status(token: str, request_id: str, max_attempts: int = 15) -> bool:
    """
    Poll validation status until complete or timeout.
    
    Args:
        token: Bearer token for authentication
        request_id: Validation request ID
        max_attempts: Maximum number of polling attempts
        
    Returns:
        bool: True if validation completed successfully
    """
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Polling validation status...")
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(f"{STATUS_URL}/{request_id}", headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error checking status: {e}")
            return False

        data = response.json()
        status = data["status"]
        
        print(f"  [{attempt}/{max_attempts}] Status: {status}")
        
        if status == "SUCCESS":
            print("✓ Validation completed!\n")
            return True
        elif status == "FAILURE":
            print("✗ Validation processing failed\n")
            return False
        
        if attempt < max_attempts:
            time.sleep(20)
    
    print("⚠ Timeout: Validation did not complete within the polling window\n")
    return False


def retrieve_report(token: str, request_id: str) -> Dict[str, Any]:
    """
    Retrieve validation report in JSON format.
    
    Args:
        token: Bearer token for authentication
        request_id: Validation request ID
        
    Returns:
        dict: JSON report data
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",  # Request JSON format
        "Cache-Control": "no-cache"
    }
    
    print("Retrieving validation report...")
    
    try:
        response = requests.get(f"{REPORT_URL}/{request_id}", headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error retrieving report: {e}")
        sys.exit(2)
    
    report = response.json()
    
    # Save JSON report to file
    report_filename = f"appinspect_report_{request_id}.json"
    with open(report_filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    print(f"✓ Report saved to: {report_filename}\n")
    
    return report


def parse_report(report: Dict[str, Any]) -> Tuple[Dict[str, int], Dict[str, List[Dict]]]:
    """
    Parse validation report and extract issues.
    
    Args:
        report: JSON report data
        
    Returns:
        tuple: (summary dict, issues dict)
    """
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
        app_version = app_report.get("app_version", "unknown")
        
        for group in app_report.get("groups", []):
            group_name = group.get("name", "unknown")
            
            for check in group.get("checks", []):
                result = check.get("result", "")
                check_name = check.get("name", "")
                messages = check.get("messages", [])
                
                issue_data = {
                    "check": check_name,
                    "group": group_name,
                    "app": app_name,
                    "version": app_version,
                    "messages": messages
                }
                
                if result == "error":
                    issues["errors"].append(issue_data)
                elif result == "failure":
                    issues["failures"].append(issue_data)
                elif result == "warning":
                    issues["warnings"].append(issue_data)
                elif result == "manual_check":
                    issues["manual_checks"].append(issue_data)
    
    return summary, issues


def print_issue_section(title: str, emoji: str, issues: List[Dict], show_details: bool = True):
    """Print a formatted section of issues."""
    if not issues:
        return
    
    print(f"\n{emoji} {title} ({len(issues)}):")
    print("-" * 70)
    
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. {issue['check']}")
        print(f"   Group: {issue['group']}")
        
        if show_details:
            for msg in issue["messages"]:
                message_text = msg.get("message", "No message provided")
                print(f"   • {message_text}")
                
                # Show file/line info if available
                if msg.get("filename"):
                    location = f"     📄 File: {msg['filename']}"
                    if msg.get("line"):
                        location += f" (line {msg['line']})"
                    print(location)
                
                # Show error code if available
                if msg.get("code"):
                    print(f"     🔖 Code: {msg['code']}")
        else:
            # Just show count of messages
            msg_count = len(issue["messages"])
            if msg_count > 0:
                print(f"   {msg_count} message(s)")


def generate_summary(summary: Dict[str, int], issues: Dict[str, List[Dict]], verbose: bool = True):
    """
    Generate and print human-readable summary.
    
    Args:
        summary: Summary statistics
        issues: Categorized issues
        verbose: Show detailed messages
    """
    print("\n" + "=" * 70)
    print("SPLUNK APPINSPECT VALIDATION SUMMARY")
    print("=" * 70)
    
    # Overview statistics
    print(f"\n📊 Overview:")
    print(f"  ✓ Success:        {summary.get('success', 0):>4}")
    print(f"  ✗ Failures:       {summary.get('failure', 0):>4}")
    print(f"  ⚠ Warnings:       {summary.get('warning', 0):>4}")
    print(f"  ❌ Errors:         {summary.get('error', 0):>4}")
    print(f"  👁 Manual Checks: {summary.get('manual_check', 0):>4}")
    print(f"  ⊘ Not Applicable: {summary.get('not_applicable', 0):>4}")
    print(f"  ⊗ Skipped:        {summary.get('skipped', 0):>4}")
    
    # Detailed issue sections
    print_issue_section("ERRORS - Critical issues that must be fixed", 
                       "❌", issues["errors"], verbose)
    
    print_issue_section("FAILURES - Must fix for Splunkbase submission", 
                       "✗", issues["failures"], verbose)
    
    print_issue_section("WARNINGS - Recommended fixes for best practices", 
                       "⚠", issues["warnings"], verbose)
    
    print_issue_section("MANUAL CHECKS - Requires human review", 
                       "👁", issues["manual_checks"], verbose)
    
    # Overall verdict
    print("\n" + "=" * 70)
    total_critical = len(issues["errors"]) + len(issues["failures"])
    
    if total_critical == 0:
        print("✅ PASS: App meets all required validation checks!")
        if issues["warnings"]:
            print(f"   Consider addressing {len(issues['warnings'])} warning(s) for best practices.")
        if issues["manual_checks"]:
            print(f"   Review {len(issues['manual_checks'])} manual check(s) before submission.")
    else:
        print(f"❌ FAIL: {total_critical} critical issue(s) must be resolved")
        print("   Fix all errors and failures before submitting to Splunkbase.")
    
    print("=" * 70 + "\n")
    
    return total_critical


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Validate Splunk app packages using AppInspect API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s my_app.tar.gz
  %(prog)s my_app.spl --max-attempts 20
  %(prog)s my_app.tar.gz --quiet

Environment Variables:
  APPINSPECT_TOKEN    Bearer token to skip authentication
        """
    )
    
    parser.add_argument(
        "app_package_path",
        help="Path to the app package (.tar.gz or .spl)"
    )
    
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=15,
        help="Maximum polling attempts (default: 15)"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Show only summary, hide detailed messages"
    )
    
    args = parser.parse_args()
    
    # Verify file exists
    if not os.path.isfile(args.app_package_path):
        print(f"❌ Error: File not found: {args.app_package_path}")
        sys.exit(2)
    
    try:
        # Step 1: Authenticate
        token = authenticate()
        
        # Step 2: Submit package
        request_id = submit_app(token, args.app_package_path)
        
        # Step 3: Poll for completion
        if not poll_status(token, request_id, args.max_attempts):
            print("Validation did not complete successfully")
            sys.exit(2)
        
        # Step 4: Retrieve report
        report = retrieve_report(token, request_id)
        
        # Step 5: Parse and summarize
        summary, issues = parse_report(report)
        total_critical = generate_summary(summary, issues, verbose=not args.quiet)
        
        # Exit with appropriate code
        sys.exit(1 if total_critical > 0 else 0)
        
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
