"""
Output Generator Module.
Writes artifacts to disk: source code files, README.md, deployment docs, etc.
"""
from typing import Dict, Any, Union, List, Optional
import json
import yaml
import os
from pathlib import Path
import shutil

class OutputGenerator:
    """
    Output Generator for writing artifacts to disk.
    
    Supports multiple formats: markdown, code, YAML, JSON.
    """
    
    def __init__(self, output_dir: str):
        """
        Initialize the output generator.
        
        Args:
            output_dir: Base directory for output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def write_file(self, path: str, content: str, overwrite: bool = False) -> str:
        """
        Write content to a file.
        
        Args:
            path: Relative path for the file
            content: Content to write
            overwrite: Whether to overwrite existing files
            
        Returns:
            Absolute path to the created file
        """
        full_path = self.output_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        if full_path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {full_path}")
        
        with open(full_path, "w", encoding='utf-8') as f:
            f.write(content)
        
        return str(full_path)
    
    def write_json(self, path: str, data: Union[Dict, List], 
                   pretty: bool = True, overwrite: bool = False) -> str:
        """
        Write data as JSON to a file.
        
        Args:
            path: Relative path for the file
            data: Data to write as JSON
            pretty: Whether to format the JSON with indentation
            overwrite: Whether to overwrite existing files
            
        Returns:
            Absolute path to the created file
        """
        # Ensure the file has a .json extension
        if not path.lower().endswith('.json'):
            path = f"{path}.json"
        
        indent = 2 if pretty else None
        content = json.dumps(data, indent=indent)
        
        return self.write_file(path, content, overwrite)
    
    def write_yaml(self, path: str, data: Union[Dict, List], 
                  overwrite: bool = False) -> str:
        """
        Write data as YAML to a file.
        
        Args:
            path: Relative path for the file
            data: Data to write as YAML
            overwrite: Whether to overwrite existing files
            
        Returns:
            Absolute path to the created file
        """
        # Ensure the file has a .yaml or .yml extension
        if not (path.lower().endswith('.yaml') or path.lower().endswith('.yml')):
            path = f"{path}.yaml"
        
        content = yaml.dump(data, default_flow_style=False)
        
        return self.write_file(path, content, overwrite)
    
    def write_markdown(self, path: str, content: str, 
                      overwrite: bool = False) -> str:
        """
        Write markdown content to a file.
        
        Args:
            path: Relative path for the file
            content: Markdown content
            overwrite: Whether to overwrite existing files
            
        Returns:
            Absolute path to the created file
        """
        # Ensure the file has a .md extension
        if not path.lower().endswith('.md'):
            path = f"{path}.md"
        
        return self.write_file(path, content, overwrite)
    
    def write_code_file(self, path: str, content: str, 
                       overwrite: bool = False) -> str:
        """
        Write code to a file (preserving file extension).
        
        Args:
            path: Relative path for the file
            content: Code content
            overwrite: Whether to overwrite existing files
            
        Returns:
            Absolute path to the created file
        """
        return self.write_file(path, content, overwrite)
    
    def write_project_structure(self, structure: Dict[str, Any]) -> List[str]:
        """
        Write a complete project structure from a nested dictionary.
        
        The dictionary should have keys as file/directory names and values as either:
        - String content for files
        - Nested dictionaries for directories
        
        Args:
            structure: Dictionary representing the project structure
            
        Returns:
            List of paths created
        """
        created_paths = []
        
        def process_item(item: Dict[str, Any], current_path: Path):
            for name, content in item.items():
                path = current_path / name
                
                if isinstance(content, dict):
                    # This is a directory
                    path.mkdir(parents=True, exist_ok=True)
                    created_paths.append(str(path))
                    process_item(content, path)
                else:
                    # This is a file
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with open(path, "w", encoding='utf-8') as f:
                        f.write(str(content))
                    created_paths.append(str(path))
        
        process_item(structure, self.output_dir)
        return created_paths
    
    def clean_output_directory(self) -> None:
        """
        Clean the output directory, removing all files and subdirectories.
        """
        for item in self.output_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    
    def get_output_path(self, relative_path: Optional[str] = None) -> str:
        """
        Get the absolute path to the output directory or a subdirectory.
        
        Args:
            relative_path: Optional relative path within the output directory
            
        Returns:
            Absolute path
        """
        if relative_path:
            return str((self.output_dir / relative_path).resolve())
        return str(self.output_dir.resolve())
