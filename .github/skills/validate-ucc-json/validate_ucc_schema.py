#!/usr/bin/env python3
"""
UCC JSON Schema Validator
Validates Splunk UCC globalConfig.json against the official UCC JSON schema.
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from jsonschema import validate, ValidationError, Draft7Validator
from datetime import datetime

# Official UCC schema URL
DEFAULT_SCHEMA_URL = (
    "https://raw.githubusercontent.com/splunk/addonfactory-ucc-generator/"
    "main/splunk_add_on_ucc_framework/schema/schema.json"
)


def download_schema(schema_url: str) -> Dict[str, Any]:
    """
    Download the JSON schema from GitHub.
    
    Args:
        schema_url: URL to the JSON schema
        
    Returns:
        dict: Parsed JSON schema
    """
    print(f"Downloading UCC schema from:\n  {schema_url}\n")
    
    try:
        response = requests.get(schema_url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("❌ Error: Request timeout while downloading schema")
        sys.exit(2)
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error: Failed to download schema (HTTP {response.status_code})")
        print(f"   {e}")
        sys.exit(2)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: Network error while downloading schema: {e}")
        sys.exit(2)
    
    try:
        schema = response.json()
        print(f"✓ Schema downloaded successfully\n")
        return schema
    except json.JSONDecodeError as e:
        print(f"❌ Error: Downloaded schema is not valid JSON: {e}")
        sys.exit(2)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load and parse the globalConfig.json file.
    
    Args:
        config_path: Path to globalConfig.json
        
    Returns:
        dict: Parsed JSON configuration
    """
    print(f"Loading configuration from:\n  {config_path}\n")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"✓ Configuration loaded successfully\n")
        return config
    except FileNotFoundError:
        print(f"❌ Error: Configuration file not found: {config_path}")
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Configuration file is not valid JSON: {e}")
        sys.exit(2)
    except IOError as e:
        print(f"❌ Error: Could not read configuration file: {e}")
        sys.exit(2)


def validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Validate configuration against schema and collect all errors.
    
    Args:
        config: The configuration to validate
        schema: The JSON schema
        
    Returns:
        tuple: (is_valid, list of errors)
    """
    errors: List[Dict[str, Any]] = []
    
    # Use Draft7Validator to collect all validation errors
    validator = Draft7Validator(schema)
    
    for error in sorted(validator.iter_errors(config), key=lambda e: str(e.path)):
        error_info = {
            "path": list(error.path) if error.path else ["root"],
            "message": error.message,
            "validator": error.validator,
            "instance_type": type(error.instance).__name__,
        }
        
        # Add schema details if available
        if hasattr(error, 'schema'):
            if isinstance(error.schema, dict):
                if 'type' in error.schema:
                    error_info["expected_type"] = error.schema['type']
                if 'enum' in error.schema:
                    error_info["allowed_values"] = error.schema['enum']
        
        errors.append(error_info)
    
    is_valid = len(errors) == 0
    return is_valid, errors


def format_path(path_list: List[Any]) -> str:
    """Format a JSON path as a string."""
    if not path_list:
        return "$"
    return "$." + ".".join(str(p) for p in path_list)


def print_validation_report(is_valid: bool, errors: List[Dict[str, Any]], quiet: bool = False) -> None:
    """
    Print a formatted validation report.
    
    Args:
        is_valid: Whether validation passed
        errors: List of validation errors
        quiet: If True, only show pass/fail
    """
    if quiet:
        status = "PASS ✓" if is_valid else "FAIL ✗"
        print(f"Validation: {status}")
        return
    
    print("=" * 70)
    print("UCC JSON SCHEMA VALIDATION REPORT")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Status: {'PASS ✓' if is_valid else 'FAIL ✗'}")
    print(f"Total Issues: {len(errors)}")
    print("=" * 70)
    
    if is_valid:
        print("\n✓ Configuration is valid according to the UCC schema.\n")
        return
    
    print(f"\n✗ Found {len(errors)} validation error(s):\n")
    
    for i, error in enumerate(errors, 1):
        path = format_path(error["path"])
        print(f"{i}. Path: {path}")
        print(f"   Error: {error['message']}")
        print(f"   Validator: {error['validator']}")
        
        if "expected_type" in error:
            print(f"   Expected type: {error['expected_type']}")
        
        if "allowed_values" in error:
            print(f"   Allowed values: {error['allowed_values']}")
        
        print()


def output_json_report(is_valid: bool, errors: List[Dict[str, Any]], config_path: str, schema_url: str) -> str:
    """
    Generate a JSON report of validation results.
    
    Args:
        is_valid: Whether validation passed
        errors: List of validation errors
        config_path: Path to the config file
        schema_url: URL of the schema
        
    Returns:
        str: JSON report as string
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "status": "pass" if is_valid else "fail",
        "config_file": config_path,
        "schema_url": schema_url,
        "validation_errors": len(errors),
        "errors": errors,
    }
    return json.dumps(report, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Validate UCC globalConfig.json against the official UCC schema"
    )
    parser.add_argument(
        "config_path",
        help="Path to the globalConfig.json file to validate"
    )
    parser.add_argument(
        "--schema-url",
        default=DEFAULT_SCHEMA_URL,
        help="URL to the UCC JSON schema (default: official GitHub version)"
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show pass/fail status"
    )
    
    args = parser.parse_args()
    
    # Download schema
    schema = download_schema(args.schema_url)
    
    # Load configuration
    config = load_config(args.config_path)
    
    # Validate
    is_valid, errors = validate_config(config, schema)
    
    # Output results
    if args.output == "json":
        report_json = output_json_report(is_valid, errors, args.config_path, args.schema_url)
        print(report_json)
    else:
        print_validation_report(is_valid, errors, args.quiet)
    
    # Exit with appropriate code
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
