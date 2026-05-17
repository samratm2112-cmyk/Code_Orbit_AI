"""
Quick test script to verify frontend can connect to backend
Run this before starting the Streamlit app
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests

def test_backend_connection():
    """Test backend connectivity"""
    backend_url = "http://localhost:8000"
    
    print("="*60)
    print("Testing Backend Connection")
    print("="*60)
    
    # Test 1: Health check
    print("\n1. Testing /health endpoint...")
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend is healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        print(f"   Make sure backend is running on {backend_url}")
        return False
    
    # Test 2: Root endpoint
    print("\n2. Testing / endpoint...")
    try:
        response = requests.get(f"{backend_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Root endpoint working")
            print(f"   Message: {data.get('message')}")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Failed: {str(e)}")
    
    # Test 3: API docs
    print("\n3. Testing /docs endpoint...")
    try:
        response = requests.get(f"{backend_url}/docs", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ API docs available at {backend_url}/docs")
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Failed: {str(e)}")
    
    # Test 4: Chat list endpoint (for AI check)
    print("\n4. Testing /api/chat/list endpoint...")
    try:
        response = requests.get(f"{backend_url}/api/chat/list", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Chat API available (AI features ready)")
        else:
            print(f"   ⚠️  Status code: {response.status_code}")
            print(f"   AI features may not be available")
    except Exception as e:
        print(f"   ⚠️  AI check failed: {str(e)}")
        print(f"   This is OK if OpenAI API key is not configured")
    
    print("\n" + "="*60)
    print("✅ Backend connection test PASSED")
    print("="*60)
    print("\nYou can now start the frontend:")
    print("  streamlit run frontend/app.py")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    success = test_backend_connection()
    sys.exit(0 if success else 1)

# Made with Bob
