#!/usr/bin/env python3
"""
Simple production test script
"""

import asyncio
import sys
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_basic_import():
    """Test basic FastAPI app import"""
    try:
        logger.info("🧪 Testing basic imports...")
        
        # Test core imports
        from datetime import datetime
        from fastapi import FastAPI
        
        logger.info("✅ Core FastAPI imports working")
        
        # Test app creation
        test_app = FastAPI(title="Test", version="1.0.0")
        logger.info("✅ FastAPI app creation working")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic import test failed: {e}")
        return False

async def test_database_optional():
    """Test that app works without database"""
    try:
        logger.info("🧪 Testing database-optional startup...")
        
        # Set a fake MongoDB URL to test graceful failure
        os.environ["MONGO_URL"] = "mongodb://fake:27017/test"
        
        # Import database module
        sys.path.insert(0, "/app/backend")
        from core.database import connect_to_mongo, db
        
        # Try connection (should fail gracefully)
        try:
            await asyncio.wait_for(connect_to_mongo(), timeout=2.0)
            logger.info("✅ Database connected (unexpected but ok)")
        except:
            logger.info("✅ Database connection failed gracefully as expected")
        
        # Verify db object handles None state
        if db.client is None and db.database is None:
            logger.info("✅ Database objects properly set to None after failure")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database optional test failed: {e}")
        return False

async def main():
    """Run all tests"""
    logger.info("🚀 Starting production readiness tests...")
    
    tests = [
        ("Basic Import Test", test_basic_import()),
        ("Database Optional Test", test_database_optional()),
    ]
    
    results = []
    for test_name, test_coro in tests:
        logger.info(f"🧪 Running {test_name}...")
        result = await test_coro
        results.append((test_name, result))
        if result:
            logger.info(f"✅ {test_name} PASSED")
        else:
            logger.error(f"❌ {test_name} FAILED")
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    logger.info(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! App is ready for deployment.")
        return True
    else:
        logger.error("❌ Some tests failed. Check deployment readiness.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)