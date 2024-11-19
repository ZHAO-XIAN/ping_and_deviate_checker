import json
import os
import cv2
import socket
from skimage.metrics import structural_similarity as ssim
from typing import Union
import numpy as np
from datetime import datetime
from argparse import ArgumentParser


class CameraDeviationChecker:
    def __init__(self, config_path: str, settings_path: str):
        # Input: Paths to config and settings files
        # Output: Initializes various settings and attributes
        self.settings = self.load_json(settings_path)
        self.threshold = self.settings.get("THRESHOLD", 0.9)
        self.standard_image_path = self.settings.get("STANDARD_IMAGE_PATH", "standard.jpg")
        self.result_json_path = self.settings.get("RESULT_PATH", "camera_deviate_status.json")
        self.frame_number = self.settings.get("FRAME_NUMBER", 100)
        self.canny_threshold1 = self.settings.get("CANNY_THRESHOLD1", 100)
        self.canny_threshold2 = self.settings.get("CANNY_THRESHOLD2", 200)
        self.sobel_kernel_size = self.settings.get("SOBEL_KERNEL_SIZE", 5)
        self.data = self.load_json(config_path)
        self.current_hostname = socket.gethostname()
        self.cap = None  # Initialize cap to None

    @staticmethod
    def load_json(file_path: str) -> dict:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def save_image(frame, output_path: str) -> None:
        cv2.imwrite(output_path, frame)
        print(f"Saved image to {output_path}")

    def capture_frame(self) -> tuple:
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame_number)
        ret, frame = self.cap.read()
        return ret, frame

    def pre_processing(self, image: Union[str, np.ndarray]) -> tuple:
        if isinstance(image, str):
            image_gray = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
            if image_gray is None:
                raise ValueError(f"Failed to load image from {image}")
        else:
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        image_canny = cv2.Canny(image_gray, self.canny_threshold1, self.canny_threshold2)
        image_sobel = cv2.Sobel(image_gray, cv2.CV_64F, 1, 1, ksize=self.sobel_kernel_size)
        return image_canny, image_sobel

    @staticmethod
    def calculate_score(standard_image: Union[str, np.ndarray], current_frame: np.ndarray) -> float:
        score, _ = ssim(standard_image, current_frame, full=True)
        return score

    def compare_frames(self, standard_image: Union[str, np.ndarray], current_frame: np.ndarray) -> bool:
        standard_canny, standard_sobel = self.pre_processing(standard_image)
        current_canny, current_sobel = self.pre_processing(current_frame)
        canny_score = self.calculate_score(standard_canny, current_canny)
        sobel_score = self.calculate_score(standard_sobel, current_sobel)
        print("canny_score", canny_score)
        print("sobel_score", sobel_score)
        return (canny_score < self.threshold and sobel_score < self.threshold)

    def check_camera_deviation(self, rtsp: str, camera: str) -> dict:
        self.cap = cv2.VideoCapture(rtsp)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            ret, frame = self.capture_frame()
            camera_standard_image = f"{camera}_{self.standard_image_path}"

            result = {"camera": camera, "timestamp": timestamp, "status": True}

            if not os.path.exists(camera_standard_image):
                if ret:
                    self.save_image(frame, camera_standard_image)
                    result["status"] = "standard image saved"
                else:
                    result["status"] = "no image captured"
            else:
                if ret:
                    is_deviated = self.compare_frames(camera_standard_image, frame)
                    result["status"] = bool(is_deviated)
                else:
                    result["status"] = "no image captured"

            return result

        finally:
            self.release_resources()

    def release_resources(self) -> None:
        if self.cap is not None:
            self.cap.release()
            print("Released video capture resources")

    def main(self) -> None:
        results = []
        try:
            group_name = self.current_hostname[:-3]
            cameras = self.data.get(group_name).get(self.current_hostname)
            
            for camera in cameras:
                result = self.check_camera_deviation(camera.get("rtsp"), camera.get("camera_name"))
                results.append(result)
            with open(self.result_json_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=4)

        except Exception as e:
            print(f"An error occurred while processing the devices: {e}")
        print(results)
        return results


if __name__ == "__main__":
    parser = ArgumentParser(description="Camera Deviation Checker")
    parser.add_argument("--config_path", type=str, default="NodeSummaryTable.json", help="Path to the config file")
    parser.add_argument("--setting_path", type=str, default="setting.json", help="Path to the setting file")
    args = parser.parse_args()

    camera_deviation_checker = CameraDeviationChecker(args.config_path, args.setting_path)
    camera_deviation_checker.main()
