"""Control panel widget for real-time parameter adjustment of the processing pipeline."""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QSpinBox, QGroupBox, QCheckBox, QPushButton,
                             QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict, Any
import loguru

from src.core.config.registry import ConfigRegistry


class ControlPanel(QWidget):
    """
    A control panel widget for real-time adjustment of processing pipeline parameters.

    This widget provides grouped controls for camera settings, frame processing
    parameters, and model configuration. It emits signals when parameters change
    to notify other components of the updates.
    """
    
    parameter_changed = pyqtSignal(str, str, object)  # config_name, param_name, value
    
    def __init__(self, config_registry: ConfigRegistry, logger: loguru.logger):
        """
        Initialize the control panel.

        Args:
            config_registry: Configuration registry for accessing configuration schemas.
            logger: Logger instance for logging parameter changes and errors.
        """
        super().__init__()
        self.config_registry = config_registry
        self.logger = logger
        self.controls: Dict[str, Dict[str, QWidget]] = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """
        Setup the control panel user interface.
        
        Creates organized groups of controls for different configuration categories
        and applies the dark theme styling.
        """
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Control Panel")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
                padding: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Camera controls
        self.setup_camera_controls(layout)
        
        # Processor controls
        self.setup_processor_controls(layout)
        
        # Model controls (placeholder for future)
        self.setup_model_controls(layout)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Apply dark theme styling
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin: 10px 0px;
                padding-top: 15px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #ffffff;
            }
            QSlider::groove:horizontal {
                border: 1px solid #555;
                height: 8px;
                background: #2b2b2b;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #555;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QSpinBox, QComboBox {
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px;
                color: #ffffff;
            }
            QCheckBox {
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #2b2b2b;
                border: 2px solid #555;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
                border-radius: 4px;
            }
        """)
        
    def setup_camera_controls(self, parent_layout: QVBoxLayout):
        """
        Setup camera configuration controls.

        Args:
            parent_layout: The parent layout to add the camera controls to.
        """
        group = QGroupBox("Camera Settings")
        layout = QVBoxLayout()
        
        # Frame rate control
        fps_layout = QHBoxLayout()
        fps_label = QLabel("FPS:")
        fps_slider = QSlider(Qt.Orientation.Horizontal)
        fps_slider.setRange(1, 60)
        fps_slider.setValue(30)
        fps_value = QLabel("30")
        
        fps_slider.valueChanged.connect(
            lambda v: self.on_parameter_changed("camera", "fps", v, fps_value)
        )
        
        fps_layout.addWidget(fps_label)
        fps_layout.addWidget(fps_slider)
        fps_layout.addWidget(fps_value)
        
        # Resolution control
        res_layout = QHBoxLayout()
        res_label = QLabel("Resolution:")
        res_combo = QComboBox()
        res_combo.addItems(["640x480", "1280x720", "1920x1080"])
        res_combo.setCurrentText("640x480")
        res_combo.currentTextChanged.connect(
            lambda v: self.on_parameter_changed("camera", "resolution", v)
        )
        
        res_layout.addWidget(res_label)
        res_layout.addWidget(res_combo)
        res_layout.addStretch()
        
        # Auto-exposure
        auto_exp_check = QCheckBox("Auto Exposure")
        auto_exp_check.setChecked(True)
        auto_exp_check.toggled.connect(
            lambda v: self.on_parameter_changed("camera", "auto_exposure", v)
        )
        
        layout.addLayout(fps_layout)
        layout.addLayout(res_layout)
        layout.addWidget(auto_exp_check)
        
        # Store controls for access
        self.controls["camera"] = {
            "fps": fps_slider,
            "resolution": res_combo,
            "auto_exposure": auto_exp_check
        }
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
        
    def setup_processor_controls(self, parent_layout: QVBoxLayout):
        """
        Setup frame processor controls.

        Args:
            parent_layout: The parent layout to add the processor controls to.
        """
        group = QGroupBox("Frame Processing")
        layout = QVBoxLayout()
        
        # Blur amount
        blur_layout = QHBoxLayout()
        blur_label = QLabel("Blur Amount:")
        blur_slider = QSlider(Qt.Orientation.Horizontal)
        blur_slider.setRange(0, 20)
        blur_slider.setValue(0)
        blur_value = QLabel("0")
        
        blur_slider.valueChanged.connect(
            lambda v: self.on_parameter_changed("processor", "blur_amount", v, blur_value)
        )
        
        blur_layout.addWidget(blur_label)
        blur_layout.addWidget(blur_slider)
        blur_layout.addWidget(blur_value)
        
        # Contrast
        contrast_layout = QHBoxLayout()
        contrast_label = QLabel("Contrast:")
        contrast_slider = QSlider(Qt.Orientation.Horizontal)
        contrast_slider.setRange(50, 200)
        contrast_slider.setValue(100)
        contrast_value = QLabel("1.0")
        
        contrast_slider.valueChanged.connect(
            lambda v: self.on_parameter_changed("processor", "contrast", v/100.0, contrast_value)
        )
        
        contrast_layout.addWidget(contrast_label)
        contrast_layout.addWidget(contrast_slider)
        contrast_layout.addWidget(contrast_value)
        
        # Brightness
        brightness_layout = QHBoxLayout()
        brightness_label = QLabel("Brightness:")
        brightness_slider = QSlider(Qt.Orientation.Horizontal)
        brightness_slider.setRange(-100, 100)
        brightness_slider.setValue(0)
        brightness_value = QLabel("0")
        
        brightness_slider.valueChanged.connect(
            lambda v: self.on_parameter_changed("processor", "brightness", v, brightness_value)
        )
        
        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(brightness_slider)
        brightness_layout.addWidget(brightness_value)
        
        # Enable/disable processing steps
        median_filter_check = QCheckBox("Median Filter")
        median_filter_check.toggled.connect(
            lambda v: self.on_parameter_changed("processor", "median_filter", v)
        )
        
        edge_detection_check = QCheckBox("Edge Detection")
        edge_detection_check.toggled.connect(
            lambda v: self.on_parameter_changed("processor", "edge_detection", v)
        )
        
        layout.addLayout(blur_layout)
        layout.addLayout(contrast_layout)
        layout.addLayout(brightness_layout)
        layout.addWidget(median_filter_check)
        layout.addWidget(edge_detection_check)
        
        # Store controls
        self.controls["processor"] = {
            "blur_amount": blur_slider,
            "contrast": contrast_slider,
            "brightness": brightness_slider,
            "median_filter": median_filter_check,
            "edge_detection": edge_detection_check
        }
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
        
    def setup_model_controls(self, parent_layout: QVBoxLayout):
        """
        Setup model and inference controls.

        Args:
            parent_layout: The parent layout to add the model controls to.
        """
        group = QGroupBox("Model Settings")
        layout = QVBoxLayout()
        
        # Confidence threshold
        conf_layout = QHBoxLayout()
        conf_label = QLabel("Confidence Threshold:")
        conf_slider = QSlider(Qt.Orientation.Horizontal)
        conf_slider.setRange(0, 100)
        conf_slider.setValue(50)
        conf_value = QLabel("0.5")
        
        conf_slider.valueChanged.connect(
            lambda v: self.on_parameter_changed("model", "confidence_threshold", v/100.0, conf_value)
        )
        
        conf_layout.addWidget(conf_label)
        conf_layout.addWidget(conf_slider)
        conf_layout.addWidget(conf_value)
        
        # Model selection
        model_layout = QHBoxLayout()
        model_label = QLabel("Model:")
        model_combo = QComboBox()
        model_combo.addItems(["MediaPipe", "Custom CNN", "Transformer"])
        model_combo.currentTextChanged.connect(
            lambda v: self.on_parameter_changed("model", "model_type", v)
        )
        
        model_layout.addWidget(model_label)
        model_layout.addWidget(model_combo)
        model_layout.addStretch()
        
        # Enable real-time inference
        realtime_check = QCheckBox("Real-time Inference")
        realtime_check.setChecked(False)
        realtime_check.toggled.connect(
            lambda v: self.on_parameter_changed("model", "realtime", v)
        )
        
        layout.addLayout(conf_layout)
        layout.addLayout(model_layout)
        layout.addWidget(realtime_check)
        
        # Store controls
        self.controls["model"] = {
            "confidence_threshold": conf_slider,
            "model_type": model_combo,
            "realtime": realtime_check
        }
        
        group.setLayout(layout)
        parent_layout.addWidget(group)
        
    def on_parameter_changed(self, config_name: str, param_name: str, 
                           value: Any, label_widget: QLabel = None):
        """
        Handle parameter changes from controls.

        Args:
            config_name: Name of the configuration category.
            param_name: Name of the specific parameter.
            value: New value for the parameter.
            label_widget: Optional label widget to update with the new value.
        """
        try:
            # Update label if provided
            if label_widget:
                if isinstance(value, float):
                    label_widget.setText(f"{value:.2f}")
                else:
                    label_widget.setText(str(value))
            
            # Emit signal for other components
            self.parameter_changed.emit(config_name, param_name, value)
            
            self.logger.debug(f"Parameter changed: {config_name}.{param_name} = {value}")
            
        except Exception as e:
            self.logger.error(f"Error handling parameter change: {e}")
            
    def get_control_value(self, config_name: str, param_name: str) -> Any:
        """
        Get the current value of a control widget.

        Args:
            config_name: Name of the configuration category.
            param_name: Name of the specific parameter.

        Returns:
            The current value of the control, or None if not found.
        """
        if config_name in self.controls and param_name in self.controls[config_name]:
            control = self.controls[config_name][param_name]
            
            if isinstance(control, QSlider):
                return control.value()
            elif isinstance(control, QComboBox):
                return control.currentText()
            elif isinstance(control, QCheckBox):
                return control.isChecked()
            elif isinstance(control, QSpinBox):
                return control.value()
                
        return None 