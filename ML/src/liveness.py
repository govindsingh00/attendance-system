"""
Liveness detection using Eye Aspect Ratio (EAR) via MediaPipe Face Mesh.

How it works:
- MediaPipe detects 468 facial landmarks on the face
- We use 6 specific landmarks around each eye
- Eye Aspect Ratio (EAR) = ratio of eye height to eye width
- Open eye  → EAR ≈ 0.25–0.35
- Closed eye → EAR ≈ 0.10–0.15
- A blink = EAR drops below threshold then rises back up
- A printed photo cannot blink → EAR stays constant
"""

import cv2
import numpy as np

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("[WARNING] mediapipe not installed. Liveness detection disabled.")


# MediaPipe Face Mesh landmark indices for eyes
# Left eye landmarks (from MediaPipe 468-point model)
LEFT_EYE = [362, 385, 387, 263, 373, 380]
# Right eye landmarks
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

# EAR threshold — below this = eye closed (blink)
EAR_THRESHOLD = 0.22

# Consecutive frames eye must be closed to count as blink
BLINK_FRAMES = 2


def _eye_aspect_ratio(landmarks, eye_indices, img_w, img_h):
    """
    Calculate Eye Aspect Ratio for given eye landmarks.
    
    EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
    
    Where p1-p6 are the 6 eye landmark points:
    p1, p4 = horizontal corners
    p2, p3, p5, p6 = vertical points
    """
    points = []
    for idx in eye_indices:
        lm = landmarks[idx]
        x = int(lm.x * img_w)
        y = int(lm.y * img_h)
        points.append((x, y))

    # Vertical distances
    v1 = np.linalg.norm(np.array(points[1]) - np.array(points[5]))
    v2 = np.linalg.norm(np.array(points[2]) - np.array(points[4]))

    # Horizontal distance
    h = np.linalg.norm(np.array(points[0]) - np.array(points[3]))

    if h == 0:
        return 0.0

    ear = (v1 + v2) / (2.0 * h)
    return ear


class LivenessDetector:
    """
    Stateful liveness detector — tracks blink state across multiple frames.
    One instance per attendance session.
    """

    def __init__(self, ear_threshold=EAR_THRESHOLD, blink_frames=BLINK_FRAMES):
        self.ear_threshold = ear_threshold
        self.blink_frames = blink_frames
        self.blink_count = 0
        self.closed_frames = 0
        self.is_live = False

        if MEDIAPIPE_AVAILABLE:
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=True,       # single frame mode
                max_num_faces=1,
                refine_landmarks=True,        # enables iris landmarks
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        else:
            self.face_mesh = None

    def process_frame(self, frame):
        """
        Process a single frame and update blink state.
        
        Returns dict:
        {
            "ear": float,           # current EAR value
            "blink_detected": bool, # True if a blink happened this frame
            "blink_count": int,     # total blinks so far
            "is_live": bool,        # True if at least 1 blink detected
            "status": str,          # human readable status
            "error": str or None    # error message if any
        }
        """
        if not MEDIAPIPE_AVAILABLE or self.face_mesh is None:
            # If mediapipe not available, pass through (no liveness check)
            return {
                "ear": 0.0,
                "blink_detected": False,
                "blink_count": 0,
                "is_live": True,  # fail open if mediapipe unavailable
                "status": "Liveness check unavailable",
                "error": "mediapipe not installed"
            }

        img_h, img_w = frame.shape[:2]

        # Convert BGR to RGB for MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return {
                "ear": 0.0,
                "blink_detected": False,
                "blink_count": self.blink_count,
                "is_live": self.is_live,
                "status": "No face detected",
                "error": None
            }

        landmarks = results.multi_face_landmarks[0].landmark

        # Calculate EAR for both eyes
        left_ear = _eye_aspect_ratio(landmarks, LEFT_EYE, img_w, img_h)
        right_ear = _eye_aspect_ratio(landmarks, RIGHT_EYE, img_w, img_h)
        avg_ear = (left_ear + right_ear) / 2.0

        blink_detected = False

        # Check for blink
        if avg_ear < self.ear_threshold:
            self.closed_frames += 1
        else:
            # Eyes just opened after being closed
            if self.closed_frames >= self.blink_frames:
                self.blink_count += 1
                blink_detected = True
                if self.blink_count >= 1:
                    self.is_live = True
            self.closed_frames = 0

        if self.is_live:
            status = f"✅ Liveness confirmed ({self.blink_count} blink(s))"
        elif self.closed_frames >= self.blink_frames:
            status = "👁️ Blink detected — keep going..."
        else:
            status = f"👁️ Please blink to confirm liveness (EAR: {avg_ear:.2f})"

        return {
            "ear": round(avg_ear, 3),
            "blink_detected": blink_detected,
            "blink_count": self.blink_count,
            "is_live": self.is_live,
            "status": status,
            "error": None
        }

    def reset(self):
        """Reset state for a new session."""
        self.blink_count = 0
        self.closed_frames = 0
        self.is_live = False


def check_liveness_single_frame(frame, ear_threshold=EAR_THRESHOLD):
    """
    Stateless single-frame liveness check.
    Returns EAR value and whether eyes are open/closed.
    Use LivenessDetector class for multi-frame blink tracking.
    """
    if not MEDIAPIPE_AVAILABLE:
        return {"ear": 0.0, "eyes_open": True, "error": "mediapipe not installed"}

    img_h, img_w = frame.shape[:2]
    mp_face_mesh = mp.solutions.face_mesh

    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        min_detection_confidence=0.5
    ) as face_mesh:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return {"ear": 0.0, "eyes_open": None, "error": "No face found"}

        landmarks = results.multi_face_landmarks[0].landmark
        left_ear = _eye_aspect_ratio(landmarks, LEFT_EYE, img_w, img_h)
        right_ear = _eye_aspect_ratio(landmarks, RIGHT_EYE, img_w, img_h)
        avg_ear = (left_ear + right_ear) / 2.0
        print(f"[LIVENESS DEBUG] EAR={round(avg_ear, 3)} threshold={ear_threshold} eyes_open={avg_ear >= ear_threshold}")
        return {
            "ear": round(avg_ear, 3),
            "eyes_open": avg_ear >= ear_threshold,
            "error": None
        }