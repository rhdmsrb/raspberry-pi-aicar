# Raspberry Pi AI Car

An autonomous car project using a Raspberry Pi, camera, GPIO motor driver, and machine-learning models.

The repository includes the supplied lane-navigation model and person-detection model. Training images are intentionally not included at this time.

## Features

- Camera-based lane detection
- Steering control for left, straight, and right movement
- Person detection using OpenCV DNN and SSD MobileNet
- Automatic stop when a person is detected
- Up-arrow key to start driving and down-arrow key to stop
- Safe cleanup of the motors, camera, and GPIO on exit

## Project Structure

```text
.
├── src/main.py                         # Main runtime entry point
├── models/lane_navigation_final.h5     # Supplied lane-navigation model
├── models/opencv/                      # Person-detection model files
├── training/make_model.ipynb            # Model-training notebook
├── examples/legacy/                    # Original step-by-step scripts
├── requirements.txt
└── .gitignore
```

## Installation

On the Raspberry Pi, move to the project root and create a Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

TensorFlow installation depends on the Raspberry Pi OS version, Python version, and CPU architecture. If installation fails, choose a TensorFlow version compatible with your environment.

## Running

```bash
python3 src/main.py
```

If the camera is not device `0`, specify the camera index:

```bash
AI_CAR_CAMERA_INDEX=1 python3 src/main.py
```

The motor pins use BCM numbering:

| Function | Pins |
|---|---:|
| Left motor PWM / direction | 18 / 22, 27 |
| Right motor PWM / direction | 23 / 25, 24 |

Before connecting the wheels, test the motor direction and emergency stop with the car lifted off the ground.

## Training Data Status

The training notebook expects a `training/video.zip` file containing the lane-training images. This dataset is intentionally not included in the repository for now. If it is added later, review its size and licensing before publishing it; a separate dataset repository or Git LFS may be appropriate.

## Limitations

- Hardware behavior cannot be verified without the actual Raspberry Pi, camera, and motor driver.
- The original training dataset and reproducible accuracy results are not included.
- The scripts in `examples/legacy` are preserved for development history; use `src/main.py` as the current entry point.
