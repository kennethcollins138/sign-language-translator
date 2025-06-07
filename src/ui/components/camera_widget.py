"""Camera widget for displaying real-time camera feed with processing controls."""

from typing import Optional

import cv2
import loguru
import numpy as np
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from src.input.ingestion import CameraIngestion
from src.input.preprocessing import FramePreprocessor


class CameraWidget(QWidget):
    """
    A modern camera widget that displays real-time camera feed with processing controls.

    This widget integrates OpenCV camera capture with PyQt6 for display, providing
    real-time frame processing capabilities with user controls for toggling processing
    and capturing snapshots. It uses QTimer for smooth frame updates and proper
    resource management.
    """
    
    frame_processed = pyqtSignal(np.ndarray)  # Signal for processed frames
    
    def __init__(self, camera_ingestion: CameraIngestion, 
                 frame_processor: FramePreprocessor, 
                 logger: loguru.logger):
        """
        Initialize the camera widget.

        Args:
            camera_ingestion: Camera ingestion instance for capturing frames.
            frame_processor: Frame processor instance for processing captured frames.
            logger: Logger instance for logging events and errors.
        """
        super().__init__()
        self.camera_ingestion = camera_ingestion
        self.frame_processor = frame_processor
        self.logger = logger
        self.current_frame: Optional[np.ndarray] = None
        self.processed_frame: Optional[np.ndarray] = None
        self.is_processing = True
        self.frame_generator = None
        
        self.setup_ui()
        self.setup_timer()
        self.start_camera()
        
    def setup_ui(self):
        """
        Setup the camera widget user interface.
        
        Creates the camera display label and control buttons with appropriate
        styling and layout.
        """
        layout = QVBoxLayout()
        
        # Camera display
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                border: 2px solid #555;
                border-radius: 8px;
            }
        """)
        self.camera_label.setText("Camera Feed")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Control buttons
        controls_layout = QHBoxLayout()
        
        self.toggle_processing_btn = QPushButton("Disable Processing")
        self.toggle_processing_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.toggle_processing_btn.clicked.connect(self.toggle_processing)
        
        self.snapshot_btn = QPushButton("Take Snapshot")
        self.snapshot_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        self.snapshot_btn.clicked.connect(self.take_snapshot)
        
        controls_layout.addWidget(self.toggle_processing_btn)
        controls_layout.addWidget(self.snapshot_btn)
        controls_layout.addStretch()
        
        layout.addWidget(self.camera_label)
        layout.addLayout(controls_layout)
        
        self.setLayout(layout)
        
    def setup_timer(self):
        """
        Setup timer for periodic camera frame updates.
        
        Configures a QTimer to update frames at approximately 30 FPS.
        """
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)  # ~30 FPS
        
    def start_camera(self):
        """
        Initialize the camera frame generator.
        
        Starts the camera ingestion generator for capturing frames.
        Logs success or failure of camera initialization.
        """
        try:
            self.frame_generator = self.camera_ingestion.camera_frames()
            self.logger.info("Camera started successfully")
        except Exception:
            self.logger.exception("Error starting camera")
            
    def update_frame(self):
        """
        Update camera frame display.
        
        Called periodically by the timer to capture and display new frames.
        Handles frame processing if enabled and emits signals for processed frames.
        """
        try:
            if self.frame_generator is None:
                return
                
            # Get next frame from generator
            raw_frame = next(self.frame_generator, None)
            
            if raw_frame is not None:
                self.current_frame = raw_frame
                
                # Process frame if processing is enabled
                if self.is_processing:
                    processed = self.frame_processor.process(raw_frame)
                    display_frame = processed if processed is not None else raw_frame
                    self.processed_frame = processed
                else:
                    display_frame = raw_frame
                    self.processed_frame = None
                
                # Convert frame to Qt format and display
                self.display_frame(display_frame)
                
                # Emit signal for other components
                if self.processed_frame is not None:
                    self.frame_processed.emit(self.processed_frame)
                    
        except StopIteration:
            self.logger.warning("Camera frame generator stopped")
            self.frame_generator = None
        except Exception:
            self.logger.exception("Error updating camera frame")
            
    def display_frame(self, frame: np.ndarray):
        """
        Convert OpenCV frame to Qt format and display in the widget.

        Args:
            frame: The frame to display as a numpy array in BGR format.
        """
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            
            # Create QImage
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Scale to fit label while maintaining aspect ratio
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(
                self.camera_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.camera_label.setPixmap(scaled_pixmap)
            
        except Exception:
            self.logger.exception("Error displaying frame")
            
    def toggle_processing(self):
        """
        Toggle frame processing on or off.
        
        Updates the button text and styling to reflect the current processing state.
        """
        self.is_processing = not self.is_processing
        if self.is_processing:
            self.toggle_processing_btn.setText("Disable Processing")
            self.toggle_processing_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
        else:
            self.toggle_processing_btn.setText("Enable Processing")
            self.toggle_processing_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            
    def take_snapshot(self):
        """
        Take a snapshot of the current frame.
        
        Saves the current frame to disk with a timestamp-based filename.
        """
        if self.current_frame is not None:
            timestamp = cv2.getTickCount()
            filename = f"snapshot_{timestamp}.jpg"
            cv2.imwrite(filename, self.current_frame)
            self.logger.info(f"Snapshot saved as {filename}")
            
    def cleanup(self):
        """
        Clean up resources when the widget is destroyed.
        
        Stops the timer and releases camera resources to prevent memory leaks.
        """
        if self.timer.isActive():
            self.timer.stop()
        if self.camera_ingestion:
            self.camera_ingestion.stop() 