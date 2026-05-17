"""
Folder Tree Generator
Creates visual representation of repository folder structure
"""

from pathlib import Path
from typing import List, Optional, Set
import os

from shared.logger import logger
from shared.constants import IGNORE_DIRECTORIES


class FolderTreeGenerator:
    """
    Generates folder tree visualization
    
    Features:
    - Clean readable folder hierarchy
    - Ignore unnecessary directories
    - Customizable depth
    - ASCII tree format
    """
    
    def __init__(self, max_depth: int = 5):
        """
        Initialize folder tree generator
        
        Args:
            max_depth: Maximum depth to traverse
        """
        self.max_depth = max_depth
        self.ignore_dirs = set(IGNORE_DIRECTORIES)
        logger.info(f"FolderTreeGenerator initialized with max_depth={max_depth}")
    
    def generate_tree(
        self,
        root_path: Path,
        prefix: str = "",
        is_last: bool = True,
        current_depth: int = 0,
        show_files: bool = False
    ) -> str:
        """
        Generate folder tree as string
        
        Args:
            root_path: Root directory path
            prefix: Prefix for tree lines
            is_last: Whether this is the last item
            current_depth: Current depth in tree
            show_files: Whether to show files or only directories
            
        Returns:
            Tree structure as string
        """
        if current_depth > self.max_depth:
            return ""
        
        lines = []
        
        # Add current directory/file
        if current_depth > 0:
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{root_path.name}/")
        else:
            lines.append(f"{root_path.name}/")
        
        # Get children
        try:
            children = sorted(root_path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        except PermissionError:
            return "\n".join(lines)
        
        # Filter children
        dirs = [c for c in children if c.is_dir() and not self._should_ignore(c.name)]
        files = [c for c in children if c.is_file()] if show_files else []
        
        all_items = dirs + files
        
        # Process children
        for i, child in enumerate(all_items):
            is_last_child = (i == len(all_items) - 1)
            
            if current_depth > 0:
                extension = "    " if is_last else "│   "
                new_prefix = prefix + extension
            else:
                new_prefix = ""
            
            if child.is_dir():
                # Recursively process directory
                subtree = self.generate_tree(
                    child,
                    new_prefix,
                    is_last_child,
                    current_depth + 1,
                    show_files
                )
                lines.append(subtree)
            else:
                # Add file
                connector = "└── " if is_last_child else "├── "
                lines.append(f"{new_prefix}{connector}{child.name}")
        
        return "\n".join(lines)
    
    def generate_simple_tree(
        self,
        root_path: Path,
        max_items: int = 50
    ) -> str:
        """
        Generate a simplified tree with limited items
        
        Args:
            root_path: Root directory path
            max_items: Maximum number of items to show
            
        Returns:
            Simplified tree structure
        """
        lines = []
        item_count = 0
        
        def add_directory(path: Path, indent: int = 0):
            nonlocal item_count
            
            if item_count >= max_items:
                return
            
            try:
                children = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            except PermissionError:
                return
            
            dirs = [c for c in children if c.is_dir() and not self._should_ignore(c.name)]
            
            for dir_path in dirs:
                if item_count >= max_items:
                    break
                
                lines.append("  " * indent + f"├── {dir_path.name}/")
                item_count += 1
                
                if indent < 2:  # Limit depth for simple tree
                    add_directory(dir_path, indent + 1)
        
        lines.append(f"{root_path.name}/")
        add_directory(root_path, 1)
        
        if item_count >= max_items:
            lines.append("  ... (truncated)")
        
        return "\n".join(lines)
    
    def generate_markdown_tree(
        self,
        root_path: Path,
        include_files: bool = False
    ) -> str:
        """
        Generate tree in markdown format
        
        Args:
            root_path: Root directory path
            include_files: Whether to include files
            
        Returns:
            Markdown formatted tree
        """
        lines = ["```"]
        lines.append(self.generate_tree(root_path, show_files=include_files))
        lines.append("```")
        return "\n".join(lines)
    
    def get_directory_structure(
        self,
        root_path: Path,
        max_depth: int = 3
    ) -> dict:
        """
        Get directory structure as nested dictionary
        
        Args:
            root_path: Root directory path
            max_depth: Maximum depth to traverse
            
        Returns:
            Nested dictionary representing structure
        """
        def build_tree(path: Path, depth: int = 0) -> dict:
            if depth > max_depth:
                return {}
            
            tree = {
                'name': path.name,
                'type': 'directory' if path.is_dir() else 'file',
                'children': []
            }
            
            if path.is_dir():
                try:
                    children = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name))
                    dirs = [c for c in children if c.is_dir() and not self._should_ignore(c.name)]
                    
                    for child in dirs:
                        tree['children'].append(build_tree(child, depth + 1))
                except PermissionError:
                    pass
            
            return tree
        
        return build_tree(root_path)
    
    def count_directories(self, root_path: Path) -> int:
        """
        Count total number of directories
        
        Args:
            root_path: Root directory path
            
        Returns:
            Number of directories
        """
        count = 0
        
        try:
            for item in root_path.rglob('*'):
                if item.is_dir() and not self._should_ignore(item.name):
                    count += 1
        except Exception as e:
            logger.error(f"Error counting directories: {str(e)}")
        
        return count
    
    def get_largest_directories(
        self,
        root_path: Path,
        top_n: int = 5
    ) -> List[dict]:
        """
        Find largest directories by file count
        
        Args:
            root_path: Root directory path
            top_n: Number of top directories to return
            
        Returns:
            List of directory info dictionaries
        """
        dir_sizes = []
        
        try:
            for item in root_path.iterdir():
                if item.is_dir() and not self._should_ignore(item.name):
                    file_count = sum(1 for _ in item.rglob('*') if _.is_file())
                    dir_sizes.append({
                        'name': item.name,
                        'path': str(item.relative_to(root_path)),
                        'file_count': file_count
                    })
        except Exception as e:
            logger.error(f"Error getting largest directories: {str(e)}")
        
        # Sort by file count and return top N
        dir_sizes.sort(key=lambda x: x['file_count'], reverse=True)
        return dir_sizes[:top_n]
    
    def _should_ignore(self, dir_name: str) -> bool:
        """
        Check if directory should be ignored
        
        Args:
            dir_name: Directory name
            
        Returns:
            True if should be ignored
        """
        # Check exact matches
        if dir_name in self.ignore_dirs:
            return True
        
        # Check if starts with dot (hidden)
        if dir_name.startswith('.'):
            return True
        
        # Check common patterns
        ignore_patterns = ['__pycache__', 'node_modules', 'venv', 'env', 'dist', 'build']
        if any(pattern in dir_name.lower() for pattern in ignore_patterns):
            return True
        
        return False
    
    def generate_compact_tree(
        self,
        root_path: Path,
        max_lines: int = 30
    ) -> str:
        """
        Generate a compact tree suitable for display
        
        Args:
            root_path: Root directory path
            max_lines: Maximum number of lines
            
        Returns:
            Compact tree string
        """
        lines = []
        line_count = 0
        
        def add_dir(path: Path, prefix: str = "", is_last: bool = True, depth: int = 0):
            nonlocal line_count
            
            if line_count >= max_lines or depth > 3:
                return
            
            # Add current directory
            if depth > 0:
                connector = "└── " if is_last else "├── "
                lines.append(f"{prefix}{connector}{path.name}/")
                line_count += 1
            else:
                lines.append(f"{path.name}/")
                line_count += 1
            
            if line_count >= max_lines:
                return
            
            # Get subdirectories
            try:
                children = sorted(
                    [c for c in path.iterdir() if c.is_dir() and not self._should_ignore(c.name)],
                    key=lambda x: x.name
                )
            except PermissionError:
                return
            
            # Process children
            for i, child in enumerate(children):
                if line_count >= max_lines:
                    break
                
                is_last_child = (i == len(children) - 1)
                extension = "    " if is_last else "│   "
                new_prefix = prefix + extension if depth > 0 else ""
                
                add_dir(child, new_prefix, is_last_child, depth + 1)
        
        add_dir(root_path)
        
        if line_count >= max_lines:
            lines.append("... (truncated)")
        
        return "\n".join(lines)


# Made with Bob