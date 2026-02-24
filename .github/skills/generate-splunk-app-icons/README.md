# Splunk App Icon Generator Skill

This skill helps generate complete icon sets for Splunk app submissions.

## File Structure

```
.github/skills/generate-splunk-app-icons/
├── SKILL.md           # Skill definition with frontmatter
├── generate_icon.py   # Icon generation script
└── README.md          # This file
```

## How It Works

When the coding agent recognizes that a user wants to generate Splunk app icons, it should:

1. Prompt the user for required information (1-2 character text)
2. Optionally ask about customization (colors, border options)
3. Execute the `generate_icon.py` script with appropriate parameters
4. Generate 4 PNG files in the TA's `/package/static/` directory

## Icon Placement in TA Structure

The icons should be placed in the **`/package/static/`** subdirectory of the TA being built. This replaces the default icons created by the `ucc-gen init` command.

```
TA-myservice/
└── package/
    └── static/          # Place generated icons here
        ├── appIcon.png
        ├── appIcon_2x.png
        ├── appIconAlt.png
        └── appIconAlt_2x.png
```

When `ucc-gen build` runs, these icons will be copied to the final TA package's `static/` directory. If we find an output/<TA-name>/static folder - i.e. `ucc-gen build` has already been run - let's copy our new icons to that folder too. Never copy icons into any of the `appserver/static/` folders - this is not the right place for icon files

## Generated Files

The skill creates these files required by Splunk AppInspect:
- `appIcon.png` (36×36) - Standard resolution icon
- `appIcon_2x.png` (72×72) - Retina display icon  
- `appIconAlt.png` (36×36) - Alternative standard icon
- `appIconAlt_2x.png` (72×72) - Alternative retina icon

## Requirements

- Python 3.6+
- [uv](https://docs.astral.sh/uv/) - Modern Python package installer

No manual installation needed! The `uv run --with pillow` command automatically handles the Pillow dependency.

## Manual Usage

You can also run the script directly using `uv`:

```bash
# Basic usage - generates in current directory
uv run --with pillow .github/skills/generate-splunk-app-icons/generate_icon.py --text "ML"

# Generate directly in TA package static folder (recommended)
uv run --with pillow .github/skills/generate-splunk-app-icons/generate_icon.py \
  --text "TI" \
  --output-dir "TA-myservice/package/static"

# With custom styling
uv run --with pillow .github/skills/generate-splunk-app-icons/generate_icon.py \
  --text "CI" \
  --bg "#2C3E50" \
  --fg "#ECF0F1" \
  --border-width 10 \
  --output-dir "TA-myservice/package/static"

# Without border
uv run --with pillow .github/skills/generate-splunk-app-icons/generate_icon.py \
  --text "DB" \
  --no-border \
  --output-dir "TA-myservice/package/static"
```

## Examples

### Machine Learning App
```bash
uv run --with pillow .github/skills/generate-splunk-app-icons/generate_icon.py \
  --text "ML" \
  --bg "#8E44AD" \
  --fg "#ECF0F1" \
  --output-dir "TA-ml-service/package/static"
```

### Database Connector
```bash
uv run --with pillow .github/skills/generate-splunk-app-icons/generate_icon.py \
  --text "DB" \
  --bg "#27AE60" \
  --fg "#FFFFFF" \
  --output-dir "TA-database-connector/package/static"
```

### CI/CD Integration
```bash
uv run --with pillow .github/skills/generate-splunk-app-icons/generate_icon.py \
  --text "CI" \
  --bg "#E74C3C" \
  --fg "#FFFFFF" \
  --output-dir "TA-cicd-integration/package/static"
```

## Agent Workflow Integration

When building a TA with the agent:
1. After `ucc-gen init` creates the base TA structure
2. Generate custom icons with the appropriate text/branding
3. Icons are placed directly in `package/static/`, replacing defaults
4. Run `ucc-gen build` - the custom icons are included in the final package
