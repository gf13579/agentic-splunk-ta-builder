---
name: ucc-build-and-package
description: Builds and packages a UCC-based Splunk TA using ucc-gen build and ucc-gen package.
---

# Skill Instructions

## When to Use This Skill
Use this skill after UCC initialization and after all updates to `globalConfig.json`, helper files, and custom command logic are complete.

## Preconditions
- `globalConfig.json` is valid and up to date
- Modular input helpers and custom command logic files are in place
- Any required dependencies are listed in `package/lib/requirements.txt`
- `package/README.txt` is updated with add-on overview, setup instructions, modular input documentation (if applicable), custom search command usage examples (if applicable), and troubleshooting guidance

## Build
Run from the TA root and always point `--source` to `package/`:

⚠️ **CRITICAL**: UCC's build process internally runs `pip install` to download dependencies from `package/lib/requirements.txt`. Using `uv run --with` creates an ephemeral Python environment without `pip`, causing the build to fail. **Use a persistent virtual environment instead:**

```bash
cd TA-myservice

# Create and activate virtual environment (one-time setup)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install UCC framework
pip install splunk-add-on-ucc-framework

# Build the add-on
ucc-gen build --source package --ta-version 1.0.0
```

Note: `ucc-gen build` may update `globalConfig.json` (for example, schema version). If the system reports the file changed, re-open it before making further edits.

## Package
Package the built add-on from the TA root (using the same venv):
```bash
cd TA-myservice
source .venv/bin/activate  # Activate the same venv used for build
ucc-gen package --path output/TA-myservice
```

## Optional Validation Hook
If validation is requested, run the `splunk-appinspect` skill after packaging and summarize results.

## Notes
- The `--source` parameter must point to `package/`.
- Do not modify `globalConfig.json` here; this skill is execution-only.
