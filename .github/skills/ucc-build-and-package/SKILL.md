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

## Build
Run from the TA root and always point `--source` to `package/`:

Prefer `uv` when available:
```bash
cd TA-myservice
uv run --with splunk-add-on-ucc-framework ucc-gen build --source package --ta-version 1.0.0
```

Note: `ucc-gen build` may update `globalConfig.json` (for example, schema version). If the system reports the file changed, re-open it before making further edits.

Fallback to venv + pip only if `uv` is unavailable.

## Package
Package the built add-on from the TA root:
```bash
cd TA-myservice
uv run --with splunk-add-on-ucc-framework ucc-gen package --path output/TA-myservice
```

## Optional Validation Hook
If validation is requested, run the `splunk-appinspect` skill after packaging and summarize results.

## Notes
- The `--source` parameter must point to `package/`.
- Do not modify `globalConfig.json` here; this skill is execution-only.
