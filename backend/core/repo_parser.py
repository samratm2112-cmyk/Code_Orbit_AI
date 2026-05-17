"""
Repository Parser - Main Orchestrator
Coordinates all repository analysis components
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from shared.logger import logger
from shared.config import settings
from backend.models.repository import (
    RepositoryMetadata,
    RepositoryAnalysis,
    RepositoryStatus,
    FileMetadata
)
from backend.core.repo_cloner import RepositoryCloner
from backend.utils.file_parser import FileParser
from backend.utils.tech_detector import TechnologyDetector
from backend.utils.repo_analyzer import RepositoryAnalyzer
from backend.utils.folder_tree import FolderTreeGenerator


class RepositoryParser:
    """
    Main repository parser that orchestrates all analysis components
    
    This is the central service that:
    1. Clones repositories
    2. Parses files
    3. Detects technologies
    4. Generates statistics
    5. Creates folder trees
    6. Prepares data for AI processing
    """
    
    def __init__(self):
        """Initialize repository parser with all components"""
        self.cloner = RepositoryCloner()
        self.file_parser = FileParser()
        self.tech_detector = TechnologyDetector()
        self.analyzer = RepositoryAnalyzer()
        self.tree_generator = FolderTreeGenerator()
        
        logger.info("RepositoryParser initialized with all components")
    
    async def parse_repository(
        self,
        url: str,
        branch: str = "main",
        include_content: bool = True
    ) -> RepositoryAnalysis:
        """
        Parse a complete repository
        
        Args:
            url: GitHub repository URL
            branch: Branch to analyze
            include_content: Whether to include file contents
            
        Returns:
            RepositoryAnalysis object with complete analysis
            
        Raises:
            Exception: If any step fails
        """
        logger.info(f"Starting repository analysis: {url}")
        
        try:
            # Step 1: Clone repository
            logger.info("Step 1/6: Cloning repository...")
            metadata = self.cloner.clone_repository(url, branch)
            metadata.status = RepositoryStatus.PARSING
            
            repo_path = Path(metadata.clone_path)
            
            # Step 2: Parse files
            logger.info("Step 2/6: Parsing files...")
            files = self.file_parser.parse_directory(
                repo_path,
                include_content=include_content,
                recursive=True
            )
            logger.info(f"Parsed {len(files)} files")
            
            # Step 3: Detect technology stack
            logger.info("Step 3/6: Detecting technology stack...")
            file_contents = {}
            if include_content:
                # Collect file contents for tech detection
                for file in files[:100]:  # Limit to first 100 files for performance
                    if file.content:
                        file_contents[file.path] = file.content
            
            tech_stack = self.tech_detector.detect_from_files(repo_path, file_contents)
            logger.info(f"Detected: {len(tech_stack.languages)} languages, "
                       f"{len(tech_stack.frameworks)} frameworks")
            
            # Step 4: Generate statistics
            logger.info("Step 4/6: Generating statistics...")
            statistics = self.analyzer.analyze(files, repo_path)
            
            # Step 5: Generate folder tree
            logger.info("Step 5/6: Generating folder tree...")
            folder_structure = self.tree_generator.generate_compact_tree(repo_path, max_lines=50)
            
            # Step 6: Identify important files and entry points
            logger.info("Step 6/6: Identifying important files...")
            important_files = self.analyzer.identify_important_files(files, repo_path)
            entry_points = self.analyzer.identify_entry_points(files)
            
            # Update metadata status
            metadata.status = RepositoryStatus.COMPLETED
            
            # Create complete analysis
            analysis = RepositoryAnalysis(
                metadata=metadata,
                statistics=statistics,
                technology_stack=tech_stack,
                folder_structure=folder_structure,
                files=files if include_content else [],
                important_files=important_files,
                entry_points=entry_points
            )
            
            logger.success(f"Repository analysis completed: {metadata.repo_id}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Repository analysis failed: {str(e)}")
            raise
    
    def get_repository_summary(
        self,
        analysis: RepositoryAnalysis
    ) -> Dict[str, Any]:
        """
        Generate a summary of repository analysis
        
        Args:
            analysis: RepositoryAnalysis object
            
        Returns:
            Dictionary with summary information
        """
        summary = {
            'repo_id': analysis.metadata.repo_id,
            'name': analysis.metadata.name,
            'owner': analysis.metadata.owner,
            'url': analysis.metadata.url,
            'branch': analysis.metadata.branch,
            'status': analysis.metadata.status,
            'analyzed_at': analysis.metadata.created_at.isoformat(),
            
            'statistics': {
                'total_files': analysis.statistics.total_files,
                'source_files': analysis.statistics.total_source_files,
                'total_lines': analysis.statistics.total_lines,
                'size_mb': round(analysis.statistics.total_size_bytes / 1024 / 1024, 2),
                'languages': list(analysis.statistics.languages_distribution.keys())[:5],
                'primary_language': list(analysis.statistics.languages_distribution.keys())[0]
                    if analysis.statistics.languages_distribution else None
            },
            
            'technology': {
                'languages': analysis.technology_stack.languages,
                'frameworks': analysis.technology_stack.frameworks,
                'tools': analysis.technology_stack.tools,
                'databases': analysis.technology_stack.databases
            },
            
            'structure': {
                'important_files': analysis.important_files[:10],
                'entry_points': analysis.entry_points[:5],
                'folder_tree_preview': '\n'.join(analysis.folder_structure.split('\n')[:15])
            }
        }
        
        return summary
    
    def prepare_for_embeddings(
        self,
        analysis: RepositoryAnalysis,
        max_files: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Prepare repository data for embedding generation
        
        Args:
            analysis: RepositoryAnalysis object
            max_files: Maximum number of files to include
            
        Returns:
            List of documents ready for embedding
        """
        documents = []
        
        # Add repository overview
        overview = {
            'type': 'overview',
            'content': self._create_overview_text(analysis),
            'metadata': {
                'repo_id': analysis.metadata.repo_id,
                'repo_name': analysis.metadata.name,
                'source': 'repository_overview'
            }
        }
        documents.append(overview)
        
        # Add important files first
        important_file_paths = set(analysis.important_files)
        important_files = [f for f in analysis.files if f.path in important_file_paths]
        
        for file in important_files[:20]:  # Limit important files
            if file.content and len(file.content.strip()) > 0:
                doc = {
                    'type': 'file',
                    'content': file.content,
                    'metadata': {
                        'repo_id': analysis.metadata.repo_id,
                        'file_path': file.path,
                        'language': file.language,
                        'size': file.size_bytes,
                        'lines': file.line_count,
                        'is_important': True
                    }
                }
                documents.append(doc)
        
        # Add other source files
        other_files = [f for f in analysis.files if f.path not in important_file_paths]
        for file in other_files[:max_files - len(documents)]:
            if file.content and len(file.content.strip()) > 0:
                doc = {
                    'type': 'file',
                    'content': file.content,
                    'metadata': {
                        'repo_id': analysis.metadata.repo_id,
                        'file_path': file.path,
                        'language': file.language,
                        'size': file.size_bytes,
                        'lines': file.line_count,
                        'is_important': False
                    }
                }
                documents.append(doc)
        
        logger.info(f"Prepared {len(documents)} documents for embeddings")
        return documents
    
    def _create_overview_text(self, analysis: RepositoryAnalysis) -> str:
        """Create overview text for the repository"""
        lines = [
            f"Repository: {analysis.metadata.name}",
            f"Owner: {analysis.metadata.owner}",
            f"URL: {analysis.metadata.url}",
            "",
            "Statistics:",
            f"- Total Files: {analysis.statistics.total_files}",
            f"- Source Files: {analysis.statistics.total_source_files}",
            f"- Lines of Code: {analysis.statistics.total_lines:,}",
            f"- Size: {analysis.statistics.total_size_bytes / 1024 / 1024:.2f} MB",
            "",
            "Languages:",
        ]
        
        for lang, count in list(analysis.statistics.languages_distribution.items())[:5]:
            lines.append(f"- {lang}: {count} files")
        
        if analysis.technology_stack.frameworks:
            lines.extend([
                "",
                "Frameworks:",
            ])
            for framework in analysis.technology_stack.frameworks[:5]:
                lines.append(f"- {framework}")
        
        if analysis.important_files:
            lines.extend([
                "",
                "Important Files:",
            ])
            for file_path in analysis.important_files[:10]:
                lines.append(f"- {file_path}")
        
        if analysis.entry_points:
            lines.extend([
                "",
                "Entry Points:",
            ])
            for entry in analysis.entry_points[:5]:
                lines.append(f"- {entry}")
        
        lines.extend([
            "",
            "Folder Structure:",
            analysis.folder_structure
        ])
        
        return "\n".join(lines)
    
    def cleanup_repository(self, repo_id: str) -> bool:
        """
        Clean up a cloned repository
        
        Args:
            repo_id: Repository ID to clean up
            
        Returns:
            True if successful
        """
        return self.cloner.cleanup_repository(repo_id)
    
    def get_repository_path(self, repo_id: str) -> Path:
        """
        Get the local path of a cloned repository
        
        Args:
            repo_id: Repository ID
            
        Returns:
            Path to repository
        """
        return self.cloner.get_clone_path(repo_id)


# Made with Bob