import loguru
from PyQt6.QtWidgets import QMainWindow

from src.core.config.registry import ConfigRegistry
from src.ui.dashboard import Dashboard


class MainWindow(QMainWindow):
    """Main application window - now delegates to Dashboard"""
    
    def __init__(self, logger: loguru.logger, config_registry: ConfigRegistry = None):
        super().__init__()
        self.logger = logger
        self.config_registry = config_registry

        # Create and show dashboard
        self.dashboard = Dashboard(logger, config_registry)
        self.setCentralWidget(self.dashboard.centralWidget())
        
        # Copy dashboard properties
        self.setWindowTitle(self.dashboard.windowTitle())
        self.setMinimumSize(self.dashboard.minimumSize())
        
        # Apply the same styling
        self.setStyleSheet(self.dashboard.styleSheet())
        
        # Copy status bar
        if self.dashboard.statusBar():
            self.setStatusBar(self.dashboard.statusBar())
            
        self.show()
        
    def closeEvent(self, event):
        """Handle close event"""
        if hasattr(self, 'dashboard'):
            self.dashboard.closeEvent(event)
        else:
            event.accept() 