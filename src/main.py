"""Raspberry Pi autonomous car controller.

The lane model and the person detector are loaded from the repository's
``models`` directory.  This file is the single production entry point; the
step-by-step scripts in ``examples/`` show how each subsystem was built up.
"""

from __future__ import annotations

import os
import threading
from pathlib import Path

import cv2
import numpy as np
import RPi.GPIO as GPIO
from tensorflow.keras.models import load_model


ROOT = Path(__file__).resolve().parents[1]
LANE_MODEL_PATH = ROOT / "models" / "lane_navigation_final.h5"
PERSON_MODEL_PATH = ROOT / "models" / "opencv" / "frozen_inference_graph.pb"
PERSON_CONFIG_PATH = ROOT / "models" / "opencv" / "ssd_mobilenet_v2_coco_2018_03_29.pbtxt"

CAMERA_INDEX = int(os.getenv("AI_CAR_CAMERA_INDEX", "0"))
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CRUISE_SPEED = 40

# BCM GPIO pins for the dual motor driver.
PWMA, AIN1, AIN2 = 18, 22, 27
PWMB, BIN1, BIN2 = 23, 25, 24


def setup_motors():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for pin in (AIN1, AIN2, PWMA, BIN1, BIN2, PWMB):
        GPIO.setup(pin, GPIO.OUT)

    left = GPIO.PWM(PWMA, 100)
    right = GPIO.PWM(PWMB, 100)
    left.start(0)
    right.start(0)
    return left, right


def motor_stop(left, right):
    left.ChangeDutyCycle(0)
    right.ChangeDutyCycle(0)
    GPIO.output((AIN1, AIN2, BIN1, BIN2), GPIO.LOW)


def motor_go(left, right, speed):
    left.ChangeDutyCycle(speed)
    right.ChangeDutyCycle(speed)
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.HIGH)
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.HIGH)


def motor_left(left, right, speed):
    left.ChangeDutyCycle(0)
    right.ChangeDutyCycle(speed)
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.HIGH)


def motor_right(left, right, speed):
    left.ChangeDutyCycle(speed)
    right.ChangeDutyCycle(0)
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.HIGH)
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.LOW)


def preprocess(image):
    """Match the preprocessing used when the supplied model was trained."""
    height = image.shape[0]
    image = image[height // 2 :, :]
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    image = cv2.resize(image, (200, 66))
    image = cv2.GaussianBlur(image, (5, 5), 0)
    _, image = cv2.threshold(image, 160, 255, cv2.THRESH_BINARY_INV)
    return image.astype(np.float32) / 255.0


def person_detector(frame_state, frame_lock, person_seen, stop_event):
    """Detect people in the newest camera frame without touching the GPIO."""
    detector = cv2.dnn.readNetFromTensorflow(
        str(PERSON_MODEL_PATH), str(PERSON_CONFIG_PATH)
    )

    while not stop_event.is_set():
        with frame_lock:
            frame = None if frame_state[0] is None else frame_state[0].copy()

        if frame is None:
            stop_event.wait(0.01)
            continue

        height, width = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, size=(250, 250), swapRB=True)
        detector.setInput(blob)
        output = detector.forward()

        found_person = False
        for detection in output[0, 0, :, :]:
            if float(detection[2]) <= 0.5:
                continue
            class_id = int(round(float(detection[1])))
            if class_id == 1:  # COCO class 1 is person
                found_person = True
                break

        if found_person:
            person_seen.set()
        stop_event.wait(0.01)


def run():
    missing = [
        path for path in (LANE_MODEL_PATH, PERSON_MODEL_PATH, PERSON_CONFIG_PATH)
        if not path.exists()
    ]
    if missing:
        raise FileNotFoundError("Missing model files: " + ", ".join(map(str, missing)))

    left_motor, right_motor = setup_motors()
    camera = cv2.VideoCapture(CAMERA_INDEX)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    if not camera.isOpened():
        raise RuntimeError(f"Could not open camera index {CAMERA_INDEX}")

    lane_model = load_model(str(LANE_MODEL_PATH), compile=False)
    stop_event = threading.Event()
    person_seen = threading.Event()
    frame_lock = threading.Lock()
    frame_state = [None]
    detector_thread = threading.Thread(
        target=person_detector,
        args=(frame_state, frame_lock, person_seen, stop_event),
        daemon=True,
    )
    detector_thread.start()

    car_state = "stop"
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                print("Camera frame read failed; stopping the motors.")
                motor_stop(left_motor, right_motor)
                continue

            frame = cv2.flip(frame, -1)
            with frame_lock:
                frame_state[0] = frame

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == 82:  # Up arrow
                car_state = "go"
            elif key == 84:  # Down arrow
                car_state = "stop"

            if person_seen.is_set():
                car_state = "stop"
                person_seen.clear()
                print("Person detected; stopping.")

            angle = int(float(lane_model.predict(np.asarray([preprocess(frame)]), verbose=0)[0]))
            if car_state != "go":
                motor_stop(left_motor, right_motor)
            elif 70 <= angle <= 110:
                motor_go(left_motor, right_motor, CRUISE_SPEED)
            elif angle > 110:
                motor_right(left_motor, right_motor, CRUISE_SPEED)
            else:
                motor_left(left_motor, right_motor, CRUISE_SPEED)

            # Keys are read once per frame at the top of the loop; a second
            # waitKey() here would consume (and drop) arrow-key presses.
            cv2.imshow("camera", frame)
    finally:
        stop_event.set()
        detector_thread.join(timeout=2)
        motor_stop(left_motor, right_motor)
        left_motor.stop()
        right_motor.stop()
        camera.release()
        cv2.destroyAllWindows()
        GPIO.cleanup()


if __name__ == "__main__":
    run()
