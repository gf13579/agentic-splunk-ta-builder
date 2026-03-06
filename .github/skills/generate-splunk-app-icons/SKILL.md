---
name: generate-splunk-app-icons
description: Generates Splunk app icon sets based on customizable text, colors, and borders. Creates icons in the required sizes for Splunk app submissions.
---

# Splunk App Icon Generator

This skill generates a complete set of 4 Splunk app icons with customizable styling.

## Usage

- Identify the TA's package/static folder path e.g. <repo_root>/TA-myservice/package/static
- Run the generation script with the desired parameters, specifying the output directory (--output-dir) as identified TA's package/static path

Example:

```
uv run --with pillow .github/skills/generate-splunk-app-icons/generate_icon.py --text "MS" --output-dir "TA-myservice/package/static"
```

**Never** use an output directory with **appserver/static** in the path - this not the correct location for app icons.


## Required Information

You must provide:
- **Text**: 1-2 characters to display on the icon (e.g., "CI", "DB", "ML")

The agent may infer this value from the app name or display name (for example, using initials) and skip prompting the user if a reasonable default is available.
Example: `TA-myservice` or `My Service Add-on for Splunk` → `MS`.

## Optional Parameters

You may ask the user for these, or use the defaults:
- **Background color**: Hex color (default: #001E36 - dark blue)
- **Foreground color**: Hex color for text (default: #31A8FF - light blue)
- **Border**: Whether to include a rounded border (default: yes)
- **Border width**: Thickness on 0-100 scale (default: 8)

## When to Use This Skill

Invoke this skill when the user:
- Mentions "Splunk app icon" or "Splunk app icons"
- Wants to generate icons for a Splunk app
- Needs appIcon.png files
