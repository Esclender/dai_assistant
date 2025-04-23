"""
CLI Interface for Dai Assistant.
Entry point for command-line operations.
"""
import click
from rich.console import Console
import asyncio
from llm_connector.provider_factory import LLMProviderFactory
from llm_connector.exceptions import LLMProviderError, UnsupportedModelError, InvalidProviderError
from dotenv import load_dotenv
load_dotenv()

console = Console()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.1.0', prog_name='Dai Assistant')
def cli():
    """🤖 Dai Assistant - Orchestrate collaborative AI agents.
    
    Dai Assistant is a powerful CLI tool for managing teams of AI agents that collaborate
    to create high-quality software projects. Each agent has specific roles and expertise.

    Basic Usage Examples:

    \b
    # Initialize a new project
    dai init --project-name my-api-project

    \b
    # Run a project with custom agent team
    dai run --agents-config configs/my-team.yaml --project-name my-api-project

    For more information about a specific command, run:
    dai COMMAND --help
    """
    pass

@cli.command()
@click.option("--project-name", "-p", 
              help="Name of the project to initialize. Will create a directory with this name.")
def init(project_name):
    """Initialize a new project with default agent configuration.

    This command creates a new project directory with:
    - Default agent configuration files
    - Project structure
    - Basic templates

    Examples:

    \b
    # Create a new project named 'my-api'
    dai init --project-name my-api

    \b
    # Create a new project with short option
    dai init -p my-webapp
    """
    console.print(f"[bold green]Initializing project:[/bold green] {project_name}")
    # TODO: Implementation for project initialization

@cli.command()
@click.option("--agents-config", "-a", required=True, 
              help="Path to YAML file containing agent configurations")
@click.option("--project-name", "-p", required=True, 
              help="Name of the project to run")
def run(agents_config, project_name):
    """Run the multi-agent orchestration with specified configuration.

    Start the collaborative AI process with your defined team of agents.
    Agents will work together based on their roles and the project requirements.

    Examples:

    \b
    # Run with default team configuration
    dai run -a configs/default-team.yaml -p my-project

    \b
    # Run with custom team and specific project
    dai run --agents-config configs/specialized-team.yaml \\
            --project-name my-api-project
    """
    console.print(f"[bold green]Running project:[/bold green] {project_name}")
    console.print(f"[bold blue]Using agents configuration:[/bold blue] {agents_config}")
    # TODO: Implementation for running the orchestration

@cli.command()
@click.argument('topic', required=False)
def help(topic):
    """Get detailed help about Dai Assistant and its features.

    \b
    Available help topics:
    - agents: Learn about agent roles and capabilities
    - config: Configuration file format and options
    - examples: See more usage examples
    - workflow: Understand the AI collaboration workflow

    Examples:

    \b
    # Get general help
    dai help

    \b
    # Get help about a specific topic
    dai help agents
    dai help config
    """
    topics = {
        'agents': """
    🤖 Agent Roles and Capabilities
    ------------------------------
    Dai Assistant supports various specialized agents:

    - Project Manager: Coordinates the team and manages requirements
    - Architect: Designs system architecture and makes technical decisions
    - Developer: Implements features and writes code
    - QA Engineer: Tests and ensures code quality
    - Security Expert: Reviews code for vulnerabilities
    - DevOps Engineer: Handles deployment and infrastructure
    - Technical Writer: Creates documentation
        """,
        'config': """
    📝 Configuration Guide
    --------------------
    Agent configurations use YAML format:

    ```yaml
    name: security-expert
    role: Security Engineer
    backstory: |
      An experienced security professional...
    output_format: markdown
    ```

    Save configurations in the configs/ directory.
        """,
        'examples': """
    📚 Usage Examples
    ---------------
    1. Create and run a new project:
       dai init -p my-project
       dai run -a configs/team.yaml -p my-project

    2. Load existing configuration:
       dai load-config -c configs/saved-team.yaml
        """,
        'workflow': """
    🔄 AI Collaboration Workflow
    -------------------------
    1. Initialize project structure
    2. Define specialized agents
    3. Configure team composition
    4. Run the collaboration
    5. Review and iterate results
        """
    }

    if topic:
        if topic in topics:
            console.print(topics[topic])
        else:
            console.print("[red]Topic not found. Run 'dai help' to see available topics.[/red]")
    else:
        ctx = click.get_current_context()
        click.echo(ctx.parent.get_help())

async def _send(provider: str, model: str, message: str):
    """Async implementation of the send command."""
    try:
        # Create provider instance
        provider_instance = LLMProviderFactory.create_provider(provider, model)
        
        # Send message
        response = await provider_instance.send_message(message)
        
        console.print(f"\n[green]Success![/green] Message received by {provider} ({model})")
        console.print(f"Response: {response['message']}")
        
    except UnsupportedModelError as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        console.print("\n[bold]Tip:[/bold] Use 'dai models' to see available models")
        raise
    except InvalidProviderError as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        console.print("\n[bold]Tip:[/bold] Use 'dai models' to see available providers")
        raise
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise

@cli.command()
@click.option("--provider", "-p", type=click.Choice(['openai', 'anthropic']), required=True,
              help="LLM provider to use (openai or anthropic)")
@click.option("--model", "-m", required=True,
              help="Model name to use (e.g., gpt-4, claude-3-7-sonnet)")
@click.argument("message")
def send(provider: str, model: str, message: str):
    """Send a message to the selected LLM provider.

    This command sends a message to the specified LLM provider and model.
    Currently, it only confirms receipt of the message.

    Examples:
    
    \b
    # Send message to OpenAI's GPT-4
    dai send --provider openai --model gpt-4 "Hello, how are you?"
    
    \b
    # Send message to Anthropic's Claude 3.7
    dai send --provider anthropic --model claude-3-7-sonnet "What's the weather like?"
    """
    asyncio.run(_send(provider, model, message))

@cli.command()
@click.option("--provider", "-p", type=click.Choice(['openai', 'anthropic']),
              help="List models for a specific provider")
def models(provider: str):
    """List available models for LLM providers.

    This command shows all available models for either a specific provider
    or all providers if no provider is specified.

    Examples:
    
    \b
    # List all models for all providers
    dai models
    
    \b
    # List only OpenAI models
    dai models --provider openai
    """
    try:
        models = LLMProviderFactory.list_models(provider)
        
        if provider:
            console.print(f"\n[green]Available models for {provider}:[/green]")
            for model in models[provider]:
                console.print(f"  - {model}")
        else:
            console.print("\n[green]Available models by provider:[/green]")
            for provider_name, model_list in models.items():
                console.print(f"\n[bold]{provider_name}[/bold] models:")
                for model in model_list:
                    console.print(f"  - {model}")
        
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {str(e)}")
        raise

@cli.command()
@click.option('--config', '-c', default='agents_config.yaml', show_default=True, help='Path to the agents YAML config file.')
def list_agents(config):
    """List all available agents from the YAML config file."""
    import yaml
    try:
        with open(config, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        agents = data.get('agents', [])
        if not agents:
            console.print("[yellow]No agents found in the config file.[/yellow]")
            return
        console.print(f"[bold green]Agents in {config}:[/bold green]")
        for agent in agents:
            console.print(f"\n[bold]{agent.get('name', 'N/A')}[/bold] | Role: {agent.get('role', 'N/A')} | Model: {agent.get('model', 'N/A')}")
            console.print(f"  [dim]Description:[/dim] {agent.get('description', '').strip()}")
    except FileNotFoundError:
        console.print(f"[red]Config file not found:[/red] {config}")
    except Exception as e:
        console.print(f"[red]Error loading agents:[/red] {str(e)}")

@cli.command()
@click.option('--config', '-c', default='agents_config.yaml', show_default=True, help='Path to the agents YAML config file.')
def list_groups(config):
    """List all groups and their member agents from the YAML config file."""
    import yaml
    try:
        with open(config, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        agents = {agent['name']: agent for agent in data.get('agents', [])}
        groups = data.get('groups', [])
        if not groups:
            console.print("[yellow]No groups found in the config file.[/yellow]")
            return
        console.print(f"[bold green]Groups in {config}:[/bold green]")
        for group in groups:
            console.print(f"\n[bold]{group.get('name', 'N/A')}[/bold] ([dim]{group.get('description', '')}[/dim])")
            members = group.get('members', [])
            if not members:
                console.print("  [yellow]No members in this group.[/yellow]")
            for member in members:
                agent = agents.get(member)
                if agent:
                    console.print(f"  - [bold]{agent['name']}[/bold] | Role: {agent['role']} | Model: {agent['model']}")
                else:
                    console.print(f"  - [red]{member} (not found in agents list)[/red]")
    except FileNotFoundError:
        console.print(f"[red]Config file not found:[/red] {config}")
    except Exception as e:
        console.print(f"[red]Error loading groups:[/red] {str(e)}")

if __name__ == "__main__":
    cli()
