"""
Repository Statistics Analyzer
Generates comprehensive statistics about repository structure and content
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict

from shared.logger import logger
from backend.models.repository import RepositoryStatistics, FileMetadata


class RepositoryAnalyzer:
    """
    Analyzes repository structure and generates statistics
    
    Features:
    - Total file counts
    - Language distribution
    - Size analysis
    - Largest files identification
    - Complexity indicators
    """
    
    def __init__(self):
        """Initialize repository analyzer"""
        logger.info("RepositoryAnalyzer initialized")
    
    def analyze(
        self,
        files: List[FileMetadata],
        repo_path: Optional[Path] = None
    ) -> RepositoryStatistics:
        """
        Analyze repository and generate statistics
        
        Args:
            files: List of parsed file metadata
            repo_path: Optional path to repository for additional analysis
            
        Returns:
            RepositoryStatistics object
        """
        logger.info(f"Analyzing repository with {len(files)} files")
        
        # Calculate basic statistics
        total_files = len(files)
        total_source_files = self._count_source_files(files)
        total_lines = sum(f.line_count for f in files)
        total_size_bytes = sum(f.size_bytes for f in files)
        
        # Language distribution
        languages_distribution = self._calculate_language_distribution(files)
        
        # File type distribution
        file_type_distribution = self._calculate_file_type_distribution(files)
        
        # Largest files
        largest_files = self._find_largest_files(files, top_n=10)
        
        statistics = RepositoryStatistics(
            total_files=total_files,
            total_source_files=total_source_files,
            total_lines=total_lines,
            total_size_bytes=total_size_bytes,
            languages_distribution=languages_distribution,
            largest_files=largest_files,
            file_type_distribution=file_type_distribution
        )
        
        logger.info(f"Analysis complete: {total_files} files, {total_lines} lines, "
                   f"{total_size_bytes / 1024:.2f} KB")
        
        return statistics
    
    def _count_source_files(self, files: List[FileMetadata]) -> int:
        """Count source code files (excluding docs, configs, etc.)"""
        source_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx',
            '.java', '.go', '.rs', '.cpp', '.c', '.h',
            '.rb', '.php', '.swift', '.kt', '.scala'
        }
        
        return sum(1 for f in files if f.extension in source_extensions)
    
    def _calculate_language_distribution(
        self,
        files: List[FileMetadata]
    ) -> Dict[str, int]:
        """Calculate file count by programming language"""
        distribution = defaultdict(int)
        
        for file in files:
            if file.language:
                distribution[file.language] += 1
        
        # Sort by count (descending)
        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))
    
    def _calculate_file_type_distribution(
        self,
        files: List[FileMetadata]
    ) -> Dict[str, int]:
        """Calculate file count by extension"""
        distribution = defaultdict(int)
        
        for file in files:
            distribution[file.extension] += 1
        
        # Sort by count (descending)
        return dict(sorted(distribution.items(), key=lambda x: x[1], reverse=True))
    
    def _find_largest_files(
        self,
        files: List[FileMetadata],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """Find the largest files in the repository"""
        # Sort by size (descending)
        sorted_files = sorted(files, key=lambda x: x.size_bytes, reverse=True)
        
        largest = []
        for file in sorted_files[:top_n]:
            largest.append({
                'path': file.path,
                'size_bytes': file.size_bytes,
                'size_kb': round(file.size_bytes / 1024, 2),
                'lines': file.line_count,
                'language': file.language
            })
        
        return largest
    
    def calculate_complexity_score(
        self,
        statistics: RepositoryStatistics
    ) -> Dict[str, Any]:
        """
        Calculate repository complexity indicators
        
        Args:
            statistics: Repository statistics
            
        Returns:
            Dictionary with complexity metrics
        """
        # Average file size
        avg_file_size = (
            statistics.total_size_bytes / statistics.total_files
            if statistics.total_files > 0 else 0
        )
        
        # Average lines per file
        avg_lines_per_file = (
            statistics.total_lines / statistics.total_source_files
            if statistics.total_source_files > 0 else 0
        )
        
        # Language diversity (number of different languages)
        language_diversity = len(statistics.languages_distribution)
        
        # Complexity score (simple heuristic)
        # Higher score = more complex
        complexity_score = (
            (statistics.total_files / 100) * 0.3 +
            (statistics.total_lines / 10000) * 0.3 +
            (language_diversity / 5) * 0.2 +
            (avg_lines_per_file / 500) * 0.2
        )
        
        # Categorize complexity
        if complexity_score < 1:
            complexity_level = "Simple"
        elif complexity_score < 3:
            complexity_level = "Moderate"
        elif complexity_score < 5:
            complexity_level = "Complex"
        else:
            complexity_level = "Very Complex"
        
        return {
            'score': round(complexity_score, 2),
            'level': complexity_level,
            'avg_file_size_bytes': round(avg_file_size, 2),
            'avg_lines_per_file': round(avg_lines_per_file, 2),
            'language_diversity': language_diversity,
            'total_files': statistics.total_files,
            'total_lines': statistics.total_lines
        }
    
    def identify_important_files(
        self,
        files: List[FileMetadata],
        repo_path: Optional[Path] = None
    ) -> List[str]:
        """
        Identify important files in the repository
        
        Args:
            files: List of file metadata
            repo_path: Optional repository path
            
        Returns:
            List of important file paths
        """
        from shared.constants import IMPORTANT_FILES
        
        important = []
        
        for file in files:
            file_name = Path(file.path).name
            
            # Check against known important files
            if file_name in IMPORTANT_FILES:
                important.append(file.path)
                continue
            
            # Check for README files
            if file_name.upper().startswith('README'):
                important.append(file.path)
                continue
            
            # Check for LICENSE files
            if 'LICENSE' in file_name.upper():
                important.append(file.path)
                continue
            
            # Check for configuration files
            if file.extension in ['.json', '.yaml', '.yml', '.toml']:
                if any(keyword in file_name.lower() for keyword in 
                      ['config', 'package', 'setup', 'docker', 'requirements']):
                    important.append(file.path)
        
        logger.info(f"Identified {len(important)} important files")
        return important
    
    def identify_entry_points(
        self,
        files: List[FileMetadata]
    ) -> List[str]:
        """
        Identify potential entry point files
        
        Args:
            files: List of file metadata
            
        Returns:
            List of entry point file paths
        """
        from shared.constants import ENTRY_POINT_PATTERNS
        
        entry_points = []
        
        for file in files:
            file_name = Path(file.path).name
            
            # Check against known entry point patterns
            if file_name in ENTRY_POINT_PATTERNS:
                entry_points.append(file.path)
                continue
            
            # Check for common entry point names
            if file_name.lower() in ['__init__.py', '__main__.py', 'cli.py', 'run.py']:
                entry_points.append(file.path)
        
        logger.info(f"Identified {len(entry_points)} entry points")
        return entry_points
    
    def generate_summary_text(
        self,
        statistics: RepositoryStatistics,
        tech_stack: Optional[Any] = None
    ) -> str:
        """
        Generate a human-readable summary of the repository
        
        Args:
            statistics: Repository statistics
            tech_stack: Optional technology stack information
            
        Returns:
            Summary text
        """
        lines = [
            "Repository Analysis Summary",
            "=" * 50,
            "",
            f"Total Files: {statistics.total_files}",
            f"Source Files: {statistics.total_source_files}",
            f"Total Lines of Code: {statistics.total_lines:,}",
            f"Total Size: {statistics.total_size_bytes / 1024 / 1024:.2f} MB",
            "",
            "Language Distribution:",
        ]
        
        for lang, count in list(statistics.languages_distribution.items())[:5]:
            percentage = (count / statistics.total_files) * 100
            lines.append(f"  - {lang}: {count} files ({percentage:.1f}%)")
        
        if tech_stack:
            lines.extend([
                "",
                "Technology Stack:",
                f"  Languages: {', '.join(tech_stack.languages[:5])}",
                f"  Frameworks: {', '.join(tech_stack.frameworks[:5])}",
                f"  Tools: {', '.join(tech_stack.tools[:5])}",
            ])
        
        lines.extend([
            "",
            "Largest Files:",
        ])
        
        for file_info in statistics.largest_files[:5]:
            lines.append(f"  - {file_info['path']} ({file_info['size_kb']} KB)")
        
        return "\n".join(lines)


# Made with Bob