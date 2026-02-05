# Agentic Splunk TA Builder

> An AI-powered template for automatically generating production-ready Splunk Technology Add-ons (TAs) using natural language conversations

## What is This?

This project provides an **agentic development framework** that enables you to generate complete, production-ready Splunk Technology Add-ons by simply describing your API to an LLM (like GitHub Copilot, Claude, or ChatGPT). No more manually writing boilerplate configuration files or setting up complex project structures—just provide your API documentation and let the AI build your TA.

### Key Features

- 🤖 **Conversational Development**: Chat with an LLM to build your TA—no complex tooling required
- 📋 **Configuration as Code**: Built on Splunk's UCC (Universal Configuration Console) framework
- 🎯 **Intelligent Architecture**: Automatically decides what components to build based on your API
- ✅ **AppInspect Ready**: Generates TAs that pass Splunk's validation requirements
- 📚 **Documentation Included**: Comes with auto-generated documentation
- 🧪 **Testing Built In**: Includes basic test suite structure
- 🚀 **Production Ready**: Creates installable packages ready for Splunkbase

## What Gets Built For You

When you provide API documentation, the agent analyzes it and automatically creates:

- **Scripted Inputs** - for endpoints that return events, logs, or time-series data
- **Custom SPL Commands** - for search/lookup endpoints that analysts need on-demand
- **Alert Actions** - for APIs that accept actions (tickets, notifications, remediation)
- **Configuration UI** - auto-generated from your specifications
- **Authentication Handling** - API keys, OAuth, basic auth, or custom patterns
- **Error Handling & Logging** - production-grade error management
- **Checkpointing** - for reliable, resumable data collection
- **Documentation** - setup guides, configuration examples, troubleshooting
- **Tests** - unit and integration test structures

## Quick Start

### Prerequisites

- Python 3.7+
- Access to an LLM that supports file context (GitHub Copilot Chat, Claude, etc.)
- Splunk Enterprise 8.0+ or Splunk Cloud (for testing the generated TA)
- API documentation for the service you want to integrate

### How to Use

1. **Clone or copy this repository**
   ```bash
   git clone <your-repo-url>
   cd agentic-splunk-ta-builder
   ```

2. **Open in your AI-enabled editor**
   - VS Code with GitHub Copilot
   - Cursor
   - Any editor with LLM integration that can read project files

3. **Start a conversation with your LLM**
   
   Share the [AGENTS.md](AGENTS.md) file with your LLM and provide:
   
   ```
   I want to build a Splunk TA for [SERVICE NAME].
   
   Here's the API documentation: [paste docs or URL]
   
   Add-on details:
   - Name: TA-myservice
   - Display Name: My Service Add-on for Splunk
   - Description: Collects events from My Service API
   - Author: Your Name
   ```

4. **Let the Agent Work**
   
   The AI will:
   - Analyze your API documentation
   - Determine what components to build
   - Generate the complete TA structure
   - Create all necessary configuration files
   - Write Python code for data collection
   - Set up testing and documentation

5. **Review and Test**
   
   ```bash
   # Build the TA
   cd TA-myservice
   ucc-gen build --source package --ta-version 1.0.0
   
   # Package for installation
   ucc-gen package --path output/TA-myservice
   
   # Validate with AppInspect
   splunk-appinspect inspect output/TA-myservice-1.0.0.tar.gz
   ```

## Understanding AGENTS.md

The [AGENTS.md](AGENTS.md) file is the **instruction manual** for the AI agent. It contains:

- **Workflow Phases**: Step-by-step process the agent follows
- **Decision Criteria**: Rules for determining what components to build
- **Best Practices**: Guidance on Splunk TA development patterns
- **Common Pitfalls**: Things to avoid
- **Success Criteria**: Checklist for a production-ready TA

Think of it as a **detailed prompt template** that gives the LLM expert knowledge in Splunk TA development. When you share this file with your LLM, it gains the context needed to build professional-grade add-ons.

### How Agentic Development Works

Traditional development: You manually write code, configs, and documentation.

Agentic development: 
1. You describe what you want (the API you're integrating)
2. The AI agent reads AGENTS.md to understand the task
3. The agent makes intelligent decisions about architecture
4. The agent generates all code, configs, and documentation
5. You review, test, and refine

The agent acts as an **expert Splunk developer** that can work 24/7 and never forgets best practices.

## Example Conversation

```
Developer: I need a Splunk TA for the JSONPlaceholder API (https://jsonplaceholder.typicode.com). 
It has endpoints like /posts, /comments, /users. Build me TA-jsonplaceholder.

Agent: [Analyzes API documentation]

I'll create a TA with:
- A scripted input to collect posts and comments (event data)
- A custom command `jsonplaceholder_user` to lookup user details on-demand
- Configuration UI for API base URL customization
- Checkpointing to track last collected post ID

[Generates complete TA structure...]

Developer: Great! Can you also add CIM compliance for the Web data model?

Agent: [Updates configuration to map fields to CIM...]

Done! Your TA is now CIM-compliant for web events.
```

## What You Need to Provide

### Required
- **API Documentation**: OpenAPI/Swagger spec, REST API docs, or developer guide
- **Add-on Metadata**: Name, display name, description, author info

### Optional
- Authentication details (helps the agent configure correctly)
- Specific endpoints to prioritize
- Data collection frequency preferences  
- CIM alignment requirements
- Proxy or advanced configuration needs

## Architecture Decisions

The agent automatically decides what to build based on your API:

| API Pattern | What Gets Built | Example Endpoints |
|-------------|----------------|-------------------|
| Event/log data | **Scripted Input** | `/events`, `/logs`, `/alerts` |
| Lookup/search | **Custom Command** | `/users/{id}`, `/search?q=` |
| Action endpoints | **Alert Action** | `POST /tickets`, `/notify` |
| Authentication | **Account Management** | API keys, OAuth, tokens |

## Project Structure

After generation, your TA will look like:

```
TA-myservice/
├── package/
│   ├── globalConfig.json      # Core UCC configuration
│   ├── bin/
│   │   ├── myservice_input.py # Data collection script
│   │   ├── myservice_cmd.py   # Custom SPL command
│   │   └── lib/               # Shared utilities
│   ├── README/
│   │   └── inputs.conf.spec   # Configuration specs
│   └── default/
│       └── app.conf           # App metadata
├── tests/                     # Test suite
└── README.md                  # Generated documentation
```

## Requirements

### Development
- Python 3.7+
- `splunk-add-on-ucc-framework` (`pip install splunk-add-on-ucc-framework`)

### Runtime (in Splunk)
- Splunk Enterprise 8.0+ or Splunk Cloud Platform
- Python 3.7+ (bundled with Splunk)
- Internet connectivity (if calling external APIs)

## Validation and Deployment

### AppInspect Validation
```bash
# Install AppInspect CLI
pip install splunk-appinspect

# Run validation
splunk-appinspect inspect TA-myservice-1.0.0.tar.gz --mode precert
```

### Installing in Splunk
```bash
# Via CLI
$SPLUNK_HOME/bin/splunk install app TA-myservice-1.0.0.tar.gz -auth admin:changeme

# Or upload via Web UI
# Settings > Apps > Install app from file
```

## Benefits Over Manual Development

| Manual Approach | Agentic Approach |
|----------------|------------------|
| Hours of boilerplate setup | Minutes of conversation |
| Manual UCC configuration | Auto-generated configs |
| Research API patterns | Agent analyzes for you |
| Write repetitive code | Agent writes idiomatic code |
| Remember AppInspect rules | Built-in compliance |
| Write documentation | Auto-generated docs |
| Set up test structure | Tests included |

## Common Use Cases

1. **SaaS API Integration**: Collect events from cloud services (GitHub, Salesforce, etc.)
2. **Security Tools**: Ingest alerts from EDR, SIEM, or threat intel platforms
3. **Custom Commands**: Add lookup capabilities for external data sources
4. **Alert Actions**: Enable Splunk to trigger actions in external systems
5. **Metrics Collection**: Pull performance data from monitoring APIs

## Troubleshooting

### Agent isn't generating what I expected
- Provide more detailed API documentation
- Be specific about which endpoints matter most
- Mention if certain patterns should be prioritized

### Generated TA fails AppInspect
- Ask the agent to review specific AppInspect findings
- The agent can fix common compliance issues automatically

### Need to customize the generated TA
- You can ask the agent to modify specific components
- Or manually edit the generated files—they're standard Python and JSON

## Contributing

Contributions welcome! Areas for improvement:

- Additional decision criteria for edge cases
- More comprehensive test generation
- Support for advanced Splunk features (KV store, lookups)
- CIM compliance templates
- Examples and templates for common API patterns

## Resources

- [Splunk UCC Framework Documentation](https://splunk.github.io/addonfactory-ucc-generator/)
- [Splunk Development Best Practices](https://dev.splunk.com/enterprise/docs/devtools/developapps/)
- [AppInspect Documentation](https://dev.splunk.com/enterprise/docs/releaseapps/appinspect/)
- [Splunk Common Information Model](https://docs.splunk.com/Documentation/CIM/latest/User/Overview)

## License

[Add your license here]

## Support

For questions or issues:
- Review the [AGENTS.md](AGENTS.md) file for detailed workflow information
- Check generated TA documentation
- Consult Splunk UCC framework docs

---

**Ready to build your first TA?** Open [AGENTS.md](AGENTS.md) in your AI-enabled editor and start the conversation!
