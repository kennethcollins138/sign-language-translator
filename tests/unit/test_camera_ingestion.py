import unittest
from unittest.mock import MagicMock, patch

import numpy as np
from pydantic import BaseModel

from src.input.exceptions import CameraOpenError, FrameReadError
from src.input.ingestion import CameraIngestion


class TestConfig(BaseModel):
    camera_id: int = 0
    fps_limit: int = 30


class TestCameraIngestion(unittest.TestCase):
    """Unit tests for the CameraIngestion class"""

    def setUp(self):
        """Set up for each test"""
        self.mock_logger = MagicMock()
        self.config = TestConfig(camera_id=1, fps_limit=30)

    @patch("src.input.ingestion.cv2.VideoCapture")
    def test_initialization_success(self, mock_video_capture):
        """Test successful initialization of CameraIngestion"""
        mock_cap_instance = mock_video_capture.return_value
        mock_cap_instance.isOpened.return_value = True
        mock_cap_instance.get.side_effect = [1920, 1080, 30]

        cam_ingestion = CameraIngestion(config=self.config, logger=self.mock_logger)

        mock_video_capture.assert_called_with(1)
        self.assertEqual(cam_ingestion.frame_width, 1920)
        self.assertEqual(cam_ingestion.frame_height, 1080)
        self.assertEqual(cam_ingestion.fps, 30)
        self.mock_logger.info.assert_not_called()

    @patch("src.input.ingestion.cv2.VideoCapture")
    def test_initialization_failure(self, mock_video_capture):
        """Test initialization failure raises CameraOpenError"""
        mock_cap_instance = mock_video_capture.return_value
        mock_cap_instance.isOpened.return_value = False

        with self.assertRaises(CameraOpenError):
            CameraIngestion(config=self.config, logger=self.mock_logger)

        mock_video_capture.assert_called_with(1)

    @patch("src.input.ingestion.time")
    @patch("src.input.ingestion.cv2.VideoCapture")
    def test_camera_frames_generator(self, mock_video_capture, mock_time):
        """Test the camera_frames generator"""
        mock_time.time.side_effect = [1.0, 2.0]
        mock_cap_instance = mock_video_capture.return_value
        mock_cap_instance.isOpened.side_effect = [True, True, False]
        mock_cap_instance.get.return_value = 0

        fake_frame = np.uint8(np.random.rand(480, 640, 3) * 255)
        mock_cap_instance.read.return_value = (True, fake_frame)

        cam_ingestion = CameraIngestion(config=self.config, logger=self.mock_logger)

        frames = list(cam_ingestion.camera_frames())

        self.assertEqual(len(frames), 1)
        np.testing.assert_array_equal(frames[0], fake_frame)
        mock_cap_instance.release.assert_called_once()

    @patch("src.input.ingestion.time")
    @patch("src.input.ingestion.cv2.VideoCapture")
    def test_camera_frames_read_fail_then_succeed(self, mock_video_capture, mock_time):
        """Test the camera_frames generator recovers from a failed read"""
        mock_time.time.return_value = 0
        mock_cap_instance = mock_video_capture.return_value
        mock_cap_instance.isOpened.side_effect = [True, True, True, False]
        mock_cap_instance.get.return_value = 0
        fake_frame = np.uint8(np.random.rand(480, 640, 3) * 255)
        mock_cap_instance.read.side_effect = [(False, None), (True, fake_frame)]

        cam_ingestion = CameraIngestion(config=self.config, logger=self.mock_logger)
        frames = list(cam_ingestion.camera_frames())

        self.assertEqual(len(frames), 1)
        self.mock_logger.warning.assert_called_once()

    @patch("src.input.ingestion.time")
    @patch("src.input.ingestion.cv2.VideoCapture")
    def test_camera_frames_read_fail_permanently(self, mock_video_capture, mock_time):
        """Test the camera_frames generator raises FrameReadError after max retries"""
        mock_time.time.return_value = 0
        mock_cap_instance = mock_video_capture.return_value
        mock_cap_instance.isOpened.return_value = True
        mock_cap_instance.get.return_value = 0
        mock_cap_instance.read.return_value = (False, None)  # Simulate a failed read

        cam_ingestion = CameraIngestion(config=self.config, logger=self.mock_logger, max_read_retries=3)

        with self.assertRaises(FrameReadError):
            list(cam_ingestion.camera_frames())

        self.assertEqual(self.mock_logger.warning.call_count, 3)
        mock_cap_instance.release.assert_called_once()

    @patch("src.input.ingestion.time")
    @patch("src.input.ingestion.cv2.VideoCapture")
    def test_frame_rate_throttling(self, mock_video_capture, mock_time):
        """Test that the frame rate is correctly throttled"""
        # We need 2 time calls per loop iteration. The test loop runs 3 times.
        # Iteration 1 (no sleep): t=1.0, t=1.0
        # Iteration 2 (sleep): t=1.01, then t=1.01 + sleep_duration
        # Iteration 3 (no sleep): t=1.07, t=1.07
        sleep_duration = (1 / 30) - 0.01
        mock_time.time.side_effect = [
            1.0, 1.0,  # Iteration 1
            1.01, 1.01 + sleep_duration,  # Iteration 2
            1.07, 1.07,  # Iteration 3
        ]
        mock_sleep = mock_time.sleep

        mock_cap_instance = mock_video_capture.return_value
        # Loop runs 3 times
        mock_cap_instance.isOpened.side_effect = [True, True, True, False]
        mock_cap_instance.get.return_value = 0
        mock_cap_instance.read.return_value = (True, np.uint8([]))

        # fps_limit = 30 means a min interval of ~0.0333s
        self.config.fps_limit = 30
        cam_ingestion = CameraIngestion(config=self.config, logger=self.mock_logger)

        list(cam_ingestion.camera_frames())

        # The second frame is too fast (t=1.01 is only 0.01s after t=1.0), so sleep should be called
        mock_sleep.assert_called_once()
        # Check that it sleeps for roughly the correct amount of time
        self.assertAlmostEqual(mock_sleep.call_args[0][0], sleep_duration, places=3)


    @patch("src.input.ingestion.cv2.VideoCapture")
    @patch("src.input.ingestion.cv2.destroyAllWindows")
    def test_stop_method(self, mock_destroy_windows, mock_video_capture):
        """Test the stop method"""
        mock_cap_instance = mock_video_capture.return_value
        mock_cap_instance.isOpened.return_value = True
        mock_cap_instance.get.return_value = 0

        cam_ingestion = CameraIngestion(config=self.config, logger=self.mock_logger)
        cam_ingestion.stop()

        mock_cap_instance.release.assert_called_once()
        mock_destroy_windows.assert_called_once()

    @patch("src.input.ingestion.cv2.VideoCapture")
    def test_context_manager(self, mock_video_capture):
        """Test CameraIngestion as a context manager"""
        mock_cap_instance = mock_video_capture.return_value
        mock_cap_instance.isOpened.return_value = True
        mock_cap_instance.get.return_value = 0

        with CameraIngestion(config=self.config, logger=self.mock_logger) as cam_ingestion:
            self.assertIsNotNone(cam_ingestion)

        mock_cap_instance.release.assert_called_once()


if __name__ == "__main__":
    unittest.main()