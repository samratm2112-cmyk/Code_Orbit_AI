"""
Test script to verify local AI functionality
Tests embeddings, semantic search, and chat without OpenAI
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_backend_health():
    """Test backend is running"""
    print("Testing backend health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("SUCCESS: Backend is healthy")
            return True
        else:
            print(f"FAIL: Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Backend not reachable: {e}")
        return False

def test_ai_health():
    """Test AI service health"""
    print("\nTesting AI service health...")
    try:
        response = requests.get(f"{BASE_URL}/api/chat/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: AI Status: {data.get('status')}")
            print(f"  Embeddings Available: {data.get('embeddings_available')}")
            print(f"  Chat Available: {data.get('chat_available')}")
            print(f"  Note: {data.get('note')}")
            return data.get('embeddings_available', False)
        else:
            print(f"FAIL: AI health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: AI health check error: {e}")
        return False

def test_repository_analysis():
    """Test repository analysis"""
    print("\nTesting repository analysis...")
    try:
        payload = {
            "url": "https://github.com/pallets/flask",
            "branch": "main",
            "include_content": True
        }
        print("  Analyzing Flask repository (this may take a minute)...")
        response = requests.post(
            f"{BASE_URL}/api/repository/analyze",
            json=payload,
            timeout=300
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                repo_data = data.get('data', {})
                metadata = repo_data.get('metadata', {})
                repo_id = metadata.get('repo_id')
                print(f"SUCCESS: Repository analyzed")
                print(f"  Repo ID: {repo_id}")
                print(f"  Name: {metadata.get('name')}")
                print(f"  Files: {repo_data.get('statistics', {}).get('total_files')}")
                return repo_id
            else:
                print(f"FAIL: Analysis failed: {data.get('message')}")
                return None
        else:
            print(f"FAIL: Analysis request failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"FAIL: Repository analysis error: {e}")
        return None

def test_embeddings_preparation(repo_id):
    """Test embeddings preparation"""
    print(f"\nTesting embeddings preparation for {repo_id}...")
    try:
        print("  Generating local embeddings (this may take 1-2 minutes)...")
        response = requests.post(
            f"{BASE_URL}/api/chat/prepare/{repo_id}",
            timeout=300
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                info = data.get('info', {})
                print(f"SUCCESS: Embeddings prepared")
                print(f"  Total Vectors: {info.get('total_vectors')}")
                print(f"  Dimension: {info.get('dimension')}")
                return True
            else:
                print(f"FAIL: Embeddings preparation failed: {data.get('message')}")
                return False
        else:
            error_data = response.json()
            print(f"FAIL: Embeddings request failed: {error_data.get('detail')}")
            return False
    except Exception as e:
        print(f"FAIL: Embeddings preparation error: {e}")
        return False

def test_semantic_search(repo_id):
    """Test semantic search"""
    print(f"\nTesting semantic search for {repo_id}...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/chat/search/{repo_id}",
            params={"query": "authentication", "k": 3},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                results = data.get('results', [])
                print(f"SUCCESS: Semantic search successful")
                print(f"  Found {len(results)} results")
                for i, result in enumerate(results[:2], 1):
                    print(f"  {i}. {result.get('file_path')} (relevance: {result.get('relevance_score'):.2f})")
                return True
            else:
                print(f"FAIL: Search failed: {data.get('message')}")
                return False
        else:
            print(f"FAIL: Search request failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Semantic search error: {e}")
        return False

def test_chat_query(repo_id):
    """Test chat query"""
    print(f"\nTesting chat query for {repo_id}...")
    try:
        payload = {
            "repo_id": repo_id,
            "question": "How is routing handled in this application?",
            "max_results": 3,
            "include_sources": True
        }
        response = requests.post(
            f"{BASE_URL}/api/chat/query",
            json=payload,
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                answer = data.get('answer', '')
                sources = data.get('sources', [])
                print(f"SUCCESS: Chat query successful")
                print(f"  Answer length: {len(answer)} characters")
                print(f"  Sources: {len(sources)}")
                print(f"  Processing time: {data.get('processing_time_ms'):.0f}ms")
                return True
            else:
                print(f"FAIL: Chat query failed")
                return False
        else:
            print(f"FAIL: Chat request failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Chat query error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("LOCAL AI FUNCTIONALITY TEST")
    print("=" * 60)
    
    # Test 1: Backend health
    if not test_backend_health():
        print("\nFAIL: Backend not running. Start it with:")
        print("  python -m uvicorn backend.main:app --reload --port 8000")
        return
    
    # Test 2: AI health
    if not test_ai_health():
        print("\nFAIL: AI service not available. Install dependencies:")
        print("  pip install sentence-transformers transformers torch")
        return
    
    # Test 3: Repository analysis
    repo_id = test_repository_analysis()
    if not repo_id:
        print("\nFAIL: Repository analysis failed")
        return
    
    # Test 4: Embeddings preparation
    if not test_embeddings_preparation(repo_id):
        print("\nFAIL: Embeddings preparation failed")
        return
    
    # Test 5: Semantic search
    if not test_semantic_search(repo_id):
        print("\nFAIL: Semantic search failed")
        return
    
    # Test 6: Chat query
    if not test_chat_query(repo_id):
        print("\nFAIL: Chat query failed")
        return
    
    print("\n" + "=" * 60)
    print("SUCCESS: ALL TESTS PASSED - LOCAL AI FULLY FUNCTIONAL")
    print("=" * 60)
    print("\nCodeOrbit AI is ready for demo!")
    print("  Frontend: http://localhost:8501")
    print("  Backend: http://localhost:8000/docs")

if __name__ == "__main__":
    main()

# Made with Bob
