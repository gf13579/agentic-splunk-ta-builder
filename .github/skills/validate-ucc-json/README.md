# UCC JSON Schema Validation Skill

Validates Splunk UCC `globalConfig.json` files against the official UCC JSON schema from the `splunk/addonfactory-ucc-generator` repository.

## Quick Start

```bash
uv run --with jsonschema,requests python3 validate_ucc_schema.py /path/to/globalConfig.json
```

## Features

- **Downloads latest schema** from the official GitHub repository
- **Comprehensive validation** with detailed error reporting
- **Multiple output formats** (human-readable text or JSON)
- **Clear path identification** for easy debugging of configuration issues

## Usage

See [SKILL.md](SKILL.md) for complete documentation.
