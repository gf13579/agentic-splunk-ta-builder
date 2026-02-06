---
name: generate-splunk-app-icons
description: Generates Splunk app icon sets based on customizable text, colors, and borders. Creates icons in the required sizes for Splunk app submissions.
---

# Splunk App Icon Generator

This skill generates a complete set of Splunk app icons with customizable styling.

## What it does

Generates four PNG icon files required for Splunk app submissions:
- `appIcon.png` (36×36)
- `appIcon_2x.png` (72×72)
- `appIconAlt.png` (36×36)
- `appIconAlt_2x.png` (72×72)

## Required Information

You must ask the user for:
- **Text**: 1-2 characters to display on the icon (e.g., "CI", "DB", "ML")

## Optional Parameters

You may ask the user for these, or use the defaults:
- **Background color**: Hex color (default: #001E36 - dark blue)
- **Foreground color**: Hex color for text (default: #31A8FF - light blue)
- **Border**: Whether to include a rounded border (default: yes)
- **Border width**: Thickness on 0-100 scale (default: 8)

## Usage

When the user wants to generate Splunk app icons:

1. **Required**: Ask for the text to display (1-2 characters)
2. Optional: Ask if they want to customize colors or border
3. Run the generation script with the provided parameters

The icons will be created in the current working directory.

## Example Commands

Use `uv run --with pillow` to execute the script with automatic dependency management:

```bash
# Basic usage with required text parameter
uv run --with pillow .github/skills/splunk-icon-gen/generate_icon.py --text "ML"

# With custom colors
uv run --with pillow .github/skills/splunk-icon-gen/generate_icon.py --text "CI" --bg "#2C3E50" --fg "#ECF0F1"

# Without border
uv run --with pillow .github/skills/splunk-icon-gen/generate_icon.py --text "DB" --no-border

# Custom border width
uv run --with pillow .github/skills/splunk-icon-gen/generate_icon.py --text "AP" --border-width 12
```

## When to Use This Skill

Invoke this skill when the user:
- Mentions "Splunk app icon" or "Splunk app icons"
- Wants to generate icons for a Splunk app
- Needs appIcon.png files
- Asks to create Splunk app graphics or assets
- References Splunk AppInspect requirements for icons
