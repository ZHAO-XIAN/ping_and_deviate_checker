import json
import socket
import subprocess
import ping3
from argparse import ArgumentParser
from datetime import datetime
from typing import Dict, List


class DevicePinger:
    """
    Class to handle pinging devices and managing ping results.
    """

    def __init__(self, config_path: str, settings_path: str) -> None:
        self.settings = self.load_json(settings_path)
        self.result_json_path = self.settings.get(
            "PING_REUSLT_PATH", "camera_ping_status.json"
        )
        self.data = self.load_json(config_path)
        self.current_hostname = socket.gethostname()

    @staticmethod
    def load_json(file_path: str) -> dict:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def ping_device(self, camera_name: str, ip_address: str) -> Dict[str, str]:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = {"camera": camera_name, "timestamp": timestamp, "status": False}

        try:
            ping_result = ping3.ping(ip_address)
            if ping_result:
                result["status"] = True
            else:
                result["status"] = False
            return result
        except ping3.errors.PingError as e:
            print(f"Error pinging {ip_address}: {e}")
            result["status"] = False
            return result

    def main(self) -> List[Dict[str, str]]:
        results = []
        try:
            group_name = self.current_hostname[:-3]
            cameras = self.data.get(group_name).get(self.current_hostname)

            for camera in cameras:
                result = self.ping_device(camera.get("camera_name"), camera.get("ip"))
                results.append(result)

            with open(self.result_json_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"An error occurred while processing the devices: {e}")
        print(results)
        return results


if __name__ == "__main__":
    parser = ArgumentParser(description="Camera Deviation Checker")
    parser.add_argument(
        "--config_path",
        type=str,
        default="NodeSummaryTable.json",
        help="Path to the config file",
    )
    parser.add_argument(
        "--setting_path",
        type=str,
        default="setting.json",
        help="Path to the setting file",
    )
    args = parser.parse_args()

    divice_pinger = DevicePinger(args.config_path, args.setting_path)
    divice_pinger.main()
