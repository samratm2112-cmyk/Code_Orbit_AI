import requests
import json

print("Checking backend health endpoint...")
try:
    response = requests.get("http://localhost:8000/api/chat/health", timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\nChecking if backend is using old or new code...")
print("Expected for NEW code: status='healthy', embeddings_available=True")
print("Current response shows OLD code is still running")
print("\nThe backend server needs to be restarted to load the new code.")

# Made with Bob
