# DAI Assistant

A CLI system for orchestrating teams of AI agents that collaborate to create high-quality software projects.

## 🤖 Project Overview

DAI Assistant enables you to define and coordinate collaborative AI agents, each with specific roles and backstories. The system orchestrates these agents to work together on software development tasks using remote LLMs (like GPT-4, Claude, etc.) and produce well-structured, testable, documented code.

## ✨ Key Features

- **Multi-Agent Collaboration**: Orchestrate specialized AI agents (PM, Architect, Developer, QA, etc.)
- **Custom Agent Definitions**: Create agents with specific roles, backstories, and prompts
- **LLM Provider Integration**: Connect to various LLMs (OpenAI, Anthropic, etc.)
- **Parallel Execution**: Optimize workflow with dependency-based execution
- **Structured Output**: Generate complete software projects with proper documentation

## 📋 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/Dai_Assistent.git
cd Dai_Assistent

# Install dependencies
pip install -e ".[dev]"
```

## 🛠️ Quick Start

```bash
# Initialize a new project
dai init --project-name "my-api-project"

# Define a custom agent
dai define-agent --name "security-expert" --role "Security Engineer"

# Run a project with default agent team
dai run --project-name "my-api-project"

# Run with custom configurations
dai run --agents-config "configs/my-team.yaml"
```

## 📊 System Architecture

The DAI Assistant is organized into these key modules:

1. **CLI Interface** (`cli/`): Command processing and user interaction
2. **Orchestrator** (`orchestrator/`): Coordinates agent execution flow
3. **Agent Runtime** (`agent_runtime/`): Manages agent execution lifecycle
4. **LLM Connector** (`llm_connector/`): Handles external LLM API interactions
5. **Knowledge Manager** (`knowledge/`): Manages shared context between agents
6. **Output Generator** (`output/`): Creates project artifacts on disk
7. **Agent Templates** (`templates/`): Stores predefined agent types
8. **Agent Definition** (`agent_definition/`): Custom agent configuration
9. **Error Handling** (`error_handling/`): Manages errors and recovery
10. **Dependency Graph** (`dependency_graph/`): Optimizes parallel execution

## 🧩 Agent Roles

DAI Assistant includes templates for these core agent types:

- **Project Manager**: Gathers requirements and manages project scope
- **Architect**: Designs system components and technical architecture
- **Developer**: Implements code based on architecture and requirements
- **QA Engineer**: Creates tests and validates code quality
- **DevOps Engineer**: Configures deployment and CI/CD pipelines
- **Technical Writer**: Produces documentation and explanations

## 🔧 Configuration

Agent configurations use YAML format:

```yaml
name: security-expert
role: Security Engineer
backstory: |
  An experienced security professional specializing in secure coding practices
  and vulnerability assessment for web applications.
prompt_template: |
  You are a Security Engineer reviewing code for security vulnerabilities.
  Focus on identifying potential issues in: {{context}}
```

## 📚 Development

To set up a development environment:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black dai_assistant tests
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 