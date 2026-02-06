# Installation for GitHub Copilot

To use this skill with GitHub Copilot in VSCode:

## Setup

1. **Copy the skill to your repository**:
   ```bash
   # Create the skills directory in your repo
   mkdir -p .github/skills
   
   # Copy this entire folder
   cp -r splunk-appinspect .github/skills/
   ```

2. **Install dependencies**:
   ```bash
   pip install -r .github/skills/splunk-appinspect/requirements.txt
   ```

3. **Make the script executable** (Linux/Mac):
   ```bash
   chmod +x .github/skills/splunk-appinspect/appinspect_validator.py
   ```

4. **Commit to your repository**:
   ```bash
   git add .github/skills/splunk-appinspect
   git commit -m "Add Splunk AppInspect skill"
   git push
   ```

## Using with GitHub Copilot

Once installed, GitHub Copilot will automatically recognize this skill when you're working in your repository.

### Example prompts:

- "Validate my Splunk app with AppInspect"
- "Run AppInspect on dist/myapp.tar.gz"
- "Check if my Splunk package passes validation"
- "What are the AppInspect failures in my app?"

Copilot will suggest using the validator script and can help you interpret the results.

## Direct Usage (without Copilot)

You can also run the validator directly:

```bash
# From your repository root
.github/skills/splunk-appinspect/appinspect_validator.py path/to/your/app.tar.gz
```

## Setting up Authentication

### Option 1: Environment Variable (Recommended for CI/CD)
```bash
# Get your token first by running the script once
export APPINSPECT_TOKEN="your_token_here"

# Add to your shell profile for persistence
echo 'export APPINSPECT_TOKEN="your_token_here"' >> ~/.bashrc
```

### Option 2: GitHub Secrets (for CI/CD workflows)
1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `APPINSPECT_TOKEN`
4. Value: Your token from the first run
5. Click "Add secret"

Then in your GitHub Actions workflow:
```yaml
- name: Validate with AppInspect
  env:
    APPINSPECT_TOKEN: ${{ secrets.APPINSPECT_TOKEN }}
  run: |
    .github/skills/splunk-appinspect/appinspect_validator.py dist/myapp.tar.gz
```

## Troubleshooting

### "Command not found"
Make sure the script is executable:
```bash
chmod +x .github/skills/splunk-appinspect/appinspect_validator.py
```

### "No module named 'requests'"
Install dependencies:
```bash
pip install requests
# or
pip install -r .github/skills/splunk-appinspect/requirements.txt
```

### "Authentication failed"
Verify your Splunk.com credentials at https://www.splunk.com/

### Copilot doesn't suggest the skill
1. Ensure the folder is in `.github/skills/splunk-appinspect/`
2. Verify `SKILL.md` has proper frontmatter with `name` and `description`
3. Try reloading VSCode
4. Check that Copilot has access to your repository context

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Validate Splunk App

on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install -r .github/skills/splunk-appinspect/requirements.txt
      
      - name: Package app
        run: |
          tar -czf myapp.tar.gz -C src/ .
      
      - name: Run AppInspect
        env:
          APPINSPECT_TOKEN: ${{ secrets.APPINSPECT_TOKEN }}
        run: |
          .github/skills/splunk-appinspect/appinspect_validator.py myapp.tar.gz
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: appinspect-report
          path: appinspect_report_*.json
```

### GitLab CI Example
```yaml
validate_app:
  image: python:3.9
  script:
    - pip install -r .github/skills/splunk-appinspect/requirements.txt
    - tar -czf myapp.tar.gz -C src/ .
    - .github/skills/splunk-appinspect/appinspect_validator.py myapp.tar.gz
  artifacts:
    when: always
    paths:
      - appinspect_report_*.json
  variables:
    APPINSPECT_TOKEN: $APPINSPECT_TOKEN
```

## Next Steps

1. Test the installation: `.github/skills/splunk-appinspect/appinspect_validator.py --help`
2. Run your first validation
3. Review the generated JSON report for detailed findings
4. Integrate into your CI/CD pipeline
5. Ask Copilot to help fix any validation issues!
