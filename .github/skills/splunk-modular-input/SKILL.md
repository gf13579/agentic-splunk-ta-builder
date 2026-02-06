---
name: splunk-modular-input
description: Implements Python data collection logic for UCC modular inputs by MODIFYING the auto-generated *_helper.py files. DO NOT create new standalone .py files - ucc-gen init creates the helper file automatically. Updates existing helper functions with API client code, checkpoint management, event writing, error handling, and authentication. Only modifies package/bin/*_helper.py files, never creates new modular input files.
---

# Skill Instructions

## When to Use This Skill
Use this skill when writing Python code for Splunk modular inputs in UCC-based add-ons. This covers the actual data collection scripts that live in `package/bin/` and are responsible for:
- Calling APIs to collect data
- Managing checkpoints (tracking what's been collected)
- Formatting and writing events to Splunk
- Handling errors and logging
- Managing authentication and rate limiting

## ⚠️ CRITICAL: UCC Helper Pattern (DO NOT CREATE NEW FILES)

**IMPORTANT**: When working with UCC-based add-ons, `ucc-gen init` automatically creates the helper file for you:
- ✅ **DO**: Modify the existing `*_helper.py` file created by `ucc-gen init`
- ❌ **DO NOT**: Create a new standalone modular input Python file
- ❌ **DO NOT**: Create files like `threat_feed.py`, `myservice_events.py`, etc.

**The helper file is already there** - just update its functions with your API client code!

### File Naming in UCC
- Input service in globalConfig: `threat_feed`
- Auto-generated helper file: `package/bin/threat_feed_helper.py` ← **Modify this!**
- You do NOT need: `package/bin/threat_feed.py` ← **Do not create this!**

### This Skill is ONLY for Modular Inputs
This skill does **NOT** apply to custom commands. Custom commands:
- ✅ **DO** need to be created from scratch (e.g., `threatintel.py`)
- Follow different patterns (inherit from `StreamingCommand`, `GeneratingCommand`, etc.)
- Are standalone executable scripts

## What is a Modular Input?
A modular input is a Python script that Splunk runs periodically to collect data. In UCC-based add-ons, these scripts are automatically configured based on your `globalConfig.json` and execute according to the interval users set in the UI.

## Core Structure: The Helper Pattern

UCC provides a powerful helper framework that simplifies modular input development. Here's the basic structure every modular input should follow:

```python
# encoding = utf-8
import import_declare_test
import os
import sys
import time
import datetime
import json

from splunklib import modularinput as smi
from solnlib import conf_manager
from solnlib import log
from solnlib.modular_input import checkpointer

def validate_input(helper, definition):
    """
    Validate the input configuration.
    Called when user creates or edits an input.
    Raise an exception if validation fails.
    """
    pass  # Add validation logic if needed

def collect_events(helper, ew):
    """
    Main data collection function.
    Called periodically based on the interval configured by the user.
    
    Args:
        helper: Helper object with methods to access config and utilities
        ew: EventWriter object to write events to Splunk
    """
    # 1. Get configuration
    # 2. Initialize checkpoint
    # 3. Call API
    # 4. Process and write events
    # 5. Update checkpoint
    # 6. Handle errors
    
    pass  # Implementation goes here
```

## Essential Helper Methods

### Getting Configuration Values

```python
def collect_events(helper, ew):
    # Get input-specific configuration (from inputs page)
    input_name = helper.get_input_stanza_names()
    interval = helper.get_arg('interval')
    index = helper.get_arg('index')
    
    # Get account credentials (from account/configuration page)
    account_name = helper.get_arg('account')
    account = helper.get_account_by_name(account_name)
    api_url = account['api_url']
    api_key = account['api_key']
    
    # Get proxy settings (if proxy tab is enabled)
    proxy_settings = helper.get_proxy()
    if proxy_settings:
        proxy_url = proxy_settings.get('proxy_url')
        proxy_username = proxy_settings.get('proxy_username')
        proxy_password = proxy_settings.get('proxy_password')
    
    # Get log level
    log_level = helper.get_log_level()
    helper.log_info(f"Starting data collection with log level: {log_level}")
```

### Common Helper Methods Reference

| Method | Purpose | Example |
|--------|---------|---------|
| `helper.get_arg(name)` | Get input parameter value | `interval = helper.get_arg('interval')` |
| `helper.get_account_by_name(name)` | Get account credentials | `account = helper.get_account_by_name('my_account')` |
| `helper.get_proxy()` | Get proxy configuration | `proxy = helper.get_proxy()` |
| `helper.get_input_stanza_names()` | Get input name | `name = helper.get_input_stanza_names()` |
| `helper.get_log_level()` | Get configured log level | `level = helper.get_log_level()` |
| `helper.log_info(msg)` | Log info message | `helper.log_info("Processing...")` |
| `helper.log_error(msg)` | Log error message | `helper.log_error("API call failed")` |
| `helper.log_warning(msg)` | Log warning message | `helper.log_warning("Rate limit hit")` |
| `helper.log_debug(msg)` | Log debug message | `helper.log_debug("Raw response: ...")` |

## Checkpoint Management

Checkpoints track what data has already been collected to avoid duplicates. UCC provides KVStore-based checkpointing.

### Basic Checkpoint Pattern

```python
from solnlib.modular_input import checkpointer

def collect_events(helper, ew):
    # Get input name for checkpoint key
    input_name = helper.get_input_stanza_names()
    
    # Get checkpointer (KVStore-based)
    ckpt = helper.get_check_point(input_name)
    
    # Read last checkpoint value
    last_timestamp = ckpt.get("last_timestamp")
    if last_timestamp is None:
        # First run - use a default starting point
        last_timestamp = "2024-01-01T00:00:00Z"
    
    helper.log_info(f"Last checkpoint: {last_timestamp}")
    
    # Collect data from API (passing last_timestamp to get only new data)
    events = fetch_data_from_api(api_url, api_key, since=last_timestamp)
    
    # Process and write events...
    
    # Update checkpoint with latest timestamp
    if events:
        latest_timestamp = events[-1]['timestamp']
        ckpt.update("last_timestamp", latest_timestamp)
        helper.log_info(f"Updated checkpoint to: {latest_timestamp}")
```

### Checkpoint Best Practices

1. **Use timestamps when possible**: APIs that support `since` or `after` parameters
2. **Use IDs for APIs without timestamps**: Store last seen ID
3. **Store multiple values**: Dictionary checkpoints for complex state
4. **Always initialize**: Provide sensible defaults for first run
5. **Update atomically**: Only update checkpoint after successfully writing events

### Advanced Checkpoint Pattern (Multiple Fields)

```python
def collect_events(helper, ew):
    input_name = helper.get_input_stanza_names()
    ckpt = helper.get_check_point(input_name)
    
    # Read checkpoint state
    checkpoint_state = ckpt.get("state")
    if checkpoint_state is None:
        checkpoint_state = {
            "last_timestamp": "2024-01-01T00:00:00Z",
            "last_id": 0,
            "page": 1
        }
    
    # Use checkpoint to fetch data
    events = fetch_paginated_data(
        since=checkpoint_state['last_timestamp'],
        after_id=checkpoint_state['last_id'],
        page=checkpoint_state['page']
    )
    
    # Process events...
    
    # Update all checkpoint fields
    if events:
        checkpoint_state['last_timestamp'] = events[-1]['timestamp']
        checkpoint_state['last_id'] = events[-1]['id']
        checkpoint_state['page'] = current_page + 1
        ckpt.update("state", checkpoint_state)
```

## Writing Events to Splunk

### Basic Event Writing

```python
def collect_events(helper, ew):
    # ... get configuration and fetch data ...
    
    # Get target index
    index = helper.get_arg('index')
    
    # Write each event
    for item in api_response['events']:
        # Create event object
        event = helper.new_event(
            source=helper.get_input_type(),  # e.g., "myservice:events"
            index=index,
            sourcetype=helper.get_sourcetype(),  # from inputs.conf
            data=json.dumps(item)  # Convert dict to JSON string
        )
        ew.write_event(event)
    
    helper.log_info(f"Successfully indexed {len(api_response['events'])} events")
```

### Event Writing Best Practices

1. **Always use JSON for structured data**: `data=json.dumps(dict)`
2. **Add timestamp if available**: `event.time = timestamp`
3. **Set appropriate sourcetype**: Usually configured in globalConfig
4. **Include source**: Helps with data routing and troubleshooting
5. **Batch logging**: Log summary stats, not individual events

### Enhanced Event Writing with Timestamp

```python
import time
from datetime import datetime

def collect_events(helper, ew):
    index = helper.get_arg('index')
    
    for item in events:
        # Extract timestamp from API response
        timestamp_str = item.get('created_at', item.get('timestamp'))
        
        # Convert to epoch time (Splunk format)
        if timestamp_str:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            epoch_time = dt.timestamp()
        else:
            epoch_time = time.time()
        
        # Create event with explicit timestamp
        event = helper.new_event(
            source=helper.get_input_type(),
            index=index,
            sourcetype=helper.get_sourcetype(),
            data=json.dumps(item),
            time=epoch_time
        )
        ew.write_event(event)
```

## API Client Pattern

### Basic HTTP Request with Error Handling

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def collect_events(helper, ew):
    # Get configuration
    account_name = helper.get_arg('account')
    account = helper.get_account_by_name(account_name)
    api_url = account['api_url']
    api_key = account['api_key']
    
    # Create session with retry logic
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # Set headers
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Make API call
        response = session.get(
            f"{api_url}/v1/events",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        events = data.get('events', [])
        
        # Write events
        for event in events:
            ew.write_event(helper.new_event(
                source=helper.get_input_type(),
                index=helper.get_arg('index'),
                sourcetype=helper.get_sourcetype(),
                data=json.dumps(event)
            ))
        
        helper.log_info(f"Successfully collected {len(events)} events")
        
    except requests.exceptions.Timeout:
        helper.log_error("API request timed out")
    except requests.exceptions.HTTPError as e:
        helper.log_error(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        helper.log_error(f"Request failed: {str(e)}")
    except json.JSONDecodeError as e:
        helper.log_error(f"Failed to parse JSON response: {str(e)}")
    except Exception as e:
        helper.log_error(f"Unexpected error: {str(e)}")
        raise
```

### API Client with Pagination

```python
def collect_events(helper, ew):
    account = helper.get_account_by_name(helper.get_arg('account'))
    api_url = account['api_url']
    api_key = account['api_key']
    
    headers = {'Authorization': f'Bearer {api_key}'}
    
    # Get checkpoint
    input_name = helper.get_input_stanza_names()
    ckpt = helper.get_check_point(input_name)
    last_timestamp = ckpt.get("last_timestamp") or "2024-01-01T00:00:00Z"
    
    page = 1
    page_size = 100
    total_events = 0
    
    while True:
        try:
            response = requests.get(
                f"{api_url}/v1/events",
                headers=headers,
                params={
                    'since': last_timestamp,
                    'page': page,
                    'per_page': page_size
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            events = data.get('events', [])
            if not events:
                break  # No more data
            
            # Write events
            for event in events:
                ew.write_event(helper.new_event(
                    source=helper.get_input_type(),
                    index=helper.get_arg('index'),
                    sourcetype=helper.get_sourcetype(),
                    data=json.dumps(event)
                ))
            
            total_events += len(events)
            
            # Check if there are more pages
            if not data.get('has_more', False):
                break
            
            page += 1
            
        except Exception as e:
            helper.log_error(f"Error on page {page}: {str(e)}")
            break
    
    # Update checkpoint with latest timestamp
    if total_events > 0:
        latest_timestamp = events[-1].get('timestamp', last_timestamp)
        ckpt.update("last_timestamp", latest_timestamp)
    
    helper.log_info(f"Collected {total_events} events across {page} pages")
```

### API Client with Rate Limiting

```python
import time
from datetime import datetime, timedelta

def collect_events(helper, ew):
    account = helper.get_account_by_name(helper.get_arg('account'))
    api_url = account['api_url']
    api_key = account['api_key']
    
    headers = {'Authorization': f'Bearer {api_key}'}
    
    # Track rate limiting
    max_requests_per_minute = 60
    request_count = 0
    window_start = datetime.now()
    
    events_to_fetch = get_event_ids_to_fetch()  # Your logic here
    
    for event_id in events_to_fetch:
        # Check if we need to wait for rate limit window
        if request_count >= max_requests_per_minute:
            elapsed = (datetime.now() - window_start).total_seconds()
            if elapsed < 60:
                sleep_time = 60 - elapsed
                helper.log_info(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            
            # Reset window
            window_start = datetime.now()
            request_count = 0
        
        try:
            response = requests.get(
                f"{api_url}/v1/events/{event_id}",
                headers=headers,
                timeout=30
            )
            request_count += 1
            
            if response.status_code == 429:
                # Rate limited - wait and retry
                retry_after = int(response.headers.get('Retry-After', 60))
                helper.log_warning(f"Rate limited, waiting {retry_after} seconds")
                time.sleep(retry_after)
                continue
            
            response.raise_for_status()
            event_data = response.json()
            
            # Write event
            ew.write_event(helper.new_event(
                source=helper.get_input_type(),
                index=helper.get_arg('index'),
                sourcetype=helper.get_sourcetype(),
                data=json.dumps(event_data)
            ))
            
        except Exception as e:
            helper.log_error(f"Error fetching event {event_id}: {str(e)}")
            continue
```

## Complete Example: Production-Ready Modular Input

Here's a complete example incorporating all best practices:

```python
# encoding = utf-8
import import_declare_test
import os
import sys
import time
import datetime
import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from splunklib import modularinput as smi
from solnlib.modular_input import checkpointer

def validate_input(helper, definition):
    """
    Validate input configuration.
    """
    # Add any validation logic here
    # For example, test API connectivity
    pass

def collect_events(helper, ew):
    """
    Main data collection function.
    """
    # Step 1: Get configuration
    try:
        account_name = helper.get_arg('account')
        account = helper.get_account_by_name(account_name)
        api_url = account.get('api_url')
        api_key = account.get('api_key')
        
        interval = helper.get_arg('interval')
        index = helper.get_arg('index')
        
        helper.log_info(f"Starting data collection for account: {account_name}")
        
    except Exception as e:
        helper.log_error(f"Failed to read configuration: {str(e)}")
        return
    
    # Step 2: Initialize checkpoint
    input_name = helper.get_input_stanza_names()
    ckpt = helper.get_check_point(input_name)
    
    last_timestamp = ckpt.get("last_timestamp")
    if last_timestamp is None:
        # First run - start from 24 hours ago
        from datetime import datetime, timedelta
        start_time = datetime.utcnow() - timedelta(hours=24)
        last_timestamp = start_time.isoformat() + "Z"
        helper.log_info(f"First run - starting from {last_timestamp}")
    else:
        helper.log_info(f"Resuming from checkpoint: {last_timestamp}")
    
    # Step 3: Set up HTTP session with retry
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'User-Agent': 'Splunk-TA-MyService/1.0.0'
    }
    
    # Step 4: Fetch and process data
    page = 1
    page_size = 100
    total_events = 0
    latest_timestamp = last_timestamp
    
    while True:
        try:
            helper.log_debug(f"Fetching page {page}")
            
            response = session.get(
                f"{api_url}/v1/events",
                headers=headers,
                params={
                    'since': last_timestamp,
                    'page': page,
                    'per_page': page_size,
                    'order': 'asc'  # Important: oldest first for proper checkpointing
                },
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            events = data.get('events', [])
            if not events:
                helper.log_debug("No more events to fetch")
                break
            
            helper.log_debug(f"Processing {len(events)} events from page {page}")
            
            # Write events to Splunk
            for event_data in events:
                # Extract timestamp if available
                event_time = None
                if 'timestamp' in event_data:
                    try:
                        dt = datetime.datetime.fromisoformat(
                            event_data['timestamp'].replace('Z', '+00:00')
                        )
                        event_time = dt.timestamp()
                    except Exception as e:
                        helper.log_warning(f"Failed to parse timestamp: {str(e)}")
                
                # Create and write event
                event = helper.new_event(
                    source=helper.get_input_type(),
                    index=index,
                    sourcetype=helper.get_sourcetype(),
                    data=json.dumps(event_data),
                    time=event_time
                )
                ew.write_event(event)
                
                # Track latest timestamp for checkpoint
                if 'timestamp' in event_data:
                    latest_timestamp = event_data['timestamp']
            
            total_events += len(events)
            
            # Check for more pages
            if not data.get('has_more', False):
                break
            
            page += 1
            
            # Safety check - don't process too many pages in one run
            if page > 100:
                helper.log_warning(f"Reached maximum page limit (100), will continue next run")
                break
            
        except requests.exceptions.Timeout:
            helper.log_error(f"Request timed out on page {page}")
            break
        except requests.exceptions.HTTPError as e:
            helper.log_error(f"HTTP error on page {page}: {e.response.status_code}")
            if e.response.status_code in [401, 403]:
                helper.log_error("Authentication failed - check API key")
            break
        except json.JSONDecodeError as e:
            helper.log_error(f"Invalid JSON response on page {page}: {str(e)}")
            break
        except Exception as e:
            helper.log_error(f"Unexpected error on page {page}: {str(e)}")
            break
    
    # Step 5: Update checkpoint
    if total_events > 0:
        ckpt.update("last_timestamp", latest_timestamp)
        helper.log_info(
            f"Successfully indexed {total_events} events. "
            f"Updated checkpoint to {latest_timestamp}"
        )
    else:
        helper.log_info("No new events to index")
```

## Common Patterns and Anti-Patterns

### ✅ DO: Use Checkpoints Properly
```python
# GOOD: Read checkpoint, use it, update it
ckpt = helper.get_check_point(input_name)
last_id = ckpt.get("last_id") or 0
events = fetch_events(after_id=last_id)
# ... process events ...
if events:
    ckpt.update("last_id", events[-1]['id'])
```

### ❌ DON'T: Forget to Initialize Checkpoints
```python
# BAD: Will fail on first run if None
last_id = ckpt.get("last_id")
events = fetch_events(after_id=last_id)  # Error if last_id is None!

# GOOD: Always provide a default
last_id = ckpt.get("last_id") or 0
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

### ❌ DON'T: Catch and Silence All Errors
```python
# BAD: Hides problems
try:
    # ... complex logic ...
except:
    pass  # Silent failure!

# GOOD: Log and handle appropriately
except Exception as e:
    helper.log_error(f"Error: {str(e)}")
    raise  # Re-raise if it's fatal
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
5. **Checkpoint granularity**: Balance between exactness and performance

## Testing Your Modular Input

### Manual Testing
1. Build the TA: `ucc-gen build`
2. Install in Splunk: Copy to `$SPLUNK_HOME/etc/apps/`
3. Configure input via UI
4. Check logs: `index=_internal source=*myservice*.log`
5. Verify events: `index=<your_index> sourcetype=<your_sourcetype>`

### Common Issues
- **No events appear**: Check permissions, API connectivity, logging
- **Duplicate events**: Checkpoint not updating properly
- **Missing events**: Pagination logic error or incorrect timestamp ordering
- **Input not running**: Check interval, Python errors in splunkd.log

## Summary

Key principles for modular inputs:
1. **Always use helper methods** for config access
2. **Implement checkpointing** to avoid duplicates
3. **Handle errors gracefully** with proper logging
4. **Use retries** for transient failures
5. **Respect rate limits** from APIs
6. **Write events with timestamps** when available
7. **Log summary statistics** not individual events
8. **Test thoroughly** before deployment
