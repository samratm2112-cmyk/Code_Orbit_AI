"""
Test script for repository ingestion pipeline
Tests the complete flow from cloning to analysis
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.repo_parser import RepositoryParser
from shared.logger import logger


async def test_small_repository():
    """Test with a small repository"""
    logger.info("=" * 60)
    logger.info("TEST 1: Small Repository (Flask)")
    logger.info("=" * 60)
    
    parser = RepositoryParser()
    
    try:
        # Test with Flask repository (small and well-structured)
        url = "https://github.com/pallets/flask"
        
        logger.info(f"Analyzing: {url}")
        analysis = await parser.parse_repository(url, branch="main", include_content=False)
        
        # Print results
        logger.info("\n" + "=" * 60)
        logger.info("ANALYSIS RESULTS")
        logger.info("=" * 60)
        
        logger.info(f"\nRepository: {analysis.metadata.name}")
        logger.info(f"Owner: {analysis.metadata.owner}")
        logger.info(f"Repo ID: {analysis.metadata.repo_id}")
        logger.info(f"Status: {analysis.metadata.status}")
        
        logger.info(f"\nStatistics:")
        logger.info(f"  Total Files: {analysis.statistics.total_files}")
        logger.info(f"  Source Files: {analysis.statistics.total_source_files}")
        logger.info(f"  Total Lines: {analysis.statistics.total_lines:,}")
        logger.info(f"  Size: {analysis.statistics.total_size_bytes / 1024 / 1024:.2f} MB")
        
        logger.info(f"\nLanguages:")
        for lang, count in list(analysis.statistics.languages_distribution.items())[:5]:
            logger.info(f"  - {lang}: {count} files")
        
        logger.info(f"\nTechnology Stack:")
        logger.info(f"  Languages: {', '.join(analysis.technology_stack.languages)}")
        logger.info(f"  Frameworks: {', '.join(analysis.technology_stack.frameworks)}")
        logger.info(f"  Tools: {', '.join(analysis.technology_stack.tools)}")
        
        logger.info(f"\nImportant Files ({len(analysis.important_files)}):")
        for file in analysis.important_files[:10]:
            logger.info(f"  - {file}")
        
        logger.info(f"\nEntry Points ({len(analysis.entry_points)}):")
        for entry in analysis.entry_points[:5]:
            logger.info(f"  - {entry}")
        
        logger.info(f"\nFolder Structure (preview):")
        logger.info(analysis.folder_structure[:500] + "...")
        
        logger.success("\n✅ Test 1 PASSED: Small repository analysis successful")
        
        # Cleanup
        parser.cleanup_repository(analysis.metadata.repo_id)
        logger.info("Cleaned up repository")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Test 1 FAILED: {str(e)}")
        return False


async def test_medium_repository():
    """Test with a medium-sized repository"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Medium Repository (FastAPI)")
    logger.info("=" * 60)
    
    parser = RepositoryParser()
    
    try:
        url = "https://github.com/fastapi/fastapi"
        
        logger.info(f"Analyzing: {url}")
        analysis = await parser.parse_repository(url, branch="master", include_content=False)
        
        logger.info(f"\nRepository: {analysis.metadata.name}")
        logger.info(f"Total Files: {analysis.statistics.total_files}")
        logger.info(f"Languages: {', '.join(list(analysis.statistics.languages_distribution.keys())[:3])}")
        logger.info(f"Frameworks: {', '.join(analysis.technology_stack.frameworks[:3])}")
        
        logger.success("\n✅ Test 2 PASSED: Medium repository analysis successful")
        
        # Cleanup
        parser.cleanup_repository(analysis.metadata.repo_id)
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Test 2 FAILED: {str(e)}")
        return False


async def test_with_content():
    """Test with file content extraction"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Repository with Content Extraction")
    logger.info("=" * 60)
    
    parser = RepositoryParser()
    
    try:
        # Use a very small repo for content extraction
        url = "https://github.com/pallets/click"
        
        logger.info(f"Analyzing: {url}")
        analysis = await parser.parse_repository(url, branch="main", include_content=True)
        
        logger.info(f"\nRepository: {analysis.metadata.name}")
        logger.info(f"Files with content: {len([f for f in analysis.files if f.content])}")
        
        # Test embedding preparation
        documents = parser.prepare_for_embeddings(analysis, max_files=50)
        logger.info(f"Documents prepared for embeddings: {len(documents)}")
        
        logger.success("\n✅ Test 3 PASSED: Content extraction successful")
        
        # Cleanup
        parser.cleanup_repository(analysis.metadata.repo_id)
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Test 3 FAILED: {str(e)}")
        return False


async def test_error_handling():
    """Test error handling"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Error Handling")
    logger.info("=" * 60)
    
    parser = RepositoryParser()
    
    # Test invalid URL
    try:
        logger.info("Testing invalid URL...")
        await parser.parse_repository("https://invalid-url.com/repo", branch="main")
        logger.error("❌ Should have raised an error for invalid URL")
        return False
    except Exception as e:
        logger.info(f"✓ Correctly caught error: {str(e)[:100]}")
    
    # Test non-existent repository
    try:
        logger.info("\nTesting non-existent repository...")
        await parser.parse_repository("https://github.com/nonexistent/repository12345", branch="main")
        logger.error("❌ Should have raised an error for non-existent repo")
        return False
    except Exception as e:
        logger.info(f"✓ Correctly caught error: {str(e)[:100]}")
    
    logger.success("\n✅ Test 4 PASSED: Error handling works correctly")
    return True


async def run_all_tests():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("REPOSITORY INGESTION PIPELINE - TEST SUITE")
    logger.info("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Small Repository", await test_small_repository()))
    results.append(("Medium Repository", await test_medium_repository()))
    results.append(("Content Extraction", await test_with_content()))
    results.append(("Error Handling", await test_error_handling()))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.success("\n🎉 ALL TESTS PASSED!")
    else:
        logger.error(f"\n⚠️  {total - passed} test(s) failed")
    
    return passed == total


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

# Made with Bob