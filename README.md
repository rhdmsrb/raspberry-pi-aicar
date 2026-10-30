# Raspberry Pi AI Car

A small autonomous car on a Raspberry Pi: it follows a lane from a camera image and stops when it sees a person.

## What it does

- **Lane following.** An NVIDIA PilotNet-style CNN (5 convolutional and 4 dense layers, 252,219 parameters) takes the lower half of each 640×480 camera frame and predicts a steering angle. The angle maps to three motor commands: left (< 70), straight (70–110), and right (> 110).
- **Pedestrian stop.** SSD MobileNetV2 (COCO) runs through OpenCV DNN on its own thread, so detection never blocks steering. The car stops when it sees a person with confidence above 0.5.
- **Safety.** The arrow keys start and stop the car, and the motors stop if a camera frame can't be read. The motors, camera, and GPIO are released on exit.

## Hardware

- Raspberry Pi with a USB/CSI camera
- Dual DC motor driver (PWM + direction pins)
- Optional: HC-06-style Bluetooth serial module, LEDs, switches, and a buzzer (used in the examples)

BCM pins: left motor PWM/dir 18 / 22, 27; right motor PWM/dir 23 / 25, 24.

## Project structure

```
src/main.py                         # runtime entry point
models/lane_navigation_final.h5     # lane-navigation CNN
models/opencv/                      # SSD MobileNetV2 COCO person detector (TensorFlow model zoo)
training/make_model.ipynb           # training pipeline for the lane CNN (dataset not included)
examples/                           # step-by-step scripts, one folder per subsystem
  python_basics/
  gpio_led_switch_buzzer/
  motors/
  bluetooth_serial/
  camera_line_tracing/              # classical CV: threshold -> contour centroid -> steer
  training_data_collection/         # drive with arrow keys and save labeled frames
  cnn_lane_following/
  threshold_lane_following/         # thresholded input + threaded inference
  person_detection/
```

`src/main.py` combines `threshold_lane_following/threaded_cnn_drive_speed_tuned.py` and `person_detection/lane_drive_stop_for_person.py`.

## Install and run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 src/main.py              # or: AI_CAR_CAMERA_INDEX=1 python3 src/main.py
```

Up arrow starts driving, down arrow stops, `q` quits. Test the motor direction and the emergency stop with the wheels off the ground first.

TensorFlow wheels depend on the Raspberry Pi OS, Python version, and CPU architecture. Pick a version that matches your Pi.

## Limitations

- The training images (`training/video.zip`) aren't included, so the lane model can't be retrained from this repo alone.
- Steering is discretized into left / straight / right, and there is no speed control.
- Running it needs the real Raspberry Pi, camera, and motor driver.
