"""
Custom Agent Definition System.
Allows users to define and manage their own agents.
"""
from typing import Dict, Any, List, Optional
import os
import yaml
import json
from pydantic import BaseModel, Field
from pathlib import Path

class AgentPrompt(BaseModel):
    """Model for agent prompt templates."""
    system: str = Field(..., description="System instruction for the agent")
    task: str = Field(..., description="Task template for the agent")
    examples: Optional[List[Dict[str, str]]] = Field(None, description="Examples to guide the agent")

class AgentDefinition(BaseModel):
    """Model for agent definition."""
    name: str = Field(..., description="Unique name of the agent")
    role: str = Field(..., description="Role of the agent (e.g., 'architect', 'dev')")
    backstory: str = Field("", description="Backstory to provide context and motivation")
    prompt: AgentPrompt = Field(..., description="Prompt templates for the agent")
    input_format: Dict[str, Any] = Field({}, description="Expected input format")
    output_format: Dict[str, Any] = Field({}, description="Expected output format")
    model_name: str = Field("gpt-4-turbo", description="LLM model to use for this agent")
    temperature: float = Field(0.7, description="Temperature setting for generation")
    max_tokens: int = Field(2000, description="Maximum tokens for generation")

class CustomAgentDefinitionSystem:
    """
    System for defining and managing custom agents.
    
    Allows users to create, save, load, and modify agent definitions.
    """
    
    def __init__(self, config_dir: str = "configs/agents"):
        """
        Initialize the custom agent definition system.
        
        Args:
            config_dir: Directory for storing agent configurations
        """
        self.config_dir = config_dir
        self._ensure_config_dir()
        
    def _ensure_config_dir(self) -> None:
        """Ensure the configuration directory exists."""
        os.makedirs(self.config_dir, exist_ok=True)
    
    def create_agent(self, agent_def: AgentDefinition) -> str:
        """
        Create and save a new agent definition.
        
        Args:
            agent_def: The agent definition
            
        Returns:
            Path to the saved agent configuration file
        """
        # Validate using pydantic
        valid_agent = AgentDefinition(**agent_def.dict())
        
        # Save the agent definition
        filepath = self._get_agent_filepath(valid_agent.name)
        self._save_agent(valid_agent, filepath)
        
        return filepath
    
    def load_agent(self, name: str) -> AgentDefinition:
        """
        Load an agent definition by name.
        
        Args:
            name: Name of the agent to load
            
        Returns:
            The agent definition
        """
        filepath = self._get_agent_filepath(name)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Agent configuration not found: {name}")
        
        return self._load_agent(filepath)
    
    def list_agents(self) -> List[str]:
        """
        List all available agent definitions.
        
        Returns:
            List of agent names
        """
        self._ensure_config_dir()
        
        agents = []
        for filename in os.listdir(self.config_dir):
            if filename.endswith(('.yaml', '.yml', '.json')):
                # Strip extension to get agent name
                agent_name = os.path.splitext(filename)[0]
                agents.append(agent_name)
                
        return agents
    
    def delete_agent(self, name: str) -> bool:
        """
        Delete an agent definition.
        
        Args:
            name: Name of the agent to delete
            
        Returns:
            True if deletion was successful
        """
        filepath = self._get_agent_filepath(name)
        
        if not os.path.exists(filepath):
            return False
        
        os.remove(filepath)
        return True
    
    def update_agent(self, name: str, updates: Dict[str, Any]) -> AgentDefinition:
        """
        Update an existing agent definition.
        
        Args:
            name: Name of the agent to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated agent definition
        """
        # Load existing agent
        agent_def = self.load_agent(name)
        
        # Update fields
        agent_dict = agent_def.dict()
        for key, value in updates.items():
            if key in agent_dict:
                agent_dict[key] = value
        
        # Create updated agent and save
        updated_agent = AgentDefinition(**agent_dict)
        filepath = self._get_agent_filepath(name)
        self._save_agent(updated_agent, filepath)
        
        return updated_agent
    
    def _get_agent_filepath(self, name: str) -> str:
        """
        Get the filepath for an agent configuration.
        
        Args:
            name: Agent name
            
        Returns:
            Filepath for the agent configuration
        """
        # Use YAML as the default format
        return os.path.join(self.config_dir, f"{name}.yaml")
    
    def _save_agent(self, agent: AgentDefinition, filepath: str) -> None:
        """
        Save an agent definition to file.
        
        Args:
            agent: Agent definition to save
            filepath: Path to save the configuration
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Determine file format based on extension
        if filepath.endswith(('.yaml', '.yml')):
            with open(filepath, 'w') as f:
                yaml.dump(agent.dict(), f, default_flow_style=False)
        elif filepath.endswith('.json'):
            with open(filepath, 'w') as f:
                json.dump(agent.dict(), f, indent=2)
        else:
            # Default to YAML
            filepath = f"{filepath}.yaml"
            with open(filepath, 'w') as f:
                yaml.dump(agent.dict(), f, default_flow_style=False)
    
    def _load_agent(self, filepath: str) -> AgentDefinition:
        """
        Load an agent definition from file.
        
        Args:
            filepath: Path to the agent configuration file
            
        Returns:
            Loaded agent definition
        """
        # Determine file format based on extension
        if filepath.endswith(('.yaml', '.yml')):
            with open(filepath, 'r') as f:
                agent_dict = yaml.safe_load(f)
        elif filepath.endswith('.json'):
            with open(filepath, 'r') as f:
                agent_dict = json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {filepath}")
        
        return AgentDefinition(**agent_dict)
    
    def create_agent_from_cli(self, name: str, role: str, backstory: str = "", output_format: str = "json") -> AgentDefinition:
        """
        Create an agent from CLI parameters.
        
        Args:
            name: Name of the agent
            role: Role of the agent
            backstory: Backstory for the agent
            output_format: Expected output format
            
        Returns:
            Created agent definition
        """
        # Create a basic prompt
        prompt = AgentPrompt(
            system=f"You are a {role}. {backstory}",
            task="Complete the task based on the following information: {{task_description}}",
            examples=None
        )
        
        # Determine output format structure
        if output_format.lower() == "json":
            out_format = {"type": "json", "schema": {}}
        elif output_format.lower() == "markdown":
            out_format = {"type": "markdown"}
        else:
            out_format = {"type": "text"}
        
        # Create agent definition
        agent_def = AgentDefinition(
            name=name,
            role=role,
            backstory=backstory,
            prompt=prompt,
            output_format=out_format
        )
        
        # Save the agent
        self.create_agent(agent_def)
        
        return agent_def
