import sys

from PyQt6.QtWidgets import QApplication

from src.core import logging
from src.core.config.registry import ConfigRegistry
from src.ui.dashboard import Dashboard


def main():
    # Setup logging
    logger = logging.setup_logger(__name__)
    logger.info("Initializing dashboard demo")
    
    # Create config registry
    registry = ConfigRegistry()
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Sign Language Translator")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SLT Team")
    
    try:
        # Create and show dashboard
        dashboard = Dashboard(logger, registry)
        dashboard.show()
        
        logger.info("Dashboard launched successfully")
        
        # Run the application
        exit_code = app.exec()
        
        logger.info(f"Application exited with code: {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.error(f"Error running dashboard: {e}")
        return 1


    
if __name__ == "__main__":
    main()
