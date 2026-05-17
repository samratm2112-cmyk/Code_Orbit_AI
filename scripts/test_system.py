"""
System validation script for CodeOrbit AI
Tests all components to ensure demo readiness
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests
import time
from typing import Dict, Any


class SystemValidator:
    """Validate all system components"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.results = []
        
    def log(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })
        print(f"{status} - {test_name}")
        if message:
            print(f"    {message}")
    
    def test_backend_health(self) -> bool:
        """Test backend is running"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            passed = response.status_code == 200
            self.log("Backend Health Check", passed, 
                    f"Status: {response.status_code}")
            return passed
        except Exception as e:
            self.log("Backend Health Check", False, str(e))
            return False
    
    def test_backend_ai_status(self) -> bool:
        """Test AI features availability"""
        try:
            response = requests.get(f"{self.backend_url}/health/ai", timeout=5)
            data = response.json()
            passed = data.get('ai_available', False)
            self.log("AI Features Check", passed,
                    f"OpenAI: {'Available' if passed else 'Not configured'}")
            return passed
        except Exception as e:
            self.log("AI Features Check", False, str(e))
            return False
    
    def test_repository_analysis(self) -> bool:
        """Test repository analysis endpoint"""
        try:
            # Use a small test repository
            payload = {
                "repo_url": "https://github.com/pallets/click",
                "branch": "main",
                "include_content": False
            }
            
            print("    Analyzing test repository (this may take 20-30 seconds)...")
            response = requests.post(
                f"{self.backend_url}/api/repository/analyze",
                json=payload,
                timeout=60
            )
            
            passed = response.status_code == 200
            if passed:
                data = response.json()
                success = data.get('success', False)
                passed = success
                
            self.log("Repository Analysis", passed,
                    f"Status: {response.status_code}")
            return passed
        except Exception as e:
            self.log("Repository Analysis", False, str(e))
            return False
    
    def test_file_structure(self) -> bool:
        """Test critical files exist"""
        critical_files = [
            "backend/main.py",
            "backend/api/repository.py",
            "backend/api/chat.py",
            "backend/core/repo_parser.py",
            "backend/ai/chat_service.py",
            "frontend/app.py",
            "frontend/services/api.py",
            "shared/config.py",
            "requirements.txt",
            ".env.example"
        ]
        
        missing = []
        for file_path in critical_files:
            full_path = project_root / file_path
            if not full_path.exists():
                missing.append(file_path)
        
        passed = len(missing) == 0
        message = f"All files present" if passed else f"Missing: {', '.join(missing)}"
        self.log("File Structure Check", passed, message)
        return passed
    
    def test_dependencies(self) -> bool:
        """Test critical dependencies are installed"""
        critical_imports = [
            ('fastapi', 'FastAPI'),
            ('uvicorn', 'Uvicorn'),
            ('streamlit', 'Streamlit'),
            ('openai', 'OpenAI'),
            ('langchain', 'LangChain'),
            ('faiss', 'FAISS'),
            ('git', 'GitPython'),
            ('plotly', 'Plotly')
        ]
        
        missing = []
        for module, name in critical_imports:
            try:
                __import__(module)
            except ImportError:
                missing.append(name)
        
        passed = len(missing) == 0
        message = f"All dependencies installed" if passed else f"Missing: {', '.join(missing)}"
        self.log("Dependencies Check", passed, message)
        return passed
    
    def test_environment(self) -> bool:
        """Test environment configuration"""
        env_file = project_root / ".env"
        
        if not env_file.exists():
            self.log("Environment Check", False, ".env file not found")
            return False
        
        # Check for OpenAI key
        with open(env_file) as f:
            content = f.read()
            has_openai = "OPENAI_API_KEY" in content
        
        self.log("Environment Check", True,
                f"OpenAI key: {'Configured' if has_openai else 'Not set (AI features disabled)'}")
        return True
    
    def test_data_directories(self) -> bool:
        """Test data directories exist"""
        directories = [
            "data/repositories",
            "data/vector_stores",
            "data/cache"
        ]
        
        missing = []
        for dir_path in directories:
            full_path = project_root / dir_path
            if not full_path.exists():
                missing.append(dir_path)
        
        passed = len(missing) == 0
        message = f"All directories present" if passed else f"Missing: {', '.join(missing)}"
        self.log("Data Directories Check", passed, message)
        return passed
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print("\n⚠️  FAILED TESTS:")
            for result in self.results:
                if not result['passed']:
                    print(f"  - {result['test']}")
                    if result['message']:
                        print(f"    {result['message']}")
        
        print("\n" + "="*60)
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED - SYSTEM IS DEMO READY!")
        else:
            print("⚠️  SOME TESTS FAILED - PLEASE FIX BEFORE DEMO")
        
        print("="*60 + "\n")
        
        return failed == 0


def main():
    """Run all validation tests"""
    print("="*60)
    print("CodeOrbit AI - System Validation")
    print("="*60 + "\n")
    
    validator = SystemValidator()
    
    print("Running validation tests...\n")
    
    # Run all tests
    validator.test_file_structure()
    validator.test_dependencies()
    validator.test_environment()
    validator.test_data_directories()
    validator.test_backend_health()
    validator.test_backend_ai_status()
    
    # Optional: Test repository analysis (takes time)
    print("\n⚠️  Repository analysis test takes 20-30 seconds.")
    response = input("Run repository analysis test? (y/n): ")
    if response.lower() == 'y':
        validator.test_repository_analysis()
    
    # Print summary
    all_passed = validator.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

# Made with Bob
