"""
CodeOrbit AI - Streamlit Frontend
Main application entry point
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
import time

# Import services and utilities
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from frontend.services.api import get_api_client
from frontend.utils.helpers import (
    format_file_size,
    format_number,
    get_language_color,
    show_success_message,
    show_error_message,
    show_info_message,
    show_warning_message,
    create_badge,
    get_sample_repositories,
    get_example_questions,
    initialize_session_state,
    clear_session_state,
    add_custom_css
)

# Page configuration
st.set_page_config(
    page_title="CodeOrbit AI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize
initialize_session_state()
add_custom_css()
api = get_api_client()


def render_sidebar():
    """Render sidebar with navigation and info"""
    with st.sidebar:
        st.markdown(
            """
            <div style='display:flex;align-items:center;gap:0.75rem;'>
                <div style='font-size:2rem;'>📘</div>
                <div>
                    <div style='font-size:1.25rem;font-weight:700;margin-bottom:0.2rem;'>Repo Intelligence</div>
                    <div style='font-size:0.9rem;color:#6c757d;margin:0;'>Developer repository insights</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("### AI-Powered Repository Intelligence")
        st.markdown("---")
        
        # Backend status
        st.markdown("#### System Status")
        
        if api.is_backend_available():
            st.success("✅ Backend Online")
        else:
            st.error("❌ Backend Offline")
            st.stop()

        if hasattr(api, "get_ai_status"):
            ai_status = api.get_ai_status()
        else:
            ai_status = {
                "status": "unavailable",
                "chat_available": False,
                "note": "AI status unavailable."
            }

        chat_ready = ai_status.get("chat_available", False)

        if chat_ready:
            st.success("✅ Groq Connected")
            st.caption("AI chat features active")
        else:
            st.warning("⚠️ Groq Not Configured")
            st.caption("Set GROQ_API_KEY in .env file")
        
        st.markdown("---")
        
        # Current repository
        if st.session_state.repo_id:
            st.markdown("#### Current Repository")
            st.info(f"📦 {st.session_state.current_repo}")
            
            if st.button("🗑️ Clear Repository"):
                clear_session_state()
                st.rerun()
        
        st.markdown("---")
        
        # Sample repositories
        st.markdown("#### 📚 Sample Repositories")
        samples = get_sample_repositories()
        
        for sample in samples[:3]:
            if st.button(f"📦 {sample['name']}", key=f"sample_{sample['name']}"):
                st.session_state.sample_url = sample['url']
                st.session_state.sample_branch = sample['branch']
                st.rerun()
        
        st.markdown("---")
        st.caption("Made with ❤️ by Bob")


def render_repository_input():
    """Render repository input section"""
    st.markdown("## 🔍 Analyze GitHub Repository")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Check if sample was selected
        default_url = st.session_state.get('sample_url', '')
        repo_url = st.text_input(
            "GitHub Repository URL",
            value=default_url,
            placeholder="https://github.com/owner/repository",
            help="Enter a public GitHub repository URL"
        )
    
    with col2:
        default_branch = st.session_state.get('sample_branch', 'main')
        branch = st.text_input(
            "Branch",
            value=default_branch,
            placeholder="main, master, dev",
            help="Branch to analyze"
        )
        st.caption("Default branch is usually main")
    
    col1, col2, col3 = st.columns([2, 1.8, 1.2])
    
    with col1:
        analyze_button = st.button("Analyze Repository", type="primary", use_container_width=True)
    
    with col2:
        include_content = st.checkbox("Include file content (for AI)", value=True)
    
    if analyze_button and repo_url:
        branch = branch.strip() or "main"
        with st.spinner("🔄 Analyzing repository... This may take a minute."):
            try:
                result = api.analyze_repository(repo_url, branch, include_content)
                
                if result.get('success'):
                    data = result.get('data', {})
                    metadata = data.get('metadata', {})
                    
                    st.session_state.repo_id = metadata.get('repo_id')
                    st.session_state.current_repo = metadata.get('name')
                    st.session_state.analysis_data = data
                    st.session_state.ai_ready = False
                    st.session_state.insights_data = None
                    st.session_state.selected_file = None
                    
                    # Clear sample selections after successful analysis
                    if 'sample_url' in st.session_state:
                        del st.session_state.sample_url
                    if 'sample_branch' in st.session_state:
                        del st.session_state.sample_branch
                    
                    show_success_message(f"Repository '{metadata.get('name')}' analyzed successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    show_error_message("Analysis failed. Please check the URL and try again.")
                    if 'sample_url' in st.session_state:
                        del st.session_state.sample_url
                    if 'sample_branch' in st.session_state:
                        del st.session_state.sample_branch
            
            except Exception as e:
                show_error_message(f"Error: {str(e)}")
                if 'sample_url' in st.session_state:
                    del st.session_state.sample_url
                if 'sample_branch' in st.session_state:
                    del st.session_state.sample_branch


def render_repository_overview():
    """Render repository overview section"""
    if not st.session_state.analysis_data:
        return
    
    data = st.session_state.analysis_data
    metadata = data.get('metadata', {})
    statistics = data.get('statistics', {})
    tech_stack = data.get('technology_stack', {})
    
    st.markdown("## 📊 Repository Overview")
    
    # Header with repo info
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### 📦 {metadata.get('name', 'Unknown')}")
        st.caption(f"Owner: {metadata.get('owner', 'Unknown')} | Branch: {metadata.get('branch', 'main')}")
    
    with col2:
        st.markdown(f"**Status:** {metadata.get('status', 'unknown').upper()}")
    
    with col3:
        if st.button("🔄 Refresh Analysis"):
            st.rerun()
    
    st.markdown("---")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📁 Total Files",
            value=format_number(statistics.get('total_files', 0))
        )
    
    with col2:
        st.metric(
            label="💻 Source Files",
            value=format_number(statistics.get('total_source_files', 0))
        )
    
    with col3:
        st.metric(
            label="📝 Lines of Code",
            value=format_number(statistics.get('total_lines', 0))
        )
    
    with col4:
        size_mb = statistics.get('total_size_bytes', 0) / (1024 * 1024)
        st.metric(
            label="💾 Repository Size",
            value=f"{size_mb:.2f} MB"
        )
    
    st.markdown("---")
    
    # Technology stack and languages
    col1, col2 = st.columns(2)
    
    with col1:
        render_technology_stack(tech_stack)
    
    with col2:
        render_language_distribution(statistics)


def render_technology_stack(tech_stack: Dict[str, Any]):
    """Render technology stack section"""
    st.markdown("### 🛠️ Technology Stack")
    
    languages = tech_stack.get('languages', [])
    frameworks = tech_stack.get('frameworks', [])
    tools = tech_stack.get('tools', [])
    
    if languages:
        st.markdown("**Languages:**")
        lang_html = " ".join([create_badge(lang, 'blue') for lang in languages[:8]])
        st.markdown(lang_html, unsafe_allow_html=True)
    
    if frameworks:
        st.markdown("**Frameworks:**")
        fw_html = " ".join([create_badge(fw, 'green') for fw in frameworks[:8]])
        st.markdown(fw_html, unsafe_allow_html=True)
    
    if tools:
        st.markdown("**Tools:**")
        tool_html = " ".join([create_badge(tool, 'orange') for tool in tools[:8]])
        st.markdown(tool_html, unsafe_allow_html=True)


def render_language_distribution(statistics: Dict[str, Any]):
    """Render language distribution chart"""
    st.markdown("### 📊 Language Distribution")
    
    lang_dist = statistics.get('languages_distribution', {})
    
    if lang_dist:
        # Create pie chart
        fig = px.pie(
            values=list(lang_dist.values()),
            names=list(lang_dist.keys()),
            title="Files by Language",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No language data available")


def get_file_icon(filename: str, language: Optional[str] = None) -> str:
    """Get icon for file type"""
    ext = filename.split('.')[-1].lower() if '.' in filename else ''
    
    icons = {
        'py': '🐍', 'js': '📜', 'ts': '📘', 'jsx': '⚛️', 'tsx': '⚛️',
        'java': '☕', 'go': '🔷', 'rs': '🦀', 'cpp': '⚙️', 'c': '⚙️',
        'html': '🌐', 'css': '🎨', 'md': '📝', 'json': '📋', 'yaml': '⚙️',
        'yml': '⚙️', 'xml': '📄', 'sql': '🗄️', 'sh': '🔧', 'dockerfile': '🐳',
        'txt': '📄', 'pdf': '📕', 'png': '🖼️', 'jpg': '🖼️', 'svg': '🎨'
    }
    
    return icons.get(ext, '📄')


def build_compact_tree(files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build a compact file tree structure"""
    tree = {}
    
    for file in files:
        path = file.get('path', '')
        if not path:
            continue
        
        parts = path.split('/')
        node = tree
        
        for i, part in enumerate(parts[:-1]):
            if part not in node:
                node[part] = {
                    'type': 'dir',
                    'children': {},
                    'file_count': 0
                }

            node[part]['file_count'] += 1
            node = node[part]['children']
        
        # Add file
        filename = parts[-1]
        node[filename] = {
            'type': 'file',
            'data': file,
            'path': path,
            'icon': get_file_icon(filename, file.get('language'))
        }
    
    return tree


def render_compact_explorer(node: Dict[str, Any], path: str = "", depth: int = 0, max_depth: int = 3):
    """Render modern compact file explorer"""
    if depth > max_depth:
        return
    
    # Sort: directories first, then files
    items = sorted(node.items(), key=lambda x: (x[1]['type'] != 'dir', x[0].lower()))
    
    for name, item in items:
        indent = "　" * depth  # Use full-width space for indentation
        
        if item['type'] == 'dir':
            # Directory
            file_count = item.get('file_count', 0)
            expander_label = f"{indent}📁 **{name}** `({file_count} files)`"
            
            # Streamlit does not support nested expanders
            # Only use expander for top-level directories
            if depth == 0:
                should_expand = file_count < 20
                with st.expander(expander_label, expanded=should_expand):
                    render_compact_explorer(item['children'], f"{path}{name}/", depth + 1, max_depth)
            else:
                st.markdown(expander_label)
                render_compact_explorer(item['children'], f"{path}{name}/", depth + 1, max_depth)
        else:
            # File
            icon = item.get('icon', '📄')
            file_data = item['data']
            file_path = item['path']
            
            # Create compact file button
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(
                    f"{indent}{icon} {name}",
                    key=f"file_btn_{file_path}",
                    use_container_width=True
                ):
                    st.session_state.selected_file = file_data
                    st.session_state.selected_file['path'] = file_path
                    st.rerun()
            
            with col2:
                # Show file size badge
                size = file_data.get('size_bytes', 0)
                if size > 0:
                    size_kb = size / 1024
                    if size_kb < 1:
                        st.caption(f"{size}B")
                    elif size_kb < 1024:
                        st.caption(f"{size_kb:.0f}KB")
                    else:
                        st.caption(f"{size_kb/1024:.1f}MB")


def render_folder_structure():
    """Render modern repository explorer"""
    if not st.session_state.analysis_data:
        return
    
    data = st.session_state.analysis_data
    files = data.get('files', [])
    important_files = data.get('important_files', [])
    entry_points = data.get('entry_points', [])
    
    st.markdown("## 📂 Repository Explorer")
    
    # Search/Filter bar
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_query = st.text_input(
            "🔍 Search files",
            placeholder="Filter by filename or extension...",
            key="file_search",
            label_visibility="collapsed"
        )
    with col2:
        show_all = st.checkbox("Show all", value=False, key="show_all_files")
    with col3:
        max_depth_value = st.selectbox("Depth", [1, 2, 3, 4, 5], index=2, key="tree_depth")
        max_depth = int(max_depth_value) if max_depth_value is not None else 3
    
    # Filter files based on search
    filtered_files = files
    if search_query:
        search_lower = search_query.lower()
        filtered_files = [
            f for f in files
            if search_lower in f.get('path', '').lower()
        ]
        st.caption(f"Found {len(filtered_files)} files matching '{search_query}'")
    
    # Main layout
    col1, col2 = st.columns([1.5, 2])
    
    with col1:
        st.markdown("### 🗂️ File Tree")
        
        # Quick access to important files
        if important_files and not search_query:
            with st.expander("⭐ Important Files", expanded=True):
                for file_path in important_files[:8]:
                    # Find the file in our files list
                    matching_file = next((f for f in files if f.get('path') == file_path), None)
                    if matching_file:
                        icon = get_file_icon(file_path.split('/')[-1])
                        if st.button(f"{icon} {file_path.split('/')[-1]}", key=f"imp_{file_path}", use_container_width=True):
                            st.session_state.selected_file = matching_file
                            st.session_state.selected_file['path'] = file_path
                            st.rerun()
        
        # Render file tree in scrollable container
        with st.container():
            if filtered_files:
                tree = build_compact_tree(filtered_files if show_all else filtered_files[:100])
                render_compact_explorer(tree, max_depth=max_depth)
                
                if not show_all and len(filtered_files) > 100:
                    st.info(f"Showing 100 of {len(filtered_files)} files. Enable 'Show all' to see more.")
            else:
                st.info("No files found matching your search.")
    
    with col2:
        st.markdown("### 📄 File Preview")
        
        selected = st.session_state.selected_file
        if selected:
            # File header
            file_path = selected.get('path', 'Unknown')
            filename = file_path.split('/')[-1]
            icon = get_file_icon(filename, selected.get('language'))
            
            st.markdown(f"#### {icon} {filename}")
            
            # File metadata in compact badges
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                lang = selected.get('language', 'Text')
                st.markdown(f"**Language:** `{lang}`")
            with col_b:
                lines = selected.get('line_count', 0)
                st.markdown(f"**Lines:** `{lines:,}`")
            with col_c:
                size = format_file_size(selected.get('size_bytes', 0))
                st.markdown(f"**Size:** `{size}`")
            
            st.caption(f"📍 Path: `{file_path}`")
            
            # Code preview with syntax highlighting
            content = selected.get('content', '')
            if content:
                # Show first 100 lines
                lines_to_show = content.split('\n')[:100]
                preview_content = '\n'.join(lines_to_show)
                
                st.code(preview_content, language=selected.get('language', '').lower())
                
                total_lines = len(content.split('\n'))
                if total_lines > 100:
                    st.caption(f"Showing first 100 lines of {total_lines} total lines")
            else:
                st.info("No content available for this file")
        else:
            # Show entry points when no file selected
            st.info("👈 Select a file from the tree to preview")
            
            if entry_points:
                st.markdown("#### 🚪 Entry Points")
                for entry in entry_points[:5]:
                    matching_file = next((f for f in files if f.get('path') == entry), None)
                    if matching_file:
                        icon = get_file_icon(entry.split('/')[-1])
                        if st.button(f"{icon} {entry}", key=f"entry_{entry}", use_container_width=True):
                            st.session_state.selected_file = matching_file
                            st.session_state.selected_file['path'] = entry
                            st.rerun()


def render_ai_insights():
    """Render AI-powered repository insights"""
    if not st.session_state.repo_id:
        return
    
    if st.session_state.insights_data is None:
        try:
            print(f"[Frontend] Fetching insights for repo_id: {st.session_state.repo_id}")
            result = api.get_repository_insights(st.session_state.repo_id)
            print(f"[Frontend] Insights response: {result.get('success')}")
            
            if result.get('success'):
                st.session_state.insights_data = result.get('data', {})
            else:
                st.session_state.insights_data = {}
                show_warning_message(f"Insights generation failed")
        except Exception as e:
            error_msg = str(e)
            print(f"[Frontend] Insights error: {error_msg}")
            show_warning_message(f"AI insights unavailable: {error_msg}")
            st.session_state.insights_data = {}
            
            # Show debug info
            with st.expander("🔍 Debug Info"):
                st.write(f"Repo ID: {st.session_state.repo_id}")
                st.write(f"Error: {error_msg}")
                try:
                    known = api.list_repositories()
                    backend_ids = [r.get('repo_id') for r in known.get('data', {}).get('repositories', [])]
                    if st.session_state.repo_id not in backend_ids:
                        st.error("⚠️ The backend server has forgotten this repository (likely due to a server restart). Please click **🗑️ Clear Repository** in the sidebar and re-analyze it.")
                except Exception:
                    pass
    
    insights = st.session_state.insights_data or {}
    if not insights:
        return
    
    st.markdown("## 🧠 AI Insights")
    st.info(insights.get('project_overview', 'Insight generation is ready.'))
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("**Architecture Summary**")
        st.write(insights.get('architecture_summary', 'No architecture details available.'))
        st.markdown("**Beginner Explanation**")
        st.write(insights.get('beginner_explanation', 'A short beginner-friendly explanation is not available.'))
    with col2:
        st.metric("Complexity", insights.get('complexity_estimate', 'Unknown'))
        st.markdown("**Key Modules**")
        key_modules = insights.get('key_modules', [])
        if key_modules:
            for module in key_modules:
                st.markdown(f"- `{module}`")
        st.markdown("**Tech Stack**")
        for label, items in insights.get('tech_stack', {}).items():
            if items:
                st.markdown(f"**{label.title()}:** {', '.join(items)}")
    
    if insights.get('folder_tree_preview'):
        with st.expander("Folder Structure Preview", expanded=False):
            st.code(insights.get('folder_tree_preview', ''), language="")


def render_ai_status():
    """Render AI status section"""
    if not st.session_state.repo_id:
        return
    
    st.markdown("## 🤖 AI Chat Features")
    
    # Check AI status
    try:
        ai_status = api.get_ai_status()
        chat_available = ai_status.get('chat_available', False)
        
        if chat_available:
            st.session_state.ai_ready = True
            show_success_message("✅ Groq API connected! You can now ask questions about the repository.")
        else:
            st.session_state.ai_ready = False
            show_warning_message("⚠️ Groq API not configured")
            st.info("""
            **To enable AI chat features:**
            1. Get an API key from https://console.groq.com/keys
            2. Create a `.env` file in the project root
            3. Add: `GROQ_API_KEY=your-api-key-here`
            4. Restart the backend server
            """)
    
    except Exception as e:
        st.session_state.ai_ready = False
        show_warning_message(f"Could not check AI status: {str(e)}")


def render_chat_interface():
    """Render AI chat interface"""
    if not st.session_state.ai_ready:
        return

    st.markdown("## 💬 Ask Your Repository")
    
    st.info("💡 Using Groq LLaMA 3 to answer questions about your repository")
    
    # Suggested questions
    with st.expander("💡 Suggested Questions", expanded=False):
        try:
            suggestions = api.get_suggested_questions(st.session_state.repo_id)
            questions = suggestions.get('suggestions', [])
            
            cols = st.columns(2)
            for idx, question in enumerate(questions[:6]):
                with cols[idx % 2]:
                    if st.button(f"💭 {question}", key=f"suggest_{idx}"):
                        # Auto-submit: store the question AND a flag to trigger chat
                        st.session_state.selected_question = question
                        st.session_state.auto_submit_question = True
                        st.rerun()
        except Exception as e:
            st.caption(f"Could not load suggestions: {str(e)}")
    
    # Chat input
    default_question = st.session_state.get('selected_question', '')
    auto_submit = st.session_state.pop('auto_submit_question', False)
    if 'selected_question' in st.session_state:
        del st.session_state.selected_question
    
    question = st.text_input(
        "Ask a question about the repository:",
        value=default_question,
        placeholder="e.g., Where is authentication implemented?",
        key="chat_input"
    )
    
    col1, col2 = st.columns([4, 1])
    with col1:
        ask_button = st.button("Ask Question", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear History"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Trigger query either from button click OR from suggested question auto-submit
    should_ask = (ask_button or auto_submit) and bool(question)

    if should_ask:
        # Validate repo_id exists
        if not st.session_state.repo_id:
            show_error_message("No repository analyzed. Please analyze a repository first.")
        else:
            with st.spinner("🤔 Thinking..."):
                try:
                    # Debug logging
                    print(f"[Frontend] Sending query with repo_id: {st.session_state.repo_id}")
                    print(f"[Frontend] Question: {question}")

                    response = api.query_repository(
                        st.session_state.repo_id,
                        question,
                        max_results=5,
                        include_sources=True
                    )

                    print(f"[Frontend] Response received: {response.get('success')}")

                    if response.get('success'):
                        # Add to history
                        st.session_state.chat_history.append({
                            'question': question,
                            'answer': response.get('answer'),
                            'sources': response.get('sources', []),
                            'time': response.get('processing_time_ms', 0)
                        })
                        show_success_message("Answer generated successfully!")
                        st.rerun()
                    else:
                        show_error_message(f"Query failed: {response.get('error', 'Unknown error')}")

                except Exception as e:
                    error_msg = str(e)
                    print(f"[Frontend] Error: {error_msg}")
                    show_error_message(f"Chat Error: {error_msg}")

                    # Show detailed error for debugging
                    with st.expander("🔍 Error Details"):
                        st.code(error_msg)
                        st.write(f"Repo ID used by frontend: `{st.session_state.repo_id}`")
                        st.write(f"Question: {question}")
                        # Show what the backend cache actually contains
                        try:
                            known = api.list_repositories()
                            backend_ids = [
                                r.get('repo_id')
                                for r in known.get('data', {}).get('repositories', [])
                            ]
                            st.write(f"Backend cache contains: {backend_ids}")
                            
                            # Auto-detect if backend was restarted and cache is empty
                            if st.session_state.repo_id not in backend_ids:
                                st.error("⚠️ The backend server has forgotten this repository (likely due to a server restart). Please click **🗑️ Clear Repository** in the sidebar and re-analyze it.")
                        except Exception as cache_err:
                            st.write(f"Could not fetch backend cache: {cache_err}")
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 📜 Conversation History")
        
        for idx, chat in enumerate(reversed(st.session_state.chat_history)):
            st.markdown(
                f"<div class='user-message'><strong>🙋 You:</strong><br>{chat['question']}</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div class='ai-message'><strong>🤖 AI:</strong><br>{chat['answer']}</div>",
                unsafe_allow_html=True
            )
            
            if chat.get('sources'):
                with st.expander(f"📚 Sources ({len(chat['sources'])})", expanded=False):
                    for source in chat['sources']:
                        st.markdown(
                            f"<div class='source-ref'><strong>File:</strong> `{source['file_path']}`<br>"
                            f"<strong>Lines:</strong> {source['start_line']}-{source['end_line']}<br>"
                            f"<strong>Relevance:</strong> {source['relevance_score']:.2%}<br>"
                            f"<strong>Preview:</strong> {source.get('content_preview', '')[:180]}..."
                            "</div>",
                            unsafe_allow_html=True
                        )
            
            st.caption(f"⏱️ Response time: {chat['time']:.0f}ms")
            st.markdown("---")


def main():
    """Main application"""
    # Render sidebar
    render_sidebar()
    
    # Main content
    st.title("🚀 CodeOrbit AI")
    st.markdown("### Understand any GitHub repository in minutes with AI")
    
    # Repository input
    render_repository_input()
    
    # Show analysis if available
    if st.session_state.analysis_data:
        render_repository_overview()
        render_folder_structure()
        render_ai_insights()
        render_ai_status()
        render_chat_interface()
    else:
        # Welcome message
        st.markdown("---")
        st.markdown("## 👋 Welcome!")
        st.markdown("""
        **Repo Intelligence** helps you understand any GitHub repository using advanced AI technology.
        
        ### 🎯 Features:
        - 📊 **Repository Analysis** - Get instant insights about any codebase
        - 🛠️ **Technology Detection** - Identify frameworks, languages, and tools
        - 📈 **Statistics & Metrics** - Understand repository complexity
        - 🤖 **AI-Powered Q&A** - Ask questions and get contextual answers
        - 📚 **Source Attribution** - See exactly where information comes from
        
        ### Get Started:
        1. Enter a GitHub repository URL above
        2. Click "Analyze Repository"
        3. Prepare AI features
        4. Start asking questions!
        
        Try one of the sample repositories from the sidebar to see it in action! 👈
        """)


if __name__ == "__main__":
    main()


# Made with Bob
