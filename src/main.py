import cv2

from src.core import logging
from src.core.config.registry import ConfigRegistry
from src.core.config.schema import CameraConfig, FrameProcessorConfig
from src.input.ingestion import CameraIngestion
from src.input.preprocessing import FramePreprocessor


def main():
    logger = logging.setup_logger(__name__)
    logger.info("Starting the application")
    
    # register configs
    ConfigRegistry()
    ConfigRegistry.register_config_schema("camera", CameraConfig)
    ConfigRegistry.register_config_schema("processor", FrameProcessorConfig)
    
    # load configs
    camera_config = ConfigRegistry.get_config("camera")
    processor_config = ConfigRegistry.get_config("processor")
    
    # initialize input components
    cam = CameraIngestion(camera_config, logger)
    frame_processor = FramePreprocessor(processor_config, logger)

    for raw in cam.camera_frames():
        processed = frame_processor.process(raw)
        cv2.imshow("frame", processed if processed is not None else raw)
        
        # Break on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cam.stop()
    
if __name__ == "__main__":
    main()
