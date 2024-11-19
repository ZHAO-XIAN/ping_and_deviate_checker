import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from camera_deviate import CameraDeviationChecker


class TestCameraDeviationChecker(unittest.TestCase):
    @patch("builtins.open", create=True)
    @patch("camera_deviate.json.load")
    @patch("camera_deviate.cv2.VideoCapture")
    @patch("camera_deviate.cv2.imread")
    @patch("camera_deviate.os.path.exists")
    def test_check_camera_deviation_no_standard_image(
        self, mock_exists, mock_imread, mock_VideoCapture, mock_json_load, mock_open
    ):
        # 模擬設定和配置檔案
        mock_json_load.side_effect = [
            {"GroupName": {"hostname": [{"camera_name": "Camera1", "rtsp": "rtsp://example.com/stream"}]}},
            {
                "THRESHOLD": 0.9,
                "STANDARD_IMAGE_PATH": "standard.jpg",
                "RESULT_PATH": "mock_result.json",
                "FRAME_NUMBER": 100,
                "CANNY_THRESHOLD1": 100,
                "CANNY_THRESHOLD2": 200,
                "SOBEL_KERNEL_SIZE": 5,
            },
        ]

        # 模擬 VideoCapture
        mock_cap = MagicMock()
        mock_VideoCapture.return_value = mock_cap
        mock_cap.read.return_value = (True, np.zeros((100, 100, 3), dtype=np.uint8))

        # 模擬 os.path.exists，表示標準影像不存在
        mock_exists.return_value = False

        # 初始化 CameraDeviationChecker 類
        checker = CameraDeviationChecker("mock_config.json", "mock_settings.json")

        # 執行 check_camera_deviation 方法
        result = checker.check_camera_deviation("rtsp://example.com/stream", "Camera1")

        # 驗證結果
        self.assertEqual(result["camera"], "Camera1")
        self.assertEqual(result["status"], "standard image saved")
        mock_cap.read.assert_called_once()

    @patch("builtins.open", create=True)
    @patch("camera_deviate.json.load")
    @patch("camera_deviate.cv2.VideoCapture")
    @patch("camera_deviate.cv2.imread")
    @patch("camera_deviate.os.path.exists")
    def test_check_camera_deviation_with_standard_image(
        self, mock_exists, mock_imread, mock_VideoCapture, mock_json_load, mock_open
    ):
        # 模擬設定和配置檔案
        mock_json_load.side_effect = [
            {"GroupName": {"hostname": [{"camera_name": "Camera1", "rtsp": "rtsp://example.com/stream"}]}},
            {
                "THRESHOLD": 0.9,
                "STANDARD_IMAGE_PATH": "standard.jpg",
                "RESULT_PATH": "mock_result.json",
                "FRAME_NUMBER": 100,
                "CANNY_THRESHOLD1": 100,
                "CANNY_THRESHOLD2": 200,
                "SOBEL_KERNEL_SIZE": 5,
            },
        ]

        # 模擬 VideoCapture
        mock_cap = MagicMock()
        mock_VideoCapture.return_value = mock_cap
        mock_cap.read.return_value = (True, np.zeros((100, 100, 3), dtype=np.uint8))

        # 模擬 os.path.exists，表示標準影像存在
        mock_exists.return_value = True

        # 模擬 cv2.imread 返回一個標準影像
        mock_imread.return_value = np.zeros((100, 100), dtype=np.uint8)

        # 初始化 CameraDeviationChecker 類
        checker = CameraDeviationChecker("mock_config.json", "mock_settings.json")

        # 執行 check_camera_deviation 方法
        result = checker.check_camera_deviation("rtsp://example.com/stream", "Camera1")

        # 驗證結果
        self.assertEqual(result["camera"], "Camera1")
        self.assertIn("status", result)
        mock_cap.read.assert_called_once()


if __name__ == "__main__":
    unittest.main()
