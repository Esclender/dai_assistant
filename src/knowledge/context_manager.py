"""
Knowledge Aggregator & Context Manager Module.
Collects results from all agents and maintains shared context.
"""
from typing import Dict, Any, List, Optional
import json
from pathlib import Path

class ContextManager:
    """
    Knowledge Aggregator and Context Manager.
    
    Collects and organizes results from all agents.
    Builds a shared context for agents to consume.
    """
    
    def __init__(self, project_name: str, base_dir: Optional[str] = None):
        """
        Initialize the context manager.
        
        Args:
            project_name: Name of the project
            base_dir: Optional base directory for context storage
        """
        self.project_name = project_name
        self.base_dir = Path(base_dir or ".").resolve()
        self.context: Dict[str, Any] = {
            "project_name": project_name,
            "agents": {},
            "artifacts": {},
            "messages": []
        }
        
        # Ensure context directory exists
        self.context_dir = self.base_dir / "contexts" / project_name
        self.context_dir.mkdir(parents=True, exist_ok=True)
    
    def add_agent_result(self, agent_id: str, result: Dict[str, Any]) -> None:
        """
        Add an agent's result to the shared context.
        
        Args:
            agent_id: ID of the agent
            result: Result data from the agent
        """
        if agent_id not in self.context["agents"]:
            self.context["agents"][agent_id] = []
        
        # Add result with timestamp
        import time
        result_with_meta = {
            "timestamp": time.time(),
            "data": result
        }
        
        self.context["agents"][agent_id].append(result_with_meta)
        
        # Process artifacts if present
        if "artifacts" in result:
            for artifact_name, artifact_content in result["artifacts"].items():
                self.add_artifact(f"{agent_id}_{artifact_name}", artifact_content)
    
    def add_artifact(self, artifact_id: str, content: Any) -> None:
        """
        Add an artifact to the context.
        
        Args:
            artifact_id: ID of the artifact
            content: Content of the artifact
        """
        self.context["artifacts"][artifact_id] = content
    
    def add_message(self, from_agent: str, to_agent: str, content: Any) -> None:
        """
        Add a message between agents to the context.
        
        Args:
            from_agent: ID of the sending agent
            to_agent: ID of the receiving agent
            content: Message content
        """
        import time
        message = {
            "timestamp": time.time(),
            "from": from_agent,
            "to": to_agent,
            "content": content
        }
        self.context["messages"].append(message)
    
    def get_full_context(self) -> Dict[str, Any]:
        """
        Get the complete context.
        
        Returns:
            The full context dictionary
        """
        return self.context
    
    def get_agent_context(self, agent_id: str) -> Dict[str, Any]:
        """
        Get the context filtered for a specific agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent-specific context
        """
        # Filter messages to/from this agent
        relevant_messages = [
            msg for msg in self.context["messages"]
            if msg["from"] == agent_id or msg["to"] == agent_id
        ]
        
        # Build agent-specific context
        agent_context = {
            "project_name": self.project_name,
            "agent_id": agent_id,
            "messages": relevant_messages,
            "artifacts": self.context["artifacts"]
        }
        
        # Include the agent's own previous results
        if agent_id in self.context["agents"]:
            agent_context["previous_results"] = self.context["agents"][agent_id]
        
        return agent_context
    
    def save_context(self) -> str:
        """
        Save the current context to disk.
        
        Returns:
            Path to the saved context file
        """
        import time
        timestamp = int(time.time())
        filename = f"context_{timestamp}.json"
        filepath = self.context_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(self.context, f, indent=2)
        
        return str(filepath)
    
    def load_context(self, filepath: str) -> None:
        """
        Load context from a file.
        
        Args:
            filepath: Path to the context file
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Context file not found: {filepath}")
        
        with open(path, "r") as f:
            loaded_context = json.load(f)
        
        self.context = loaded_context
        self.project_name = loaded_context.get("project_name", self.project_name)
    
    def get_latest_results(self, agent_id: str, count: int = 1) -> List[Dict[str, Any]]:
        """
        Get the latest results from a specific agent.
        
        Args:
            agent_id: ID of the agent
            count: Number of latest results to retrieve
            
        Returns:
            List of latest results
        """
        if agent_id not in self.context["agents"]:
            return []
        
        results = sorted(
            self.context["agents"][agent_id],
            key=lambda x: x["timestamp"],
            reverse=True
        )
        
        return [r["data"] for r in results[:count]]
    
    def clear_context(self) -> None:
        """Clear the current context."""
        self.context = {
            "project_name": self.project_name,
            "agents": {},
            "artifacts": {},
            "messages": []
        }
