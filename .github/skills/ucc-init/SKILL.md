---
name: ucc-init
description: Initializes UCC-based Splunk TA structure and creates the initial globalConfig.json from architecture decisions made in AGENTS.md.
---

# Skill Instructions

## When to Use This Skill
Use this skill when you need to initialize a new UCC-based TA after API/vendor analysis is complete and architectural decisions are made in AGENTS.md.

## Inputs Expected From Orchestrator
- Add-on name (e.g., `TA-myservice`)
- Display name (e.g., `My Service Add-on for Splunk`)
- Primary input name (used for `ucc-gen init`)
- Auth scheme and credential fields
- Logging is always required
- Proxy tab is always required

## Scope
This skill focuses on **UCC initialization and baseline configuration only**. It does not analyze API docs or decide which components to build.

## Steps

### 1) Gather required metadata
If add-on name or display name is missing, use `ask_questions` to confirm defaults and do not proceed until confirmed.

### 2) Initialize the UCC project
Prefer `uv` when available:
```bash
uv run --with splunk-add-on-ucc-framework ucc-gen init \
  --addon-name "TA-myservice" \
  --addon-display-name "My Service Add-on for Splunk" \
  --addon-input-name myservice_input
```
Fallback to venv + pip only if `uv` is unavailable.

Do not use `--addon-rest-root <rest_root>` unless the addon-name has underscores. Rest root characters can only be alphanumeric or the hyphen character.

**Do** use `--addon-rest-root` if your add-on name contains underscores, as UCC will not automatically convert underscores to hyphens for the REST root. For example, if your add-on name is `TA_myservice`, you should specify `--addon-rest-root ta-myservice` to ensure the REST root is correctly formatted.

### 3) Baseline globalConfig.json
Ensure `globalConfig.json` exists and contains:
- `meta` with name, displayName, version, apiVersion, restRoot
- Configuration pages for account, proxy, and logging
- Empty placeholders for inputs/customSearchCommand/alerts if they will be populated later

Immediately after `ucc-gen init` generates `globalConfig.json` for the first time, update `pages.configuration.tabs` so the proxy tab is always present directly after the Account and Logging tabs:

```json
[
  {
    "name": "account"
  },
  {
    "type": "loggingTab"
  },
  {
    "type": "proxyTab"
  }
]
```

Use the minimal proxy definition from UCC:

```json
{
  "type": "proxyTab"
}
```

If the generated `tabs` array does not already match that order, rewrite it before any later skill modifies `globalConfig.json`.

### 4) Input helper stubs
`ucc-gen init` creates a single `*_helper.py` for the primary input. If multiple inputs are required, create helper stubs by copying the generated helper file and adjusting the filename to match each input name. This keeps the modular input skill focused on modifying existing helpers rather than creating new files.

## Out of Scope
- API analysis or architecture decisions
- Custom command implementation
- Modular input implementation logic
- Build, package, or AppInspect validation

## Notes
- Do not run `ucc-gen build` here; that is handled by `ucc-build-and-package`.
- If updating `package/lib/requirements.txt`, add dependencies on new lines.
