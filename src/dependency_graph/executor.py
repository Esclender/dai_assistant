"""
Dependency Graph Executor Module

This module handles the execution of agents based on their dependencies,
allowing for parallel execution when possible.
"""

import asyncio
import logging
from typing import Dict, List, Set, Any, Callable, Awaitable, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AgentTask:
    """Represents an agent task in the dependency graph."""
    agent_id: str
    depends_on: List[str]  # IDs of agents this task depends on
    executor: Callable[..., Awaitable[Any]]  # Function to execute the agent
    args: tuple = ()
    kwargs: Dict[str, Any] = None
    result: Any = None
    completed: bool = False


class DependencyGraphExecutor:
    """
    Manages the execution of interdependent agent tasks.
    Optimizes for parallel execution when dependencies allow.
    """

    def __init__(self):
        self.tasks: Dict[str, AgentTask] = {}
        self.results: Dict[str, Any] = {}

    def add_task(
        self,
        agent_id: str,
        executor: Callable[..., Awaitable[Any]],
        depends_on: List[str] = None,
        args: tuple = None,
        kwargs: Dict[str, Any] = None
    ) -> None:
        """
        Add a task to the dependency graph.
        
        Args:
            agent_id: Unique identifier for the agent task
            executor: Async function that executes the agent's work
            depends_on: List of agent IDs this task depends on
            args: Positional arguments for the executor
            kwargs: Keyword arguments for the executor
        """
        self.tasks[agent_id] = AgentTask(
            agent_id=agent_id,
            depends_on=depends_on or [],
            executor=executor,
            args=args or (),
            kwargs=kwargs or {},
        )

    def _get_ready_tasks(self, completed_tasks: Set[str]) -> List[str]:
        """Find tasks whose dependencies are all satisfied."""
        ready_tasks = []
        
        for task_id, task in self.tasks.items():
            if task.completed:
                continue
                
            if all(dep in completed_tasks for dep in task.depends_on):
                ready_tasks.append(task_id)
                
        return ready_tasks

    async def _execute_task(self, task_id: str) -> Any:
        """Execute a single task and store its result."""
        task = self.tasks[task_id]
        
        # Prepare kwargs with results from dependencies
        kwargs = task.kwargs.copy() if task.kwargs else {}
        
        # Add dependency results to kwargs if not already there
        for dep_id in task.depends_on:
            dep_result_key = f"{dep_id}_result"
            if dep_result_key not in kwargs:
                kwargs[dep_result_key] = self.results[dep_id]
        
        try:
            logger.info(f"Executing task: {task_id}")
            result = await task.executor(*task.args, **kwargs)
            self.tasks[task_id].completed = True
            self.results[task_id] = result
            logger.info(f"Task completed: {task_id}")
            return result
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            raise

    async def execute(self, max_concurrent: int = 5) -> Dict[str, Any]:
        """
        Execute all tasks respecting their dependencies.
        
        Args:
            max_concurrent: Maximum number of tasks to run concurrently
            
        Returns:
            Dictionary mapping task IDs to their results
        """
        completed_tasks: Set[str] = set()
        
        while len(completed_tasks) < len(self.tasks):
            ready_tasks = self._get_ready_tasks(completed_tasks)
            
            if not ready_tasks:
                if len(completed_tasks) < len(self.tasks):
                    logger.error("Deadlock detected in dependency graph")
                    raise RuntimeError("Deadlock detected in dependency graph")
                break
            
            # Execute ready tasks concurrently with limits
            tasks = [self._execute_task(task_id) for task_id in ready_tasks[:max_concurrent]]
            await asyncio.gather(*tasks)
            
            # Update completed tasks
            completed_tasks.update([
                task_id for task_id, task in self.tasks.items() if task.completed
            ])
        
        return self.results

    def visualize(self) -> str:
        """
        Generate a simple text representation of the dependency graph.
        
        Returns:
            A string visualizing the dependency graph
        """
        result = []
        result.append("Dependency Graph:")
        
        # Find root nodes (tasks with no dependencies)
        root_nodes = [task_id for task_id, task in self.tasks.items() 
                     if not task.depends_on]
        
        visited = set()
        
        def _visualize_node(node_id: str, depth: int = 0):
            if node_id in visited:
                return
                
            visited.add(node_id)
            indent = "  " * depth
            result.append(f"{indent}└─ {node_id}")
            
            # Find dependent tasks
            dependents = [task_id for task_id, task in self.tasks.items()
                         if node_id in task.depends_on]
            
            for dependent in dependents:
                _visualize_node(dependent, depth + 1)
        
        # Start with root nodes
        for root in root_nodes:
            _visualize_node(root)
            
        return "\n".join(result)
