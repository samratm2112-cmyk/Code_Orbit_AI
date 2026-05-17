"""Direct test of embeddings service"""
import sys
sys.path.append('.')

from backend.ai.embeddings import embeddings_service

print("Testing embeddings service directly...")
print(f"Is available: {embeddings_service.is_available()}")

if embeddings_service.is_available():
    print("SUCCESS: Embeddings service is available!")
    try:
        model = embeddings_service._load_local_model()
        print(f"Model loaded: {model}")
        print(f"Dimension: {embeddings_service.dimension}")
    except Exception as e:
        print(f"Error loading model: {e}")
else:
    print("FAIL: Embeddings service not available")

# Made with Bob
