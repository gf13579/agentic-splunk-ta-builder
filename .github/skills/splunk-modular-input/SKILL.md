---
name: splunk-modular-input
description: Implements Python data collection logic for UCC modular inputs by MODIFYING the auto-generated *_helper.py files. Uses the stream_events() and validate_input() entry points defined by UCC. Adds API client logic, event writing, error handling, and optional state management. Only modifies package/bin/*_helper.py files.
---

# Skill Instructions

## When to Use This Skill

Use this skill when writing Python code for Splunk modular inputs in UCC-based add-ons. The helper file you're modifying contains:
- `validate_input()`: Validates input configuration (called when creating/editing inputs in the UI)
- `stream_events()`: Main data collection function (called periodically based on the interval set by users)

**Assumption:** API/vendor documentation analysis and architectural decisions are completed before using this skill. This skill implements the previously defined inputs; it does not design them.

**Dependency note:** If you add third-party imports beyond the default UCC set, update `package/lib/requirements.txt` with each new package on its own line. UCC includes `requests`, `solnlib`, and `splunk-sdk` by default.

## Making changes to globalConfig.json

Before writing any replacements to large json files like globalConfig.json, output the target structure as a code block and reason about which existing text it replaces in full.

Replace the entire object (e.g. "configuration") when possible to avoid syntax errors and incorrect nesting caused by simultaneous replacement using the multi_replace_string_in_file tool that may conflict with each other.

## Editing globalConfig.json for Account Parameters

It's common for APIs to require credentials and base URLs. These should be added as configurable fields in the account configuration section of `globalConfig.json`. An example is provided below - where API URL has been added to the standard account fields created by the UCC init command:

```json
        "configuration": {
            "tabs": [
                {
                    "name": "account",
                    "table": {
                        "actions": [
                            "edit",
                            "delete",
                            "clone"
                        ],
                        "header": [
                            {
                                "label": "Name",
                                "field": "name"
                            }
                        ]
                    },
                    "entity": [
                        {
                            "type": "text",
                            "label": "Name",
                            "validators": [
                                {
                                    "type": "regex",
                                    "errorMsg": "Account Name must begin with a letter and consist exclusively of alphanumeric characters and underscores.",
                                    "pattern": "^[a-zA-Z]\\w*$"
                                },
                                {
                                    "type": "string",
                                    "errorMsg": "Length of input name should be between 1 and 100",
                                    "minLength": 1,
                                    "maxLength": 100
                                }
                            ],
                            "field": "name",
                            "help": "A unique name for the account.",
                            "required": true
                        },
                        {
                            "type": "text",
                            "label": "API URL",
                            "field": "api_url",
                            "help": "Base URL for the Threat Intelligence API.",
                            "required": true,
                            "defaultValue": "https://api.example.com",
                            "validators": [
                                {
                                    "type": "string",
                                    "errorMsg": "Length of API URL should be between 8 and 2048",
                                    "minLength": 8,
                                    "maxLength": 2048
                                }
                            ]
                        },
                        {
                            "type": "text",
                            "label": "API key",
                            "field": "api_key",
                            "help": "API key",
                            "required": true,
                            "encrypted": true,
                            "validators": [
                                {
                                    "type": "string",
                                    "errorMsg": "Length of API key should be between 1 and 50",
                                    "minLength": 1,
                                    "maxLength": 50
                                }
                            ]
                        }
                    ],
                    "title": "Accounts"
                },
                {
                    "type": "loggingTab"
                }
            ],
            "title": "Configuration",
            "description": "Set up your add-on"
        }
```

## Editing globalConfig.json for Custom Input Parameters

Before implementing the helper file logic, you may need to edit `globalConfig.json` to expose API parameters as configurable fields in the UI.

**When to add custom input fields:**
- API endpoints accept optional parameters (e.g., `limit`, `filters`, `date_range`)
- Users should be able to customize data collection behavior without editing code
- Examples: `limit` (max results), `ioc_type` (filter by type), `polling_frequency`, `data_source`

**How to add custom fields to an input:**

In `globalConfig.json`, locate the `pages.inputs.services[]` array and add fields to the `entity` array for your input. Example:

```json
{
  "pages": {
    "inputs": {
      "services": [
        {
          "name": "my_input",
          "title": "My Input",
          "entity": [
            {
              "type": "text",
              "label": "Name",
              "field": "name",
              "required": true
            },
            {
              "type": "interval",
              "label": "Interval",
              "field": "interval",
              "defaultValue": "300"
            },
            {
              "type": "text",
              "label": "Limit",
              "field": "limit",
              "defaultValue": "1000",
              "help": "Maximum number of results per collection run",
              "validators": [
                {
                  "type": "number",
                  "errorMsg": "Limit must be between 1 and 10000",
                  "range": [1, 10000],
                  "isInteger": true
                }
              ]
            },
            {
              "type": "singleSelect",
              "label": "IOC Type",
              "field": "ioc_type",
              "options": {
                "disableSearch": true,
                "autoCompleteFields": [
                  {"label": "IP", "value": "ip"},
                  {"label": "Domain", "value": "domain"},
                  {"label": "All", "value": "all"}
                ]
              },
              "defaultValue": "all",
              "help": "Filter threat feed by indicator type"
            }
          ]
        }
      ]
    }
  }
}
```

Note - prefer "autoCompleteFields" over "items" for singleSelect as "items" appears to be broken currently.

**Common UCC field types for inputs:**
- `text`: Free-form text input
- `number`: Integer or float with optional range validation
- `checkbox`: Boolean toggle
- `singleSelect`: Dropdown menu (options provided)
- `interval`: Time interval with validation
- `index`: Splunk index selector

**Accessing custom fields in the helper:**
Once defined in globalConfig.json, access these fields in your `stream_events()` function:

```python
def stream_events(inputs: smi.InputDefinition, event_writer: smi.EventWriter):
    for input_name, input_item in inputs.inputs.items():
        # Access custom parameters
        limit = input_item.get("limit", "1000")  # With default fallback
        ioc_type = input_item.get("ioc_type", "all")
        
        # Use in API call
        params = {
            "limit": int(limit),
            "ioc_type": ioc_type
        }
        response = session.get(api_url, params=params)
```

**Validating globalConfig.json:**
After editing globalConfig.json, validate it before building using the `validate-ucc-json` skill to catch schema errors early:

```bash
uv run --with requests python3 .github/skills/validate-ucc-json/validate_ucc_json.py globalConfig.json
```

If validation fails, fix the schema violations before running `ucc-gen build`.

**Reference examples:**
- See `.github/skills/ucc-config-generator/exampleOfGlobalConfig.json` for a complete example with custom input parameters

## Key Principle: ONLY Modify the Helper File

**IMPORTANT**: When working with UCC-based add-ons, `ucc-gen init` automatically creates the first helper file for you.

If more than one type of input is required, define it in globalConfig.json and then create additional helper stubs by copying the generated helper file and adjusting the filename to match each input name. This keeps the modular input skill focused on modifying existing helpers rather than creating new files.

- ✅ **DO**: Modify the existing `*_helper.py` files
- ❌ **DO NOT**: Create new standalone modular input Python files
- ❌ **DO NOT**: Create files like `threat_feed.py`, `myservice_events.py`, etc.

**The first helper file is already there** - just update its functions with your API client code!

### File Naming in UCC
- Input service in globalConfig: `threat_feed`
- Auto-generated helper file: `package/bin/threat_feed_helper.py` ← **Modify this!**
- You do NOT need: `package/bin/threat_feed.py` ← **Do not create this!**

## UCC Modular Input Structure

The generated helper file has this structure:

```python
import import_declare_test
import json
import logging
from solnlib import conf_manager, log
from splunklib import modularinput as smi

ADDON_NAME = "TA-MyAddOn"

def validate_input(definition: smi.ValidationDefinition):
    """Validate input configuration. Raise an exception to fail validation."""
    pass

def stream_events(inputs: smi.InputDefinition, event_writer: smi.EventWriter):
    """Main data collection function called by Splunk."""
    # inputs.inputs is a dict like:
    # {
    #   "my_input://<input_name>": {
    #     "account": "<account_name>",
    #     "disabled": "0",
    #     "host": "$decideOnStartup",
    #     "index": "<index_name>",
    #     "interval": "<interval>",
    #     "python.version": "python3",
    #   },
    # }
    for input_name, input_item in inputs.inputs.items():
        # Process this input
        pass
```

**Key parameters:**
- `inputs.metadata["session_key"]`: Splunk session token (needed for REST API calls)
- `inputs.inputs`: Dictionary of configured inputs (can be multiple if the input is instantiated multiple times)
- `input_item`: Configuration values for the current input instance
- `event_writer`: Object with `write_event()` method

## Handling API Base URLs

API base URLs should be:
1. **Configurable in globalConfig.json** (account configuration)
2. **Retrieved from account settings** at runtime

For example, if one base URL is required, add an `api_url` field to the account configuration:
```json
{
  "name": "account",
  "entity": [
    {
      "type": "text",
      "label": "API URL",
      "field": "api_url",
      "defaultValue": "https://api.example.com",
      "help": "Base URL for the API endpoint"
    },
    ...
  ]
}
```

**Never** hard-code API URLs in the helper files.

**Never** use a validator to require that URLs start with "https". http is fine.

Example code to retrieve a base API url from account configuration:

```python
account_config = get_account_config(session_key, account_name)
api_url = account_config.get("api_url", "https://api.example.com")
```

## Getting Configuration Values

### Accessing Input Configuration

Inside `stream_events()`, use `inputs.inputs` to access configuration:

```python
def stream_events(inputs: smi.InputDefinition, event_writer: smi.EventWriter):
    for input_name, input_item in inputs.inputs.items():
        # User-configured fields
        account_name = input_item.get("account")          # From globalConfig
        index = input_item.get("index")                   # From globalConfig
        interval = input_item.get("interval")            # From globalConfig
        custom_field = input_item.get("my_custom_param") # From globalConfig
        
        # Metadata
        session_key = inputs.metadata["session_key"]
        server_uri = inputs.metadata.get("server_uri")   # Optional
```

### Getting Account Credentials

Use `conf_manager` from solnlib to fetch account credentials from your account config file:

```python
from solnlib import conf_manager

def get_account_config(session_key: str, addon_name: str, account_name: str) -> dict:
    """Fetch account credentials from the account config."""
    cfm = conf_manager.ConfManager(
        session_key,
        addon_name,
        realm=f"__REST_CREDENTIAL__#{addon_name}#configs/conf-{addon_name}_account",
    )
    account_conf = cfm.get_conf(f"{addon_name}_account")
    return dict(account_conf.get(account_name))
```

See [conf_manager documentation](https://splunk.github.io/addonfactory-solutions-library-python/conf_manager/) for more details.

### Getting Proxy Settings

Proxy configuration is stored in the app settings:

```python
def get_proxy_config(session_key: str, addon_name: str) -> dict:
    """Fetch proxy settings."""
    cfm = conf_manager.ConfManager(session_key, addon_name)
    try:
        settings_conf = cfm.get_conf(f"{addon_name}_settings")
        proxy = settings_conf.get("proxy")
        if proxy:
            return {
                "proxy_enabled": proxy.get("proxy_enabled") in ("1", "true", "yes"),
                "proxy_url": proxy.get("proxy_url"),
                "proxy_username": proxy.get("proxy_username"),
                "proxy_password": proxy.get("proxy_password"),
            }
    except Exception:
        pass
    return {}
```

## Logging

Use solnlib's logging:

```python
from solnlib import log

logger = log.Logs().get_logger("addon_name_input_name")
logger.setLevel(logging.INFO)

logger.info("Processing input")
logger.warning("Rate limit approaching")
logger.error("API call failed")
logger.debug("Response: %s", response.text)
```

Set log level from configuration:

```python
from solnlib import conf_manager, log
import logging

session_key = inputs.metadata["session_key"]
log_level = conf_manager.get_log_level(
    logger=logger,
    session_key=session_key,
    app_name=ADDON_NAME,
    conf_name=f"{ADDON_NAME}_settings",
)
logger.setLevel(log_level)
```

## Events and Writing

Write events using `event_writer.write_event()`:

```python
from splunklib import modularinput as smi

event = smi.Event(
    data=json.dumps({"key": "value"}, ensure_ascii=False, default=str),
    source="myapp",
    sourcetype="my:sourcetype",
    index=index_name,
)
event_writer.write_event(event)
```

With timestamp:

```python
from datetime import datetime

# Parse ISO timestamp to epoch
timestamp_str = "2024-02-13T10:30:00Z"
dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
event.time = dt.timestamp()
event_writer.write_event(event)
```

## Baseline Pattern: Simple Collection (Without Checkpoints)

For most APIs, the simplest approach is to fetch and index all available data on each collection run. This is **stateless** and does not require checkpoint management.

**When to use this pattern:**
- ✅ API returns all current data (no change tracking needed)
- ✅ Data is idempotent (safe to re-index)
- ✅ API has no incremental query parameters (`since`, `after`, `last_modified`)
- ✅ Data set is reasonably small on each run
- ✅ Simple troubleshooting preferred over avoiding duplicates

```python
def stream_events(inputs: smi.InputDefinition, event_writer: smi.EventWriter):
    for input_name, input_item in inputs.inputs.items():
        session_key = inputs.metadata["session_key"]
        normalized_input_name = input_name.split("/")[-1]
        logger = log.Logs().get_logger(f"addon_{normalized_input_name}")
        
        try:
            # Get configuration
            account_name = input_item.get("account")
            index = input_item.get("index")
            
            # Get credentials
            account = get_account_config(session_key, ADDON_NAME, account_name)
            api_key = account.get("api_key")
            
            logger.info(f"Starting collection for {normalized_input_name}")
            
            # Fetch all available data
            session = build_session()
            response = session.get(
                f"{api_url}/v1/events",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"limit": 100},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            
            # Write all events
            event_count = 0
            for event_data in data.get("events", []):
                event_writer.write_event(smi.Event(
                    data=json.dumps(event_data, ensure_ascii=False, default=str),
                    sourcetype="my:sourcetype",
                    index=index,
                ))
                event_count += 1
            
            logger.info(f"Completed collection: {event_count} events indexed")
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            logger.error(f"Collection failed: {str(e)}", exc_info=True)
```

## API Integration

### Basic HTTP Request with Retry Logic



```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def build_session(proxy_config: dict = None) -> requests.Session:
    """Create a session with retry logic and proxy support."""
    session = requests.Session()
    
    # Configure retries
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Configure proxy if provided
    if proxy_config and proxy_config.get("proxy_enabled"):
        proxy_url = proxy_config.get("proxy_url")
        if proxy_config.get("proxy_username") and proxy_config.get("proxy_password"):
            # Build proxy URL with credentials
            parsed = urlparse(proxy_url)
            auth = f"{proxy_config['proxy_username']}:{proxy_config['proxy_password']}"
            proxy_url = f"{parsed.scheme}://{auth}@{parsed.netloc}{parsed.path}"
        session.proxies = {"http": proxy_url, "https": proxy_url}
    
    return session

def stream_events(inputs: smi.InputDefinition, event_writer: smi.EventWriter):
    for input_name, input_item in inputs.inputs.items():
        try:
            session = build_session()
            headers = {"Authorization": f"Bearer {api_key}"}
            
            response = session.get(
                f"{api_url}/v1/events",
                headers=headers,
                params={"limit": 100},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            
            # Process response...
            
        except requests.exceptions.Timeout:
            logger.error("API request timed out")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {str(e)}")
```

### Pagination Example

When an API supports pagination, fetch all pages on each run and write all events:

```python
def stream_events(inputs: smi.InputDefinition, event_writer: smi.EventWriter):
    for input_name, input_item in inputs.inputs.items():
        try:
            session = build_session()
            normalized_input_name = input_name.split("/")[-1]
            
            page = 1
            total_events = 0
            
            while True:
                response = session.get(
                    f"{api_url}/v1/events",
                    headers={"Authorization": f"Bearer {api_key}"},
                    params={
                        "page": page,
                        "per_page": 100,
                        "order": "asc",
                    },
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()
                
                events = data.get("events", [])
                if not events:
                    break
                
                for event_data in events:
                    event_writer.write_event(smi.Event(
                        data=json.dumps(event_data, ensure_ascii=False, default=str),
                        sourcetype="my:sourcetype",
                        index=input_item.get("index"),
                    ))
                
                total_events += len(events)
                if not data.get("has_more", False):
                    break
                
                page += 1
                
            logger.info(f"Fetched {total_events} events in {page} pages")
            
        except Exception as e:
            logger.error(f"Pagination failed: {str(e)}", exc_info=True)
```

## Error Handling and Logging

Use try/except with proper logging instead of silent failures:

```python
def stream_events(inputs: smi.InputDefinition, event_writer: smi.EventWriter):
    for input_name, input_item in inputs.inputs.items():
        normalized_input_name = input_name.split("/")[-1]
        logger = log.Logs().get_logger(f"addon_{normalized_input_name}")
        
        try:
            # Set log level
            session_key = inputs.metadata["session_key"]
            log_level = conf_manager.get_log_level(
                logger=logger,
                session_key=session_key,
                app_name=ADDON_NAME,
                conf_name=f"{ADDON_NAME}_settings",
            )
            logger.setLevel(log_level)
            
            # Log input start
            logger.info(f"Starting data collection for {normalized_input_name}")
            
            # ... collection logic ...
            
            # Log input end
            logger.info(f"Completed collection: {total_events} events indexed")
            
        except Exception as e:
            logger.error(f"Exception in {normalized_input_name}: {str(e)}", exc_info=True)
            # Re-raise if fatal; otherwise Splunk will retry on next interval
```

## Advanced Patterns: Stateful Collection with Checkpoints

Use checkpoints only when needed to avoid re-indexing the same data. Checkpoints track state between modular input runs using KVStore.

**Reference:** [KVStoreCheckpointer documentation](https://splunk.github.io/addonfactory-solutions-library-python/modular_input/checkpointer/#kvstore-checkpointer)

### When to Use Checkpoints

**Use checkpoints when:**
- ✅ API supports incremental queries (`since`, `after`, `last_modified`, `from_timestamp`, etc.)
- ✅ Data changes over time and re-indexing would create duplicates
- ✅ Data set is large and you want to avoid fetching everything each run
- ✅ API provides event IDs or offsets to resume from

**Skip checkpoints when:**
- ❌ API always returns fresh data regardless of query parameters (reference/lookup data)
- ❌ API has no parameters for incremental filtering
- ❌ Data is immutable or reference-only
- ❌ Duplicates are acceptable or automatically deduplicated
- ❌ Adding complexity is not worth the small performance gain

### Checkpoint Pattern

```python
from solnlib.modular_input import checkpointer

def stream_events(inputs: smi.InputDefinition, event_writer: smi.EventWriter):
    for input_name, input_item in inputs.inputs.items():
        session_key = inputs.metadata["session_key"]
        normalized_input_name = input_name.split("/")[-1]
        
        try:
            # Create checkpointer with collection name, session key, and app name
            ckpt = checkpointer.KVStoreCheckpointer(
                collection_name="addon_checkpoints",  # KVStore collection name
                session_key=session_key,
                app=ADDON_NAME,
            )
            
            # Read checkpoint state (returns None if not set)
            last_state = ckpt.get(normalized_input_name)
            
            # On first run, initialize with defaults
            if last_state is None:
                last_timestamp = "2024-01-01T00:00:00Z"
            else:
                last_timestamp = last_state.get("last_timestamp")
            
            # Fetch data using checkpoint
            session = build_session()
            response = session.get(
                f"{api_url}/v1/events",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"since": last_timestamp, "limit": 100},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            
            # Write events and track latest timestamp
            events = data.get("events", [])
            for event_data in events:
                event_writer.write_event(smi.Event(
                    data=json.dumps(event_data, ensure_ascii=False, default=str),
                    sourcetype="my:sourcetype",
                    index=input_item.get("index"),
                ))
            
            # Update checkpoint only after all events written
            if events:
                ckpt.update(normalized_input_name, {
                    "last_timestamp": events[-1]["timestamp"],
                })
                logger.info(f"Fetched {len(events)} new events")
            
        except Exception as e:
            logger.error(f"Collection failed: {str(e)}", exc_info=True)
```

### Checkpoint Best Practices

1. **Initialize on first run**: Always provide defaults for first-run scenarios
2. **Store sufficient state**: Include all fields needed to resume correctly (timestamp, ID, etc.)
3. **Update after success**: Only update checkpoint after events are successfully written
4. **Use atomic updates**: Write all state fields in one update call
5. **Reference state by key**: Use the normalized input name as the checkpoint key

## Common Patterns

### Structure for Multiple Inputs

If globalConfig.json defines multiple input types, you will need one helper file per input. The first helper file will be generated by `ucc-gen init` - copy if more are required.

### Handling Rate Limits

Check response headers and respect backoff:

```python
response = session.get(url)
if response.status_code == 429:
    retry_after = int(response.headers.get("Retry-After", 60))
    logger.warning(f"Rate limited, backing off {retry_after}s")
    time.sleep(retry_after)
```

### Testing Validation

The `validate_input()` function is called when users create/edit an input:

```python
def validate_input(definition: smi.ValidationDefinition):
    """Validate input configuration."""
    account_name = definition.parameters.get("account")
    api_url = definition.parameters.get("api_url")
    
    # Test connectivity or credentials
    try:
        account = get_account_config(session_key, ADDON_NAME, account_name)
        api_key = account.get("api_key")
        
        response = requests.get(
            f"{api_url}/v1/health",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=5,
        )
        response.raise_for_status()
    except Exception as e:
        raise smi.ValidationError(f"Cannot connect to API: {str(e)}")
```

## Common Patterns and Anti-Patterns

### ✅ DO: Simple Pattern First (No Checkpoints)
```python
# GOOD: Start simple, add checkpoints only if needed
response = session.get(api_url, headers=headers, timeout=30)
response.raise_for_status()
for event in response.json()["events"]:
    event_writer.write_event(smi.Event(
        data=json.dumps(event),
        sourcetype="my:sourcetype",
        index=index,
    ))
```

### ✅ DO: Use Checkpoints Correctly (When Needed)
```python
# GOOD: Read checkpoint, use it, update after success
ckpt = checkpointer.KVStoreCheckpointer(...)
last_id = (ckpt.get(input_name) or {}).get("last_id", 0)
events = fetch_events(after_id=last_id)
for event in events:
    event_writer.write_event(...)
if events:
    ckpt.update(input_name, {"last_id": events[-1]['id']})
```

### ❌ DON'T: Overuse Checkpoints
```python
# BAD: Premature optimization
# Using checkpoints for reference data that doesn't change
ckpt = KVStoreCheckpointer(...)  # Unnecessary!
events = fetch_all_users()  # This never changes

# GOOD: Keep it simple if data is static
response = session.get("/v1/users")
for user in response.json():
    event_writer.write_event(...)  # No checkpoint needed
```

### ❌ DON'T: Forget to Initialize Checkpoints (If Using Them)
```python
# BAD: Will fail on first run if None
last_id = ckpt.get(input_name)
events = fetch_events(after_id=last_id)  # Error if last_id is None!

# GOOD: Always provide a default
last_id = (ckpt.get(input_name) or {}).get("last_id", 0)
```

### ✅ DO: Handle API Errors Gracefully
```python
# GOOD: Specific error handling
try:
    response = session.get(url)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        helper.log_error("Authentication failed")
    elif e.response.status_code == 429:
        helper.log_warning("Rate limited")
    else:
        helper.log_error(f"HTTP error: {e}")
```

### ✅ DO: Log at Appropriate Levels
```python
# GOOD: Informative logging
helper.log_info(f"Starting collection for {input_name}")
helper.log_debug(f"API response: {response.text[:200]}")
helper.log_warning(f"Retrying after rate limit")
helper.log_error(f"Failed to parse event: {str(e)}")
```

### ❌ DON'T: Log Every Event or Excessive Debug Info
```python
# BAD: Too verbose, impacts performance
for event in events:
    helper.log_info(f"Processing event: {event}")  # Don't do this!

# GOOD: Summary logging
helper.log_info(f"Processed {len(events)} events")
```

### ✅ DO: Use Proper Event Timestamps
```python
# GOOD: Preserve original event time
timestamp_str = event['created_at']
dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
event_time = dt.timestamp()

event = helper.new_event(..., time=event_time)
```

### ❌ DON'T: Omit Timestamps When Available
```python
# BAD: Uses current time instead of event time
event = helper.new_event(..., data=json.dumps(event_data))
# Missing time parameter - Splunk will use collection time!
```

## Performance Considerations

1. **Batch processing**: Collect and write multiple events per run
2. **Pagination**: Don't try to fetch all data in one request
3. **Connection pooling**: Use `requests.Session()` for multiple requests
4. **Timeout settings**: Always set timeouts (30s is reasonable)

## Documentation Requirements

After implementing modular inputs, document them in `package/README.txt` (to be updated before the build and package phase). For each modular input, include:

1. **Input Name:** Machine name used in `inputs.conf` (e.g., `threat_feed`)
2. **Description:** Human-readable purpose of the input
3. **Data Collected:** What events or data this input collects
4. **Required Configuration:**
   - Which account/credentials are needed
   - Any custom parameters (e.g., `limit`, `filters`, `ioc_type`) and their default values
   - Typical polling interval recommendations
   - Index destination
5. **Example Configuration:** Show sample input setup from the UI or `inputs.conf` example

This documentation helps users understand what data each input collects and how to configure it for their use case.

## Summary

Key principles for modular inputs:
- **Start simple**: Fetch and write all data on each run (no checkpoints) as the baseline
- **Handle errors gracefully** with proper logging
- **Write events with timestamps** when available
- **Add checkpoints only if needed** to avoid duplicate indexing of large datasets
- **Use stateless collection** unless the API explicitly supports incremental filters
