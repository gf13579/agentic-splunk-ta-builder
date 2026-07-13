---
name: splunk-custom-command
description: Generates Splunk custom search commands for UCC-managed add-ons. Defines commands in globalConfig.json and creates Python implementation files in package/bin/ for API-based data retrieval, enrichment, or search operations.
---

# Splunk Custom Search Command Skill

## Purpose
This skill generates custom search commands (also known as custom SPL commands) for UCC-managed Splunk add-ons. Custom search commands extend Splunk's Search Processing Language (SPL) to enable users to interact with external APIs, perform lookups, enrich data, or generate events directly from search queries.

**Assumption:** API/vendor documentation analysis and architectural decisions are already completed in AGENTS.md. This skill should not re-analyze the API; it should implement the previously defined commands and arguments.

## Requirement Levels

Use the following interpretation rules when applying this skill:

- **UCC schema requirements** are mandatory and are called out explicitly in this file.
- **Architecture decisions** such as whether the add-on uses a configurable `api_url`, a fixed endpoint, or proxy-aware HTTP clients should come from `AGENTS.md` or the current task design.
- **Code templates** in this skill are examples. They are not a requirement to add every field shown in the example to every add-on.
- If you copy an example that uses `api_url`, adapt it to the add-on's architecture instead of assuming `api_url` is always required.

## When to Use This Skill

Create a **custom search command** when:

- **API provides search/lookup/enrichment endpoints** (e.g., `/users/{id}`, `/search`, `/threat-intel/lookup`)
- **Analysts need on-demand API queries** from SPL (e.g., `| myapicommand user="john"`)
- **Results should be returned on-demand**, not pre-indexed
- **Data is more suitable for enrichment** than long-term storage
- **API data supplements existing Splunk events** (e.g., user details, threat intelligence)

**Examples:**
- `| threatintel_lookup ip="1.2.3.4"` - Look up threat intelligence for an IP address
- `| userinfo_enrich user="jsmith"` - Enrich events with user profile data
- `| apiquery endpoint="/metrics" timerange="1h"` - Query API metrics on demand

**Do NOT use this for:**
- Continuous data collection (use modular inputs/scripted inputs instead)
- Event ingestion that should be indexed (use modular inputs)
- Alert response actions (use alert actions instead)

## Command Types

UCC supports three types of custom search commands:

1. **Generating** - Creates new events from scratch (does not require input events)
   - Use for: API queries that generate new data
   - Example: `| myapi_generate endpoint="/events" count=100`

2. **Streaming** - Processes events one at a time, can add/modify/filter fields
   - Use for: Enrichment, transformation, filtering
   - Example: `... | myapi_enrich field=user`

3. **Transforming** - Processes all events together, can aggregate or reduce
   - Use for: API calls that need to process batches
   - Example: `... | myapi_batch action="analyze"`

**This skill focuses on generating commands** for API data retrieval, as they are most common for API-based add-ons.

---

## Making changes to globalConfig.json

Before writing any replacements to large json files like globalConfig.json, output the target structure as a code block and reason about which existing text it replaces in full.

Replace the entire object (e.g. "configuration") when possible to avoid syntax errors and incorrect nesting caused by simultaneous replacement using the multi_replace_string_in_file tool that may conflict with each other.


## Implementation Steps

### Step 1: Define Command in globalConfig.json

Add a `customSearchCommand` array at the root level of `globalConfig.json` (same level as `meta` and `pages`). Example below:

```json
{
    "meta": {...},
    "pages": {...},
    "customSearchCommand": [
        {
            "commandName": "myapicommand",
            "fileName": "myapicommand_logic.py",
            "commandType": "generating",
            "requiredSearchAssistant": true,
            "description": "Query the MyAPI service for data based on specified parameters.",
            "syntax": "myapicommand query=<string> limit=<int> [field=<string>]",
            "usage": "public",
            "arguments": [
                {
                    "name": "query",
                    "required": true,
                    "validate": {
                        "type": "RegularExpression"
                    }
                },
                {
                    "name": "limit",
                    "required": false,
                    "defaultValue": 100,
                    "validate": {
                        "type": "Integer",
                        "minimum": 1,
                        "maximum": 1000
                    }
                },
                {
                    "name": "field",
                    "required": false
                }
            ]
        }
    ]
}
```

## ⚠️ CRITICAL: Common Schema Validation Mistakes

**These errors occur frequently and prevent the build from succeeding. Read carefully:**

### Mistake 1: Location in globalConfig.json

❌ **WRONG** - `customSearchCommand` inside `pages`:
```json
{
    "meta": {...},
    "pages": {
        "configuration": {...},
        "customSearchCommand": [...]  // ❌ WRONG LOCATION!
    }
}
```

✅ **CORRECT** - `customSearchCommand` at ROOT level (same as `meta` and `pages`):
```json
{
    "meta": {...},
    "pages": {...},
    "customSearchCommand": [...]  // ✅ CORRECT!
}
```

### Mistake 2: Property Names

❌ **WRONG** - Using incorrect property names:
```json
{
    "name": "mycommand",              // ❌ Should be "commandName"
    "displayName": "My Command",      // ❌ Not a valid property
    "filename": "mycommand.py",       // ❌ Should be "fileName" (camelCase)
    "description": "..."
}
```

✅ **CORRECT** - Using UCC schema property names:
```json
{
    "commandName": "mycommand",       // ✅ CORRECT
    "fileName": "mycommand_logic.py", // ✅ CORRECT (camelCase)
    "commandType": "generating",      // ✅ REQUIRED
    "arguments": [...]                // ✅ REQUIRED (even if empty, need at least one)
}
```

### Mistake 3: Command Naming Convention

❌ **WRONG** - Command name contains underscores, hyphens, or uppercase:
```json
{
    "commandName": "my_command",      // ❌ Underscores not allowed
    "commandName": "my-command",      // ❌ Hyphens not allowed
    "commandName": "MyCommand"        // ❌ Uppercase not allowed
}
```

✅ **CORRECT** - Only lowercase alphanumerics (a-z, 0-9):
```json
{
    "commandName": "mycommand",       // ✅ GOOD
    "commandName": "tireputationip",  // ✅ GOOD (all lowercase, no separators)
    "commandName": "ipreputation",    // ✅ GOOD
    "commandName": "userinfo"         // ✅ GOOD
}
```

**Pattern rule:** `^[a-z0-9]+$` - If your command name contains underscores or hyphens, remove them.

### Mistake 4: Missing Required Properties

❌ **WRONG** - Omitting required fields:
```json
{
    "commandName": "mycommand",
    "fileName": "mycommand_logic.py"
    // ❌ Missing commandType and arguments!
}
```

✅ **CORRECT** - All required properties present:
```json
{
    "commandName": "mycommand",
    "fileName": "mycommand_logic.py",
    "commandType": "generating",      // ✅ REQUIRED
    "arguments": [                    // ✅ REQUIRED
        {
            "name": "query",
            "required": true
        }
    ]
}
```

**Required fields:** `commandName`, `fileName`, `commandType`, `arguments` (array with at least 1 item)

### Validate Before Building

After editing `globalConfig.json` with your custom commands, **always validate** using the validate-ucc-json skill before running the build:

```bash
uv run --with jsonschema,requests python3 .github/skills/validate-ucc-json/validate_ucc_schema.py /path/to/globalConfig.json
```

This catches schema errors early and shows you exactly what's wrong.

---

### Step 2: Create the Python Logic File

**CRITICAL:** UCC generates a wrapper file (e.g., `myapicommand.py`) automatically. You must create the **logic file** specified in `fileName` (e.g., `myapicommand_logic.py`) in the `package/bin/` directory. The logic file is independent of splunklib.searchcommands - it's generic Python code that the wrapper will call via its `generate` function.

**Shared configuration note:** Many examples below read `api_url` and credentials from account configuration. That is a common pattern, not a universal requirement. If the add-on targets one fixed vendor endpoint, you may keep the endpoint constant and only fetch credentials from configuration.

**File naming convention:**
- **Wrapper file** (auto-generated by UCC): Matches `commandName` (e.g., `myapicommand.py`)
- **Logic file** (YOU create): Matches `fileName` in config (e.g., `myapicommand_logic.py`)

**Required function:** For generating commands, your logic file must contain a `generate` function. The logic file must not import from splunklib.searchcommands directly; instead, it should define the `generate` function that the wrapper will call.

When yielding results, be sure to included a "_raw" field - set to json.dumps(your_result_dict) along with "_time" in epoch format, typically set to `time.time()` unless your API provides a timestamp.

### Step 3: Update add-on dependencies

If the logic file imports third-party libraries (anything beyond the default UCC set), update `package/lib/requirements.txt` in the add-on:

- `ucc-gen init` provides `splunktaucclib`, `splunk-sdk`, and `solnlib` by default.
- Add any new dependency you import (e.g., `requests`, `dateutil`) on a new line in `package/lib/requirements.txt`.
- Keep this in sync with the Python code so `ucc-gen build` vendors the dependency into `output/<TA>/lib`.

## Configuration Reference

### Required attributes in `customSearchCommand`:

| Attribute | Type | Description |
|-----------|------|-------------|
| `commandName` | string | Name of the command users will type in SPL (e.g., `myapicommand`). **Must contain only lowercase letters and numbers (a-z, 0-9) — no underscores, hyphens, or special characters.** |
| `fileName` | string | Name of YOUR Python logic file (e.g., `myapicommand_logic.py`) |
| `commandType` | string | One of: `generating`, `streaming`, or `eventing` |
| `arguments` | array | List of command arguments with validation rules |

⚠️ Command Naming Rule: The commandName must match the regex pattern ^[a-z0-9]+$. Use alphanumerics only. Do NOT use underscores, hyphens, or other special characters. For example, use ipreputation instead of ip_reputation.

### Optional attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `requiredSearchAssistant` | boolean | Enable search assistant (syntax help in UI). Default: false |
| `description` | string | Description shown in search assistant (required if `requiredSearchAssistant=true`) |
| `syntax` | string | Syntax pattern for search assistant (required if `requiredSearchAssistant=true`) |
| `usage` | string | One of: `public`, `private`, `deprecated` (required if `requiredSearchAssistant=true`) |

### Argument attributes:

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | string | Argument name (must match Python Option name) |
| `required` | boolean | Whether argument is mandatory |
| `defaultValue` | string/number | Default value if not provided |
| `validate` | object | Validation rules (see below) |

### Validation types:

UCC supports these validators from `splunklib.searchcommands.validators`:

1. **Integer** - Validates integer with optional `minimum` and `maximum`
   ```json
   {"type": "Integer", "minimum": 1, "maximum": 1000}
   ```

2. **Float** - Validates float with optional `minimum` and `maximum`
   ```json
   {"type": "Float", "minimum": 0.0, "maximum": 100.0}
   ```

3. **Boolean** - Validates boolean (true/false)
   ```json
   {"type": "Boolean"}
   ```

4. **Fieldname** - Validates Splunk field name
   ```json
   {"type": "Fieldname"}
   ```

5. **RegularExpression** - Validates string against regex
   ```json
   {"type": "RegularExpression"}
   ```

If we're expecting a string - or don't know the value - we should omit the `validate` field.

A snippet from the UCC's schema.json is provided below:

```json
  "customSearchCommand": {
      "type": "object",
      "description": "Support for custom Search Command.",
      "properties": {
        "commandName": {
          "type": "string",
          "pattern": "^[a-z0-9]+$",
          "maxLength": 100,
          "description": "Name of the custom Search Command."
        },
        "fileName": {
          "type": "string",
          "pattern": "^\\w+\\.py$",
          "description": "Name of the file which contains logic for custom search command. The file should be a python file only."
        },
        "commandType": {
          "type": "string",
          "description": "Type of the custom search command. There are 4 types of command i.e generating, streaming, transforming and dataset processing",
          "enum": [
            "generating",
            "streaming",
            "dataset processing",
            "transforming"
          ]
        },
        "requiredSearchAssistant": {
          "type": "boolean",
          "default": false,
          "description": "Specifies if search assistant is required or not. If yes then searchbnf.conf will be generated."
        },
        "description": {
          "type": "string",
          "description": "Description of the custom search command. It is an required attribute for searchbnf.conf."
        },
        "syntax": {
          "type": "string",
          "maxLength": 100,
          "description": "Syntax for the custom search command. It is an required attribute for searchbnf.conf."
        },
        "usage": {
          "type": "string",
          "description": "Specifies what will be the usage of custom search command. It is an required attribute for searchbnf.conf.",
          "enum": [
            "public",
            "private",
            "deprecated"
          ]
        },
        "arguments": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/arguments"
          },
          "minItems": 1
        }
      },
      "required": [
        "commandName",
        "fileName",
        "commandType",
        "arguments"
      ],
      "additionalProperties": false
    },
    "arguments": {
      "type": "object",
      "description": "Arguments used for custom search command",
      "properties": {
        "name": {
          "type": "string",
          "description": "Name of the argument"
        },
        "required": {
          "type": "boolean",
          "default": true,
          "description": "Specifies if the argument is required or not"
        },
        "validate": {
          "$ref": "#/definitions/CustomSearchCommandValidator"
        },
        "defaultValue": {
          "items": {
            "oneOf": [
              {
                "type": "string"
              },
              {
                "type": "number"
              }
            ]
          },
          "description": "Provide default value to the arguments passed for custom search command"
        }
      },
      "required": [
        "name"
      ],
      "additionalProperties": false
    },
    "CustomSearchCommandValidator": {
      "type": "object",
      "description": "It is used to validate the values of arguments for custom search command",
      "oneOf": [
        {
          "$ref": "#/definitions/CustomIntegerValidator"
        },
        {
          "$ref": "#/definitions/CustomFloatValidator"
        },
        {
          "$ref": "#/definitions/CustomRegularExpressionValidator"
        },
        {
          "$ref": "#/definitions/CustomFieldnameValidator"
        },
        {
          "$ref": "#/definitions/CustomBooleanValidator"
        }
      ]
    },
    "CustomIntegerValidator": {
      "type": "object",
      "properties": {
        "minimum": {
          "type": "number",
          "description": "Minimum value used for validation"
        },
        "maximum": {
          "type": "number",
          "description": "Maximum value used for validation"
        },
        "type": {
          "const": "Integer",
          "type": "string",
          "description": "This is integer Validator for custom search command, provide at least one of `minimumValue` or `maximumValue`"
        }
      },
      "required": [
        "type"
      ],
      "additionalProperties": false
    },
    "CustomFloatValidator": {
      "type": "object",
      "properties": {
        "minimumValue": {
          "type": "number",
          "description": "Minimum value used for validation"
        },
        "maximumValue": {
          "type": "number",
          "description": "Maximum value used for validation"
        },
        "type": {
          "const": "Float",
          "type": "string",
          "description": "This is Float Validator for custom search command, provide at least one of `minimumValue` or `maximumValue` for validation purpose."
        }
      },
      "required": [
        "type"
      ],
      "additionalProperties": false
    },
    "CustomRegularExpressionValidator": {
      "type": "object",
      "properties": {
        "type": {
          "const": "RegularExpression",
          "type": "string",
          "description": "This is RegularExpression Validator which validates if the input value is a valid regular expression pattern or not."
        }
      },
      "required": [
        "type"
      ],
      "additionalProperties": false
    },
    "CustomFieldnameValidator": {
      "type": "object",
      "properties": {
        "type": {
          "const": "Fieldname",
          "type": "string",
          "description": "Validates field name option values."
        }
      },
      "required": [
        "type"
      ],
      "additionalProperties": false
    },
    "CustomBooleanValidator": {
      "type": "object",
      "properties": {
        "type": {
          "const": "Boolean",
          "type": "string",
          "description": "Validates Boolean option values."
        }
      },
      "required": [
        "type"
      ],
      "additionalProperties": false
    },
```

## Python Implementation Pattern

### Template Structure

Create `<addon>/package/bin/<fileName>.py` with this structure:

```python
"""
Custom search command logic for <command_name>
"""
import sys
import json
import traceback
from splunklib import six

def generate(command):
    """
    Generator function for creating events.
    
    Args:
        command: GeneratingCommand instance with parsed options
        
    Yields:
        dict: Event records to return to Splunk
    """
    # Access command options
    query = command.query  # Required argument
    limit = command.limit if hasattr(command, 'limit') else 100
    
    # Get logger from command
    logger = command.logger
    
    try:
        # Get configuration from Splunk storage/passwords
        session_key = command.search_results_info.auth_token
        config = get_addon_config(session_key)
        
        # Initialize API client
        api_client = APIClient(
            base_url=config.get('api_url'),
            api_key=config.get('api_key'),
            logger=logger
        )
        
        # Call API
        logger.info(f"Executing query: {query} with limit: {limit}")
        results = api_client.query(query, limit=limit)
        
        # Yield events
        for item in results:
            # Transform API response to Splunk event
            event = {
                '_time': item.get('timestamp', int(time.time())),
                '_raw': json.dumps(item),
                'source': 'myapi',
                'sourcetype': 'myapi:lookup',
                **item  # Add all API fields as Splunk fields
            }
            yield event
            
    except Exception as e:
        logger.error(f"Error in generate command: {str(e)}")
        logger.error(traceback.format_exc())
        raise


def get_addon_config(session_key):
    """
    Retrieve add-on configuration from Splunk storage/passwords.
    
    Args:
        session_key: Splunk session key for authentication
        
    Returns:
        dict: Configuration parameters
    """
    # Import Splunk REST library
    from solnlib import conf_manager
    
    cfm = conf_manager.ConfManager(
        session_key,
        "TA-myapi",
        realm="__REST_CREDENTIAL__#TA-myapi#configs/conf-ta_myapi_account"
    )
    
    # Get account configuration
    account_conf = cfm.get_conf("ta_myapi_account")
    accounts = account_conf.get_all()
    
    if not accounts:
        raise Exception("No API account configured")
    
    # Get first account
    account = list(accounts.values())[0]
    
    return {
        'api_url': account.get('api_url'),
        'api_key': account.get('api_key')
    }


class APIClient:
    """
    Client for interacting with external API.
    """
    
    def __init__(self, base_url, api_key, logger=None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.logger = logger
        self.session = self._create_session()
    
    def _create_session(self):
        """Create configured requests session."""
        import requests
        session = requests.Session()
        session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Splunk-TA-MyAPI/1.0.0'
        })
        return session
    
    def query(self, query, limit=100):
        """
        Execute API query.
        
        Args:
            query: Search query string
            limit: Maximum results to return
            
        Returns:
            list: API response records
        """
        url = f"{self.base_url}/search"
        params = {
            'q': query,
            'limit': limit
        }
        
        if self.logger:
            self.logger.debug(f"API request: GET {url} with params {params}")
        
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return data.get('results', [])
```

## Complete Example of globalConfig.json content and Python logic file for a `threatintel` command that queries a threat intelligence API.

### globalConfig.json Configuration

```json
{
    "meta": {
        "name": "TA-threat-intel",
        "displayName": "Threat Intelligence Add-on",
        "version": "1.0.0",
        "restRoot": "ta_threat_intel"
    },
    "pages": {
        "configuration": {
            "title": "Configuration",
            "description": "Configure Threat Intelligence API",
            "tabs": [
                {
                    "name": "account",
                    "title": "Account",
                    "entity": [
                        {
                            "field": "name",
                            "label": "Account Name",
                            "type": "text",
                            "required": true
                        },
                        {
                            "field": "api_url",
                            "label": "API URL",
                            "type": "text",
                            "required": true,
                            "defaultValue": "https://api.threatintel.example.com"
                        },
                        {
                            "field": "api_key",
                            "label": "API Key",
                            "type": "text",
                            "encrypted": true,
                            "required": true
                        }
                    ]
                }
            ]
        }
    },
    "customSearchCommand": [
        {
            "commandName": "threatintel",
            "fileName": "threatintel_logic.py",
            "commandType": "generating",
            "requiredSearchAssistant": true,
            "description": "Query threat intelligence data for IPs, domains, or hashes.",
            "syntax": "threatintel indicator=<string> type=<ip|domain|hash> [limit=<int>]",
            "usage": "public",
            "arguments": [
                {
                    "name": "indicator",
                    "required": true
                },
                {
                    "name": "type",
                    "required": true
                },
                {
                    "name": "limit",
                    "required": false,
                    "defaultValue": 100,
                    "validate": {
                        "type": "Integer",
                        "minimum": 1,
                        "maximum": 1000
                    }
                }
            ]
        }
    ]
}
```

### Python Implementation: `package/bin/threatintel_logic.py`

```python
"""
Threat Intelligence custom search command logic.
Queries external threat intelligence API for indicator reputation.
"""
import sys
import json
import time
import traceback
from splunklib import six


def generate(command):
    """
    Generate threat intelligence results for the specified indicator.
    
    This function is called by the UCC-generated wrapper and must yield
    event dictionaries for Splunk to process.
    
    Args:
        command: GeneratingCommand instance with parsed options
        
    Yields:
        dict: Event records containing threat intelligence data
    """
    # Get logger
    logger = command.logger
    
    try:
        # Extract command arguments
        indicator = command.indicator
        indicator_type = command.type
        limit = getattr(command, 'limit', 100)
        
        logger.info(f"Threat intelligence lookup: indicator={indicator}, type={indicator_type}, limit={limit}")
        
        # Get session key for accessing Splunk configuration
        session_key = command.search_results_info.auth_token
        
        # Retrieve API configuration
        config = get_api_config(session_key, logger)
        
        # Initialize threat intel client
        ti_client = ThreatIntelClient(
            base_url=config['api_url'],
            api_key=config['api_key'],
            logger=logger
        )
        
        # Query threat intelligence API
        results = ti_client.lookup_indicator(
            indicator=indicator,
            indicator_type=indicator_type,
            limit=limit
        )
        
        logger.info(f"Retrieved {len(results)} threat intelligence records")
        
        # Transform and yield results
        for record in results:
            event = transform_to_splunk_event(record, indicator, indicator_type)
            yield event
            
    except Exception as e:
        logger.error(f"Error in threatintel command: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Yield error event to inform user
        yield {
            '_time': int(time.time()),
            'error': str(e),
            'indicator': indicator if 'indicator' in locals() else 'unknown',
            'status': 'failed'
        }


def get_api_config(session_key, logger):
    """
    Retrieve threat intelligence API configuration from Splunk.
    
    Args:
        session_key: Splunk session key
        logger: Logger instance
        
    Returns:
        dict: Configuration with api_url and api_key
    """
    try:
        from solnlib import conf_manager
        
        # Initialize configuration manager
        cfm = conf_manager.ConfManager(
            session_key,
            "TA-threat-intel",
            realm="__REST_CREDENTIAL__#TA-threat-intel#configs/conf-ta_threat_intel_account"
        )
        
        # Get account configuration
        account_conf = cfm.get_conf("ta_threat_intel_account")
        accounts = account_conf.get_all()
        
        if not accounts:
            raise ValueError("No threat intelligence API account configured. Please configure in the add-on setup page.")
        
        # Use the first configured account
        account = list(accounts.values())[0]
        
        logger.debug(f"Using API URL: {account.get('api_url')}")
        
        return {
            'api_url': account.get('api_url'),
            'api_key': account.get('api_key')
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve API configuration: {str(e)}")
        raise


def transform_to_splunk_event(record, indicator, indicator_type):
    """
    Transform API response record into Splunk event format.
    
    Args:
        record: API response record (dict)
        indicator: Searched indicator value
        indicator_type: Type of indicator (ip, domain, hash)
        
    Returns:
        dict: Splunk event with proper fields
    """
    # Extract timestamp (use current time if not provided)
    timestamp = record.get('timestamp')
    if timestamp:
        # Convert ISO format to epoch
        try:
            from dateutil import parser
            dt = parser.parse(timestamp)
            event_time = int(dt.timestamp())
        except:
            event_time = int(time.time())
    else:
        event_time = int(time.time())
    
    # Build Splunk event
    event = {
        # Splunk metadata fields
        '_time': event_time,
        '_raw': json.dumps(record),
        'source': 'threat_intel_api',
        'sourcetype': 'threat_intel:lookup',
        
        # Search criteria
        'indicator': indicator,
        'indicator_type': indicator_type,
        
        # Threat intelligence fields
        'threat_score': record.get('score', 0),
        'threat_level': record.get('level', 'unknown'),
        'malicious': record.get('malicious', False),
        'categories': ','.join(record.get('categories', [])),
        'first_seen': record.get('first_seen'),
        'last_seen': record.get('last_seen'),
        'source_feeds': ','.join(record.get('sources', [])),
        
        # Additional context
        'tags': ','.join(record.get('tags', [])),
        'confidence': record.get('confidence', 0),
        'description': record.get('description', '')
    }
    
    # Add any additional fields from API response
    for key, value in record.items():
        if key not in event and not isinstance(value, (dict, list)):
            event[f'ti_{key}'] = value
    
    return event


class ThreatIntelClient:
    """
    HTTP client for threat intelligence API.
    """
    
    def __init__(self, base_url, api_key, logger=None):
        """
        Initialize threat intelligence client.
        
        Args:
            base_url: API base URL
            api_key: API authentication key
            logger: Optional logger instance
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.logger = logger
        self.session = self._create_session()
    
    def _create_session(self):
        """Create and configure requests session."""
        import requests
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry
        
        session = requests.Session()
        
        # Configure retries
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers
        session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Splunk-TA-ThreatIntel/1.0.0'
        })
        
        return session
    
    def lookup_indicator(self, indicator, indicator_type, limit=100):
        """
        Query threat intelligence for an indicator.
        
        Args:
            indicator: Indicator value (IP, domain, hash)
            indicator_type: Type of indicator
            limit: Maximum results
            
        Returns:
            list: Threat intelligence records
        """
        endpoint = f"{self.base_url}/v1/indicators/{indicator_type}/{indicator}"
        
        params = {'limit': limit}
        
        if self.logger:
            self.logger.debug(f"API request: GET {endpoint}")
        
        try:
            response = self.session.get(
                endpoint,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get('data', [])
            
            if self.logger:
                self.logger.info(f"API returned {len(results)} results for {indicator}")
            
            return results
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"API request failed: {str(e)}")
            raise
```

## Best Practices

### 1. Error Handling
- Always wrap API calls in try/except blocks
- Log errors with full traceback for debugging
- Yield error events to inform users (don't fail silently)

### 2. Configuration Management
- Use UCC's configuration page for credentials
- Never hardcode API keys
- Only make API URLs configurable when the endpoint varies across deployments, or when the add-on architecture requires that flexibility
- Use `solnlib.conf_manager` to access configuration

### 3. Logging
- Use `command.logger` for consistent logging
- Log at appropriate levels (info, debug, error)
- Include request details for troubleshooting

### 4. Performance
- Implement timeouts on API calls (default: 30s)
- Use retry logic for transient failures
- Respect API rate limits

### 5. Data Transformation
- Always include `_time`, `_raw`, `source`, `sourcetype`
- Flatten nested JSON structures for easier searching
- Use consistent field naming conventions

### 6. Validation
- Use UCC validators in globalConfig.json
- Validate API responses before yielding events
- Handle missing or malformed data gracefully

### 7. Security
- Use encrypted storage for credentials
- Don't log sensitive data (API keys, passwords)
- Validate and sanitize user inputs

## Generated Files

When you run `ucc-gen build`, UCC generates:

1. **Wrapper file**: `output/TA-myapi/bin/myapicommand.py`
   - Auto-generated by UCC
   - Imports your logic function
   - Handles SPL command dispatching

2. **commands.conf**: `output/TA-myapi/default/commands.conf`
   ```conf
   [myapicommand]
   filename = myapicommand.py
   chunked = true
   python.version = python3
   ```

3. **searchbnf.conf** (if `requiredSearchAssistant=true`): `output/TA-myapi/default/searchbnf.conf`
   ```conf
   [myapicommand]
   syntax = myapicommand query=<string> limit=<int>
   description = Query the MyAPI service for data.
   usage = public
   ```

## Documentation Requirements

After implementing custom search commands, document them in `package/README.txt` (to be updated before the build and package phase). For each custom command, include:

1. **Command Name:** Exact SPL syntax (e.g., `threatintel_lookup`)
2. **Description:** What the command does in plain language
3. **Usage Syntax:** Parameter names, types, and which are required vs. optional
4. **Examples:** At least 1 practical SPL example showing how to use the command:
   - Example of the command alone: `| threatintel_lookup ip="1.2.3.4"` - returns threat intel data
5. **Output Fields:** List of fields the command returns (e.g., `threat_level`, `last_seen`, `reputation_score`)


**Remember:** Create/update the **logic file** (specified in `fileName`), not the wrapper file (specified in `commandName`). UCC generates the wrapper automatically.

