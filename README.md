# Raspberry Pi AI Car

라즈베리파이 카메라와 GPIO 모터 드라이버를 사용하는 자율주행 자동차 프로젝트입니다.
현재 저장소에는 제공된 차선 인식 모델과 사람 감지 모델을 포함하고, 학습용 이미지 데이터는 포함하지 않습니다.

## 기능

- 카메라 영상 기반 차선 인식
- 차선 각도에 따른 좌회전·직진·우회전
- OpenCV DNN SSD MobileNet을 이용한 사람 감지 시 정지
- 위쪽 방향키로 주행 시작, 아래쪽 방향키 또는 `q`로 정지
- 종료 시 모터·카메라·GPIO 정리

## 구성

```text
.
├── src/main.py                         # 통합 실행 파일
├── models/lane_navigation_final.h5     # 제공된 차선 모델
├── models/opencv/                      # 사람 감지 모델
├── training/make_model.ipynb            # 학습 노트북 (데이터는 별도 보관)
├── examples/legacy/                    # 기존 단계별 코드
├── requirements.txt
└── .gitignore
```

## 설치

라즈베리파이에서 프로젝트 루트로 이동한 뒤 환경에 맞는 Python을 준비합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

TensorFlow는 Raspberry Pi OS와 Python 버전에 따라 설치 가능한 버전이 달라질 수 있습니다.
설치가 실패하면 사용하는 Raspberry Pi OS, Python 버전, CPU 아키텍처에 맞춰 TensorFlow 버전을 별도로 조정해야 합니다.

## 실행

```bash
python3 src/main.py
```

카메라 장치 번호가 기본값 `0`이 아니면 다음처럼 지정할 수 있습니다.

```bash
AI_CAR_CAMERA_INDEX=1 python3 src/main.py
```

모터 핀은 BCM 기준으로 다음과 같습니다.

| 기능 | 핀 |
|---|---:|
| 왼쪽 모터 PWM / 방향 | 18 / 22, 27 |
| 오른쪽 모터 PWM / 방향 | 23 / 25, 24 |

실제 차량에 연결하기 전에 바퀴를 들어 올린 상태에서 방향과 긴급 정지를 먼저 확인해야 합니다.

## 학습 데이터 보류

학습 노트북은 `training/video.zip`을 압축 해제해 학습 데이터를 읽도록 되어 있습니다.
현재 저장소에는 해당 데이터가 의도적으로 포함되어 있지 않습니다. 나중에 데이터를 추가할 때는 용량과 공개 가능 여부를 확인한 뒤 별도 저장소 또는 Git LFS 사용을 검토하세요.

## 현재 한계

- 실제 라즈베리파이, 카메라, 모터 드라이버가 없으면 하드웨어 동작 검증은 할 수 없습니다.
- 제공된 모델의 학습 데이터와 정확도 재현 결과는 포함되어 있지 않습니다.
- `examples/legacy`는 학습·개발 이력 보존용이며 현재 실행 진입점은 `src/main.py`입니다.
