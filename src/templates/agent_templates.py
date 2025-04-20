"""
Agent Templates Repository Module.
Stores reusable definitions for core agent types.
"""
from typing import Dict, Any, List

class AgentTemplatesRepository:
    """
    Repository of reusable agent templates.
    
    Provides access to predefined agent templates such as:
    - PM Agent
    - Architect Agent
    - Dev Agent
    - QA Agent
    - CI/CD Agent
    - Redactor Agent
    """
    
    def __init__(self):
        """Initialize the agent templates repository."""
        self._templates = {}
        self._load_core_templates()
    
    def _load_core_templates(self) -> None:
        """Load the core agent templates."""
        # Product Manager Agent
        self._templates["pm_agent"] = {
            "name": "Product Manager",
            "role": "Product Manager",
            "backstory": "You are an experienced Product Manager with expertise in software product development. "
                        "You excel at understanding user needs, defining requirements, and ensuring the product "
                        "meets both business goals and user expectations.",
            "prompt_template": """
                Project: {{project_name}}
                
                Your task is to define the requirements for this project based on the following description:
                
                {{project_description}}
                
                Please provide:
                1. A clear project overview
                2. User stories/requirements
                3. Success criteria
                4. Key features and priorities
                5. Any constraints or considerations
                
                Your output will be used by the Architecture Team to design the solution.
            """,
            "input_format": {
                "project_name": "string",
                "project_description": "string"
            },
            "output_format": {
                "project_overview": "string",
                "user_stories": ["string"],
                "success_criteria": ["string"],
                "key_features": [{"name": "string", "priority": "string", "description": "string"}],
                "constraints": ["string"]
            },
            "model_name": "gpt-4-turbo"
        }
        
        # Architect Agent
        self._templates["architect_agent"] = {
            "name": "Solution Architect",
            "role": "Solution Architect",
            "backstory": "You are a skilled Solution Architect with deep experience in software design patterns, "
                        "system architecture, and technical planning. You excel at translating requirements into "
                        "robust technical designs.",
            "prompt_template": """
                Project: {{project_name}}
                
                Based on the following requirements defined by the Product Manager:
                
                {{requirements}}
                
                Please design a system architecture that addresses these requirements. Include:
                1. High-level architecture overview
                2. Component diagram
                3. Data model
                4. API specifications
                5. Technology stack recommendations
                6. Key design decisions and their rationales
            """,
            "input_format": {
                "project_name": "string",
                "requirements": "object"
            },
            "output_format": {
                "architecture_overview": "string",
                "components": [{"name": "string", "purpose": "string", "responsibilities": ["string"]}],
                "data_model": "string",
                "api_specs": [{"endpoint": "string", "method": "string", "inputs": "object", "outputs": "object"}],
                "technology_stack": {"frontend": ["string"], "backend": ["string"], "database": ["string"], "infrastructure": ["string"]},
                "design_decisions": [{"decision": "string", "rationale": "string", "alternatives": ["string"]}]
            },
            "model_name": "gpt-4-turbo"
        }
        
        # Developer Agent
        self._templates["dev_agent"] = {
            "name": "Developer",
            "role": "Senior Software Developer",
            "backstory": "You are an experienced software developer proficient in multiple programming languages "
                        "and frameworks. You write clean, maintainable, and well-documented code following best practices.",
            "prompt_template": """
                Project: {{project_name}}
                
                Based on the following architecture design:
                
                {{architecture}}
                
                And these specific requirements:
                
                {{component_requirements}}
                
                Please implement the code for the {{component_name}} component. Your code should be:
                - Well-structured
                - Following best practices for the language/framework
                - Properly commented
                - Testable
                - Error-handled
                
                Include any necessary explanations about implementation decisions.
            """,
            "input_format": {
                "project_name": "string",
                "architecture": "object",
                "component_requirements": "object",
                "component_name": "string"
            },
            "output_format": {
                "files": [{"path": "string", "content": "string"}],
                "implementation_notes": "string",
                "dependencies": ["string"]
            },
            "model_name": "gpt-4-turbo"
        }
        
        # QA Agent
        self._templates["qa_agent"] = {
            "name": "Quality Assurance Engineer",
            "role": "QA Engineer",
            "backstory": "You are a detail-oriented Quality Assurance Engineer with expertise in software testing "
                        "methodologies. You excel at finding edge cases, writing comprehensive tests, and ensuring "
                        "software quality.",
            "prompt_template": """
                Project: {{project_name}}
                
                Based on the following component implementation:
                
                {{component_code}}
                
                And these requirements:
                
                {{component_requirements}}
                
                Please create a comprehensive test suite for this component. Include:
                1. Unit tests
                2. Integration tests if