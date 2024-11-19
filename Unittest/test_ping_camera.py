import json
import subprocess
import unittest
from unittest import mock
from unittest.mock import MagicMock, mock_open, patch

from ping_camera import DevicePinger


class TestDevicePinger(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open, read_data='{"PING_REUSLT_PATH": "mock_path.json"}')
    def test_load_json(self, mock_file):
        # Test load_json method
        device_pinger = DevicePinger("NodeSummaryTable_for_v4.json", "setting.json")
        expected_data = {"PING_REUSLT_PATH": "mock_path.json"}
        actual_data = device_pinger.load_json("setting.json")
        self.assertEqual(actual_data, expected_data)
        mock_file.assert_any_call("setting.json", "r", encoding="utf-8")  # Adjust for multiple calls

    @patch("subprocess.check_output", return_value="mock_hostname\n")
    def test_get_current_hostname(self, mock_subprocess):
        # Test get_current_hostname method
        device_pinger = DevicePinger("NodeSummaryTable_for_v4.json", "setting.json")
        expected_hostname = "mock_hostname"
        actual_hostname = device_pinger.get_current_hostname()
        self.assertEqual(actual_hostname, expected_hostname)
        mock_subprocess.assert_called_with("hostname", shell=True, text=True)  # Adjust this line to expect one call

    @patch("subprocess.check_output")
    def test_ping_device_error(self, mock_ping):
        # Simulate ping failure (camera not connected)
        mock_ping.side_effect = subprocess.CalledProcessError(
            returncode = 1,
            cmd = "ping",
            output = None,
            stderr = None
        )
        
        device_pinger = DevicePinger("NodeSummaryTable_for_v4.json", "setting.json")
        result = device_pinger.ping_device("Camera1", "192.168.0.1")
        print("result", result)
        self.assertEqual(result["status"], False)
        
    @patch("ping_camera.ping")
    def test_ping_device_success(self, mock_ping):
        # Simulate successful ping
        device_pinger = DevicePinger("NodeSummaryTable_for_v4.json", "setting.json")
        result = device_pinger.ping_device("Camera1", "127.0.0.1")
        self.assertEqual(result["status"], True)




    @patch("builtins.open", new_callable=mock_open)
    @patch("socket.gethostname", return_value="t1420kai1")
    def test_main(self, mock_file, mock_subprocess):
        # Test main method
        mock_config_data = {
            "t1420k": {
                "t1420kai1": [
                    {"camera_name": "camera1", "ip": "192.168.0.1"},
                    {"camera_name": "camera2", "ip": "192.168.0.2"}
                ]
            }
        }

        # Mock the JSON file read for the config
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_config_data))):
            device_pinger = DevicePinger("NodeSummaryTable_for_v4.json", "setting.json")
            results = device_pinger.main()

            # Verify that results contain mocked cameras and correct statuses
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0]["camera"], "camera1")
            self.assertEqual(results[1]["camera"], "camera2")
            

if __name__ == "__main__":
    unittest.main()
