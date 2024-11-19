import json
import os
import cv2
import socket
from skimage.metrics import structural_similarity as ssim
from typing import Union
import numpy as np
from datetime import datetime
from argparse import ArgumentParser

def pre_processing(image: Union[str, np.ndarray]) -> tuple:
        if isinstance(image, str):
            image_gray = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
            if image_gray is None:
                raise ValueError(f"Failed to load image from {image}")
        else:
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        image_canny = cv2.Canny(image_gray, 100, 200)
        image_sobel = cv2.Sobel(image_gray, cv2.CV_64F, 0, 1, ksize = 5)
        return image_canny, image_sobel

def calculate_score(standard_image: Union[str, np.ndarray], current_frame: np.ndarray) -> float:
        score, _ = ssim(standard_image, current_frame, full=True)
        return score

def compare_frames(standard_image: Union[str, np.ndarray], current_frame: np.ndarray) -> bool:
    standard_canny, standard_sobel = pre_processing(standard_image)
    current_canny, current_sobel = pre_processing(current_frame)
    canny_score = calculate_score(standard_canny, current_canny)
    sobel_score = calculate_score(standard_sobel, current_sobel)
    print("canny_score", canny_score)
    print("sobel_score", sobel_score)
    return (canny_score < 0.8 and sobel_score < 0.8)

if __name__ == '__main__':
    result = compare_frames("offset.png", "no_offset.png")
    print("result", result)
