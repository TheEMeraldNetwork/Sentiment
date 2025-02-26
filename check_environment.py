"""
Environment verification script to check all dependencies and API configurations.
"""

import sys
import importlib
import logging
from pathlib import Path

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def check_package(package_name: str, logger: logging.Logger) -> bool:
    """Check if a package is installed and can be imported"""
    try:
        importlib.import_module(package_name)
        logger.info(f"✓ {package_name} successfully imported")
        return True
    except ImportError as e:
        logger.error(f"✗ {package_name} import failed: {str(e)}")
        return False

def check_api_keys(logger: logging.Logger) -> bool:
    """Check if required API keys are configured"""
    sys.path.append(str(Path(__file__).parent))
    try:
        from utils.config.api_providers_config import FINNHUB_KEY
        if not FINNHUB_KEY:
            logger.error("✗ FINNHUB_KEY is not set in api_providers_config.py")
            return False
        logger.info("✓ API keys configured correctly")
        return True
    except ImportError:
        logger.error("✗ api_providers_config.py not found or FINNHUB_KEY not defined")
        return False
    except Exception as e:
        logger.error(f"✗ Error checking API keys: {str(e)}")
        return False

def check_directories(logger: logging.Logger) -> bool:
    """Check if required directories exist"""
    required_dirs = [
        'results',
        'results/archive',
        'results/archive/sentiment',
        'results/archive/market',
        'results/archive/predictions',
        'results/archive/posterior',
        'results/archive/master',
        'results/archive/reports',
        'logs'
    ]
    
    success = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        if path.exists():
            logger.info(f"✓ Directory exists: {dir_path}")
        else:
            logger.error(f"✗ Failed to create directory: {dir_path}")
            success = False
    return success

def main():
    """Run all environment checks"""
    logger = setup_logging()
    logger.info("Starting environment verification...")
    
    # Required packages to check
    packages = [
        'pandas',
        'numpy',
        'torch',
        'transformers',
        'scipy',
        'pymc',
        'aesara',
        'plotly',
        'yfinance',
        'finnhub',
    ]
    
    # Check each package
    packages_ok = all(check_package(pkg, logger) for pkg in packages)
    
    # Check API keys
    api_ok = check_api_keys(logger)
    
    # Check directories
    dirs_ok = check_directories(logger)
    
    # Final status
    if all([packages_ok, api_ok, dirs_ok]):
        logger.info("\nEnvironment verification successful! ✓")
        return True
    else:
        logger.error("\nEnvironment verification failed! ✗")
        logger.error("Please fix the above errors before running the workflow.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 