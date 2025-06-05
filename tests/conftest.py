import sys
import os
import shutil
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def pytest_sessionfinish(session, exitstatus):
    """
    Clean up test data and logs after test session completes
    """
    # Define paths to clean
    test_data_dir = project_root / "tests" / "data"
    test_logs_dir = project_root / "tests" / "logs"

    # Clean test data directory
    if test_data_dir.exists():
        for item in test_data_dir.iterdir():
            if item.is_file():
                os.remove(item)
            elif item.is_dir():
                shutil.rmtree(item)
        print(f"Cleaned test data directory: {test_data_dir}")

    # Clean test logs directory
    if test_logs_dir.exists():
        for item in test_logs_dir.iterdir():
            if item.is_file():
                os.remove(item)
            elif item.is_dir():
                shutil.rmtree(item)
        print(f"Cleaned test logs directory: {test_logs_dir}")