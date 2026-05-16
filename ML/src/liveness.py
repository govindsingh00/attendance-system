"""
Liveness detection using Eye Aspect Ratio (EAR) via MediaPipe Face Mesh.
Compatible with mediapipe 0.10.33 using the new Tasks API.
"""

import cv2
import numpy as np
import os
import urllib.request

try:
    import mediapipe as mp
    from mediapipe.tasks import python as mp_tasks
    from mediapipe.tasks.python.vision import FaceLandmarker, FaceLandmarkerOptions
    from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode
    MEDIAPIPE_AVAILABLE = True
except ImportError as e:
    MEDIAPIPE_AVAILABLE = False
    print(f"[WARNING] mediapipe not installed: {e}")

LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
EAR_THRESHOLD = 0.18
BLINK_FRAMES = 2

MODEL_PATH = os.path.join(os.path.dirname(__file__), "face_landmarker.task")
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"


def _ensure_model():
    if not os.path.exists(MODEL_PATH):
        print("[LIVENESS] Downloading face landmarker model (~30MB)...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("[LIVENESS] Model downloaded successfully.")


def _eye_aspect_ratio(landmarks, eye_indices, img_w, img_h):
    points = []
    for idx in eye_indices:
        lm = landmarks[idx]
        x = int(lm.x * img_w)
        y = int(lm.y * img_h)
        points.append((x, y))
    v1 = np.linalg.norm(np.array(points[1]) - np.array(points[5]))
    v2 = np.linalg.norm(np.array(points[2]) - np.array(points[4]))
    h = np.linalg.norm(np.array(points[0]) - np.array(points[3]))
    if h == 0:
        return 0.0
    return (v1 + v2) / (2.0 * h)


def check_liveness_single_frame(frame, ear_threshold=EAR_THRESHOLD):
    if not MEDIAPIPE_AVAILABLE:
        return {"ear": 0.0, "eyes_open": True, "error": "mediapipe not installed"}

    try:
        _ensure_model()
        img_h, img_w = frame.shape[:2]

        base_options = mp_tasks.BaseOptions(model_asset_path=MODEL_PATH)
        options = FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=VisionTaskRunningMode.IMAGE,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
        )

        with FaceLandmarker.create_from_options(options) as landmarker:
            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            )
            result = landmarker.detect(mp_image)

            if not result.face_landmarks:
                return {"ear": 0.0, "eyes_open": None, "error": "No face found"}

            landmarks = result.face_landmarks[0]
            left_ear = _eye_aspect_ratio(landmarks, LEFT_EYE, img_w, img_h)
            right_ear = _eye_aspect_ratio(landmarks, RIGHT_EYE, img_w, img_h)
            avg_ear = (left_ear + right_ear) / 2.0

            print(f"[LIVENESS DEBUG] EAR={round(avg_ear, 3)} threshold={ear_threshold} eyes_open={avg_ear >= ear_threshold}")

            return {
                "ear": round(avg_ear, 3),
                "eyes_open": avg_ear >= ear_threshold,
                "error": None
            }

    except Exception as e:
        print(f"[LIVENESS EXCEPTION] {e}")
        return {"ear": 0.0, "eyes_open": True, "error": str(e)}


class LivenessDetector:
    def __init__(self, ear_threshold=EAR_THRESHOLD, blink_frames=BLINK_FRAMES):
        self.ear_threshold = ear_threshold
        self.blink_frames = blink_frames
        self.blink_count = 0
        self.closed_frames = 0
        self.is_live = False

    def process_frame(self, frame):
        result = check_liveness_single_frame(frame, self.ear_threshold)
        ear = result.get("ear", 0.0)
        eyes_open = result.get("eyes_open", True)
        blink_detected = False

        if eyes_open is False:
            self.closed_frames += 1
        else:
            if self.closed_frames >= self.blink_frames:
                self.blink_count += 1
                blink_detected = True
                self.is_live = True
            self.closed_frames = 0

        return {
            "ear": ear,
            "blink_detected": blink_detected,
            "blink_count": self.blink_count,
            "is_live": self.is_live,
            "status": "✅ Live" if self.is_live else f"👁️ Please blink (EAR:{ear})",
            "error": result.get("error")
        }

    def reset(self):
        self.blink_count = 0
        self.closed_frames = 0
        self.is_live = False