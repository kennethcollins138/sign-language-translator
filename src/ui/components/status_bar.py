"""Status bar widget for displaying real-time system and application metrics."""

from PyQt6.QtWidgets import QStatusBar, QHBoxLayout, QLabel, QProgressBar, QWidget
from PyQt6.QtCore import QTimer, pyqtSignal
import psutil
import time
from typing import Optional
import loguru


class StatusBar(QStatusBar):
    """
    A status bar widget for displaying real-time system and application metrics.

    This widget shows performance information including FPS, CPU usage, memory usage,
    application status, and uptime. It updates automatically using a timer and
    provides methods for external components to update specific metrics.
    """
    
    def __init__(self, logger: loguru.logger):
        """
        Initialize the status bar.

        Args:
            logger: Logger instance for logging events and errors.
        """
        super().__init__()
        self.logger = logger
        self.start_time = time.time()
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.current_fps = 0.0
        
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        """
        Setup the status bar user interface.
        
        Creates labels for displaying various metrics and arranges them in
        a horizontal layout within the status bar.
        """
        # Create a container widget for the custom layout
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # FPS display
        self.fps_label = QLabel("FPS: 0.0")
        self.fps_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        
        # CPU usage
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_label.setStyleSheet("""
            QLabel {
                color: #2196F3;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        
        # Memory usage
        self.memory_label = QLabel("Memory: 0%")
        self.memory_label.setStyleSheet("""
            QLabel {
                color: #FF9800;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        
        # Processing status
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        
        # Uptime
        self.uptime_label = QLabel("Uptime: 00:00:00")
        self.uptime_label.setStyleSheet("""
            QLabel {
                color: #9C27B0;
                font-weight: bold;
                padding: 0 10px;
            }
        """)
        
        # Add widgets to layout
        layout.addWidget(self.fps_label)
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.memory_label)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.uptime_label)
        
        container.setLayout(layout)
        
        # Add the container to the status bar
        self.addWidget(container, 1)  # Stretch factor of 1
        
        # Style the status bar
        self.setStyleSheet("""
            QStatusBar {
                background-color: #1e1e1e;
                border-top: 1px solid #555;
            }
        """)
        
    def setup_timer(self):
        """
        Setup timer for periodic status updates.
        
        Configures a QTimer to update system metrics every second.
        """
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)  # Update every second
        
    def update_status(self):
        """
        Update all status information displays.
        
        Called periodically by the timer to refresh CPU usage, memory usage,
        uptime, and FPS calculations.
        """
        try:
            # Update CPU usage
            cpu_percent = psutil.cpu_percent()
            self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")
            
            # Update memory usage
            memory = psutil.virtual_memory()
            self.memory_label.setText(f"Memory: {memory.percent:.1f}%")
            
            # Update uptime
            uptime_seconds = int(time.time() - self.start_time)
            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            seconds = uptime_seconds % 60
            self.uptime_label.setText(f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # Update FPS (calculated from frame updates)
            current_time = time.time()
            if current_time - self.last_fps_time >= 1.0:
                self.current_fps = self.frame_count / (current_time - self.last_fps_time)
                self.fps_label.setText(f"FPS: {self.current_fps:.1f}")
                self.frame_count = 0
                self.last_fps_time = current_time
                
        except Exception as e:
            self.logger.error(f"Error updating status bar: {e}")
            
    def update_fps(self):
        """
        Update the frame count for FPS calculation.
        
        Should be called by external components when a new frame is processed.
        """
        self.frame_count += 1
        
    def set_status(self, status: str, color: str = "#ffffff"):
        """
        Set the processing status message.

        Args:
            status: The status message to display.
            color: The color for the status text (default: white).
        """
        self.status_label.setText(f"Status: {status}")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: bold;
                padding: 0 10px;
            }}
        """)
        
    def cleanup(self):
        """
        Clean up resources when the status bar is destroyed.
        
        Stops the timer to prevent memory leaks and continued execution.
        """
        if self.timer and self.timer.isActive():
            self.timer.stop() 