"""
Helper utilities for the frontend
"""

import streamlit as st
from typing import Dict, Any, List
import time


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    size_float = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_float < 1024.0:
            return f"{size_float:.2f} {unit}"
        size_float /= 1024.0
    return f"{size_float:.2f} TB"


def format_number(num: int) -> str:
    """Format number with commas"""
    return f"{num:,}"


def get_language_color(language: str) -> str:
    """Get color for programming language"""
    colors = {
        'Python': '#3776ab',
        'JavaScript': '#f7df1e',
        'TypeScript': '#3178c6',
        'Java': '#007396',
        'Go': '#00add8',
        'Rust': '#dea584',
        'C++': '#00599c',
        'C': '#555555',
        'Ruby': '#cc342d',
        'PHP': '#777bb4',
        'Swift': '#ffac45',
        'Kotlin': '#7f52ff',
        'HTML': '#e34c26',
        'CSS': '#563d7c',
        'Markdown': '#083fa1',
    }
    return colors.get(language, '#808080')


def show_success_message(message: str):
    """Show success message"""
    st.success(f"✅ {message}")


def show_error_message(message: str):
    """Show error message"""
    st.error(f"❌ {message}")


def show_info_message(message: str):
    """Show info message"""
    st.info(f"ℹ️ {message}")


def show_warning_message(message: str):
    """Show warning message"""
    st.warning(f"⚠️ {message}")


def create_metric_card(label: str, value: str, delta: str | None = None):
    """Create a metric card"""
    st.metric(label=label, value=value, delta=delta)


def show_loading_spinner(message: str = "Loading..."):
    """Show loading spinner"""
    return st.spinner(message)


def create_progress_bar(progress: float, text: str = ""):
    """Create progress bar"""
    st.progress(progress, text=text)


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def create_badge(text: str, color: str = "blue") -> str:
    """Create a colored badge"""
    colors = {
        'blue': '#1f77b4',
        'green': '#2ca02c',
        'red': '#d62728',
        'orange': '#ff7f0e',
        'purple': '#9467bd',
        'gray': '#7f7f7f'
    }
    bg_color = colors.get(color, colors['blue'])
    return f'<span style="background-color: {bg_color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">{text}</span>'


def render_markdown_with_code(text: str):
    """Render markdown with code highlighting"""
    st.markdown(text, unsafe_allow_html=True)


def create_expandable_section(title: str, content: str, expanded: bool = False):
    """Create expandable section"""
    with st.expander(title, expanded=expanded):
        st.write(content)


def show_json_data(data: Dict[str, Any], expanded: bool = False):
    """Show JSON data in expandable section"""
    with st.expander("📄 Raw Data", expanded=expanded):
        st.json(data)


def create_download_button(data: str, filename: str, label: str = "Download"):
    """Create download button"""
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime="text/plain"
    )


def get_sample_repositories() -> List[Dict[str, str]]:
    """Get list of sample repositories for demo"""
    return [
        {
            "name": "Flask",
            "url": "https://github.com/pallets/flask",
            "description": "Python web framework",
            "branch": "main"
        },
        {
            "name": "FastAPI",
            "url": "https://github.com/fastapi/fastapi",
            "description": "Modern Python web framework",
            "branch": "master"
        },
        {
            "name": "Streamlit",
            "url": "https://github.com/streamlit/streamlit",
            "description": "Python app framework",
            "branch": "develop"
        },
        {
            "name": "Scikit-learn",
            "url": "https://github.com/scikit-learn/scikit-learn",
            "description": "Machine learning library",
            "branch": "main"
        }
    ]


def get_example_questions() -> List[str]:
    """Get example questions for demo"""
    return [
        "What is the main purpose of this repository?",
        "Where is authentication implemented?",
        "How is routing handled?",
        "What testing framework is used?",
        "How are environment variables loaded?",
        "Which files handle database connections?",
        "Explain the API flow",
        "What is the project structure?",
        "How is error handling implemented?",
        "Where are the main entry points?"
    ]


def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'current_repo' not in st.session_state:
        st.session_state.current_repo = None
    
    if 'analysis_data' not in st.session_state:
        st.session_state.analysis_data = None
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'embeddings_ready' not in st.session_state:
        st.session_state.embeddings_ready = False
    
    if 'repo_id' not in st.session_state:
        st.session_state.repo_id = None
    
    if 'insights_data' not in st.session_state:
        st.session_state.insights_data = None
    
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    
    if 'selected_file' not in st.session_state:
        st.session_state.selected_file = None
    
    if 'semantic_search_query' not in st.session_state:
        st.session_state.semantic_search_query = ''


def clear_session_state():
    """Clear session state"""
    st.session_state.current_repo = None
    st.session_state.analysis_data = None
    st.session_state.chat_history = []
    st.session_state.embeddings_ready = False
    st.session_state.repo_id = None


def add_custom_css():
    """Add custom CSS styling"""
    st.markdown("""
    <style>
    /* Main container */
    .main {
        padding: 2rem;
    }
    
    /* Cards */
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    /* Chat messages */
    .user-message {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #2196f3;
    }
    
    .ai-message {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4caf50;
    }
    
    /* Source references */
    .source-ref {
        background-color: #fff3e0;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
        font-size: 0.9rem;
        border-left: 3px solid #ff9800;
    }
    
    /* Technology badges */
    .tech-badge {
        display: inline-block;
        background-color: #e0e0e0;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        margin: 0.25rem;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* Headers */
    h1 {
        color: #1f77b4;
        font-weight: 700;
    }
    
    h2 {
        color: #2c3e50;
        font-weight: 600;
        margin-top: 2rem;
    }
    
    h3 {
        color: #34495e;
        font-weight: 500;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        font-weight: 500;
    }
    
    /* Sidebar */
    .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Code blocks */
    code {
        background-color: #f5f5f5;
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
        font-size: 0.9rem;
    }
    
    /* Links */
    a {
        color: #1f77b4;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)


# Made with Bob