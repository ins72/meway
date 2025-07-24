"""
Minimal production backend startup script
This ensures the backend starts correctly in container environments
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Setup production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("production_startup")

def main():
    """Production startup with error recovery"""
    logger.info("🚀 Starting Mewayz API in production mode...")
    
    try:
        # Set production environment variables
        os.environ.setdefault("PYTHONPATH", str(backend_dir))
        os.environ.setdefault("PYTHONUNBUFFERED", "1")
        
        # Import and run the application
        import uvicorn
        from main import app
        
        logger.info("✅ Application imported successfully")
        logger.info("🌐 Starting uvicorn server on 0.0.0.0:8001")
        
        # Run with production settings
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
            log_level="info",
            access_log=True,
            loop="asyncio"
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Received shutdown signal")
    except Exception as e:
        logger.error(f"❌ Production startup failed: {e}")
        import traceback
        logger.error(f"📊 Stack trace: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()