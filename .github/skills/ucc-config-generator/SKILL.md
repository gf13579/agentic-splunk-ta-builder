---
name: ucc-config-generator
description: Deprecated legacy skill. Use ucc-init and ucc-build-and-package instead.
---

# Skill Instructions

## Status
This skill is deprecated and should not be used for new work.

## Replacement
Use these skills instead:
- `ucc-init` for UCC initialization and initial `globalConfig.json`
- `ucc-build-and-package` for `ucc-gen build` and `ucc-gen package`

## Rationale
The previous ucc-config-generator combined API analysis, architecture decisions, UCC init, build, packaging, and documentation. These responsibilities now belong to the main orchestration agent (AGENTS.md) and the focused skills listed above.
