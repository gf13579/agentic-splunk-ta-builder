"""Deploy a Splunk TA package to a test Splunk instance.

Reads SPLUNK_USERNAME, SPLUNK_PASSWORD, and SPLUNK_API_URL from .env in repo root.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import requests
from dotenv import dotenv_values


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for _ in range(6):
        if (current / ".git").exists() or (current / ".env").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    return start.resolve().parents[3]


def load_env(repo_root: Path) -> dict:
    env = dotenv_values(repo_root / ".env")
    # Let real environment variables override .env values.
    env.update({k: v for k, v in os.environ.items() if v is not None})
    return env


def infer_app_name(package_path: Path) -> str:
    name = package_path.name
    if name.endswith(".tar.gz"):
        name = name[:-7]
    match = re.match(r"^(?P<app>.+?)-\d+\.\d+.*$", name)
    if match:
        return match.group("app")
    return name


def deploy_package(
    package_path: Path,
    api_url: str,
    username: str,
    password: str,
    app_name: str,
    verify_tls: bool,
) -> None:
    host = urlparse(api_url).hostname
    if not host:
        raise ValueError("SPLUNK_API_URL must include a hostname.")

    remote_path = f"/tmp/{package_path.name}"
    scp_target = f"{host}:{remote_path}"
    scp_result = subprocess.run(
        ["scp", str(package_path), scp_target],
        check=False,
        capture_output=True,
        text=True,
    )
    if scp_result.returncode != 0:
        raise RuntimeError(
            f"SCP failed ({scp_result.returncode}): {scp_result.stderr.strip()}"
        )

    url = f"{api_url.rstrip('/')}/services/apps/local"
    data = {
        "name": remote_path,
        "filename": "true",
        "update": "true",
    }
    response = requests.post(
        url,
        data=data,
        auth=(username, password),
        verify=verify_tls,
        timeout=120,
    )
    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"Install failed ({response.status_code}): {response.text.strip()}"
        )

    restart_url = f"{api_url.rstrip('/')}/services/server/control/restart"
    restart_response = requests.post(
        restart_url,
        auth=(username, password),
        verify=verify_tls,
        timeout=120,
    )
    if restart_response.status_code not in (200, 201):
        raise RuntimeError(
            "Restart failed "
            f"({restart_response.status_code}): {restart_response.text.strip()}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deploy a Splunk TA package to a test Splunk instance."
    )
    parser.add_argument("package", help="Path to the .tar.gz package")
    parser.add_argument(
        "--app-name",
        help="Optional app name override (default: inferred from filename)",
    )
    parser.add_argument(
        "--insecure",
        action="store_true",
        help="Disable TLS verification (use only with self-signed test certs)",
    )
    args = parser.parse_args()

    package_path = Path(args.package)
    if not package_path.exists():
        print(f"Package not found: {package_path}")
        return 2

    repo_root = find_repo_root(Path(__file__))
    env = load_env(repo_root)
    username = env.get("SPLUNK_USERNAME")
    password = env.get("SPLUNK_PASSWORD")
    api_url = env.get("SPLUNK_API_URL")

    if not username or not password or not api_url:
        print("Missing SPLUNK_USERNAME, SPLUNK_PASSWORD, or SPLUNK_API_URL in .env")
        return 2

    app_name = args.app_name or infer_app_name(package_path)

    try:
        deploy_package(
            package_path=package_path,
            api_url=api_url,
            username=username,
            password=password,
            app_name=app_name,
            verify_tls=not args.insecure,
        )
        print(f"Uploaded {package_path.name} as app '{app_name}' to {api_url}")
        return 0
    except Exception as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
