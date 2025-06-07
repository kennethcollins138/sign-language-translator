"""Main dashboard window for the sign language translator application."""

import loguru
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.core.config.registry import ConfigRegistry
from src.core.config.schema import CameraConfig, FrameProcessorConfig
from src.input.ingestion import CameraIngestion
from src.input.preprocessing import FramePreprocessor
from src.ui.components.camera_widget import CameraWidget
from src.ui.components.control_panel import ControlPanel
from src.ui.components.status_bar import StatusBar


class Dashboard(QMainWindow):
    """
    Main dashboard window for the sign language translator application.

    This dashboard provides a modern interface for real-time camera feed display,
    parameter adjustment, and system monitoring. It integrates camera ingestion,
    frame processing, and user controls in a cohesive interface with proper
    resource management and signal-slot communication between components.
    """
    
    def __init__(self, logger: loguru.logger, config_registry: ConfigRegistry = None):
        """
        Initialize the dashboard.

        Args:
            logger: Logger instance for logging events and errors.
            config_registry: Configuration registry for managing application settings.
                           If None, a new registry will be created.
        """
        super().__init__()
        self.logger = logger
        self.config_registry = config_registry or ConfigRegistry()
        
        # Initialize components
        self.camera_ingestion = None
        self.frame_processor = None
        self.camera_widget = None
        self.control_panel = None
        self.status_bar = None
        
        self.setup_configs()
        self.setup_ui()
        self.setup_connections()
        self.apply_theme()
        
    def setup_configs(self):
        """
        Setup configuration schemas and load configurations.
        
        Registers the camera and processor configuration schemas with the
        registry and loads the current configuration values.
        """
        self.config_registry.register_config_schema("camera", CameraConfig)
        self.config_registry.register_config_schema("processor", FrameProcessorConfig)
        
        # Load configs
        self.camera_config = ConfigRegistry.get_config("camera")
        self.processor_config = ConfigRegistry.get_config("processor")
        
    def setup_ui(self):
        """
        Setup the main dashboard user interface.
        
        Creates the main layout with splitter panes for camera/tabs on the left
        and control panel on the right, along with the status bar.
        """
        self.setWindowTitle("Sign Language Translator Dashboard")
        self.setMinimumSize(1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Camera and tabs
        left_widget = self.setup_left_panel()
        
        # Right side - Control panel
        right_widget = self.setup_right_panel()
        
        # Add to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        # Set initial sizes (70% left, 30% right)
        splitter.setSizes([1000, 400])
        
        main_layout.addWidget(splitter)
        
        # Setup status bar
        self.setup_status_bar()
        
    def setup_left_panel(self) -> QWidget:
        """
        Setup the left panel with camera feed and additional tabs.

        Returns:
            QWidget containing the tabbed interface with camera, logs, and analytics.
        """
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Initialize camera components
        self.camera_ingestion = CameraIngestion(self.camera_config, self.logger)
        self.frame_processor = FramePreprocessor(self.processor_config, self.logger)
        
        # Create camera widget
        self.camera_widget = CameraWidget(
            self.camera_ingestion, 
            self.frame_processor, 
            self.logger
        )
        
        # Create tab widget for different views
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
            }
            QTabBar::tab:hover {
                background-color: #505050;
            }
        """)
        
        # Camera tab
        tabs.addTab(self.camera_widget, "Camera Feed")
        
        # Logs tab
        self.setup_logs_tab(tabs)
        
        # Analytics tab (placeholder)
        self.setup_analytics_tab(tabs)
        
        layout.addWidget(tabs)
        
        return widget
        
    def setup_right_panel(self) -> QWidget:
        """
        Setup the right panel with control widgets.

        Returns:
            QScrollArea containing the control panel for parameter adjustment.
        """
        # Create scroll area for control panel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setMinimumWidth(350)
        
        # Create control panel
        self.control_panel = ControlPanel(self.config_registry, self.logger)
        scroll_area.setWidget(self.control_panel)
        
        # Style scroll area
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #2b2b2b;
            }
            QScrollBar:vertical {
                background-color: #404040;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #606060;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #707070;
            }
        """)
        
        return scroll_area
        
    def setup_logs_tab(self, tabs: QTabWidget):
        """
        Setup the logs display tab.

        Args:
            tabs: The tab widget to add the logs tab to.
        """
        logs_widget = QTextEdit()
        logs_widget.setReadOnly(True)
        logs_widget.setFont(QFont("Consolas", 9))
        logs_widget.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: none;
            }
        """)
        
        # Add some sample log entries
        logs_widget.append("[INFO] Dashboard initialized")
        logs_widget.append("[INFO] Camera connected")
        logs_widget.append("[DEBUG] Frame processing enabled")
        
        tabs.addTab(logs_widget, "Logs")
        
        # Store reference for adding logs
        self.logs_widget = logs_widget
        
    def setup_analytics_tab(self, tabs: QTabWidget):
        """
        Setup the analytics and metrics tab.

        Args:
            tabs: The tab widget to add the analytics tab to.
        """
        analytics_widget = QWidget()
        layout = QVBoxLayout()
        
        # Placeholder for future analytics
        from PyQt6.QtWidgets import QLabel
        placeholder = QLabel("Analytics and metrics will be displayed here")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 16px;
                font-style: italic;
            }
        """)
        
        layout.addWidget(placeholder)
        analytics_widget.setLayout(layout)
        
        tabs.addTab(analytics_widget, "Analytics")
        
    def setup_status_bar(self):
        """
        Setup the status bar for displaying system metrics.
        
        Creates and configures the status bar widget.
        """
        self.status_bar = StatusBar(self.logger)
        self.setStatusBar(self.status_bar)
        
    def setup_connections(self):
        """
        Setup signal-slot connections between components.
        
        Connects parameter change signals from the control panel to handlers
        and frame processing signals to status updates.
        """
        if self.camera_widget and self.control_panel and self.status_bar:
            # Connect parameter changes to update processing
            self.control_panel.parameter_changed.connect(self.on_parameter_changed)
            
            # Connect frame processing to status updates
            self.camera_widget.frame_processed.connect(self.on_frame_processed)
            
    def on_parameter_changed(self, config_name: str, param_name: str, value):
        """
        Handle parameter changes from the control panel.

        Args:
            config_name: Name of the configuration category.
            param_name: Name of the specific parameter.
            value: New value for the parameter.
        """
        try:
            self.logger.info(f"Parameter changed: {config_name}.{param_name} = {value}")
            
            # Update status
            self.status_bar.set_status(f"Updated {param_name}", "#4CAF50")
            
            # Add to logs
            if hasattr(self, "logs_widget"):
                self.logs_widget.append(f"[CONFIG] {config_name}.{param_name} = {value}")
                
            # Here you would update the actual configuration
            # For now, just log the change
            
        except Exception:
            self.logger.exception("Error handling parameter change")
            self.status_bar.set_status("Configuration Error", "#f44336")
            
    def on_frame_processed(self):
        """
        Handle processed frames from the camera widget.

        Args:
            frame: The processed frame as a numpy array.
        """
        # Update FPS counter
        if self.status_bar:
            self.status_bar.update_fps()
            
    def apply_theme(self):
        """
        Apply dark theme styling to the entire application.
        
        Sets the global stylesheet for consistent dark theme appearance
        across all components.
        """
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QSplitter::handle {
                background-color: #555;
            }
            QSplitter::handle:horizontal {
                width: 4px;
            }
            QSplitter::handle:vertical {
                height: 4px;
            }
        """)
        
    def close_event(self, event):
        """
        Handle application close event.

        Args:
            event: The close event from Qt.
        """
        try:
            self.logger.info("Shutting down dashboard...")
            
            # Cleanup components
            if self.camera_widget:
                self.camera_widget.cleanup()
            if self.status_bar:
                self.status_bar.cleanup()
            if self.camera_ingestion:
                self.camera_ingestion.stop()
                
            event.accept()
            
        except Exception:
            self.logger.exception("Error during shutdown")
            event.accept()  # Accept anyway to ensure app closes 