import cv2
import json
import numpy as np
import requests
from deepface import DeepFace


class FaceRecognizer:
    """Handles real-time face recognition using saved face encodings."""

    def __init__(
        self,
        encodings_path: str = "models/encodings.json",
        model_name: str = "ArcFace",
        threshold: float = 0.7,
        django_url: str = "http://127.0.0.1:8000/ml/recognize/",
        section: str = "",
        cid: str = "",
        time_slot: str = "",
        teacher_email: str = ""
    ):
        self.encodings_path = encodings_path
        self.model_name = model_name
        self.threshold = threshold
        self.django_url = django_url
        self.section = section
        self.cid = cid
        self.time_slot = time_slot
        self.teacher_email = teacher_email
        self.known_encodings = {}
        self.cam = None
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def _load_encodings(self):
        """Load saved face encodings from JSON file."""
        import os
        if not os.path.exists(self.encodings_path):
            raise FileNotFoundError(
                f"Encodings file not found at '{self.encodings_path}'. Run train.py first."
            )
        with open(self.encodings_path, "r") as f:
            self.known_encodings = json.load(f)
        print(f"[INFO] Loaded encodings for {len(self.known_encodings)} student(s).")

    def _initialize_camera(self):
        """Initialize the webcam."""
        self.cam = cv2.VideoCapture(1)
        if not self.cam.isOpened():
            raise RuntimeError("Could not open camera.")

    def _release_camera(self):
        """Release camera and close all windows."""
        if self.cam:
            self.cam.release()
        cv2.destroyAllWindows()

    def _cosine_similarity(self, a: list, b: list) -> float:
        """Calculate cosine similarity between two embeddings."""
        a, b = np.array(a), np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def _match_face(self, embedding: list) -> tuple:
        """Match a face embedding against all known encodings."""
        best_match = "Unknown"
        best_score = -1

        for student_id, known_enc in self.known_encodings.items():
            score = self._cosine_similarity(embedding, known_enc)
            if score > best_score:
                best_score = score
                best_match = student_id if score >= self.threshold else "Unknown"

        return best_match, round(best_score, 2)

    def _get_embedding(self, frame) -> list | None:
        """Generate face embedding from a frame."""
        temp_path = "temp_frame.jpg"
        cv2.imwrite(temp_path, frame)
        try:
            result = DeepFace.represent(
                img_path=temp_path,
                model_name=self.model_name,
                enforce_detection=False
            )
            emb = np.array(result[0]["embedding"])
            emb = emb / np.linalg.norm(emb)
            return emb.tolist()
        except Exception as e:
            print(f"[WARNING] Could not generate embedding: {e}")
            return None

    def _send_to_django(self, stid: str, score: float):
        """Send recognized student ID to Django backend."""
        if stid == "Unknown":
            return

        try:
            params = {
                "section": self.section,
                "cid": self.cid,
                "time_slot": self.time_slot,
                "teacher_email": self.teacher_email
            }
            response = requests.post(
                self.django_url,
                json={"stid": stid, "score": score},
                params=params,
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                print(f"[✓] {data.get('msg', 'Marked present')} (score: {score})")
            else:
                print(f"[✗] Django returned {response.status_code}: {response.text}")
        except requests.exceptions.ConnectionError:
            print(f"[✗] Django server unreachable. Is it running at {self.django_url}?")
        except requests.exceptions.Timeout:
            print(f"[✗] Request timed out for student {stid}.")
        except Exception as e:
            print(f"[✗] Unexpected error sending to Django: {e}")

    def _draw_result(self, frame, x: int, y: int, w: int, h: int,
                     student_id: str, score: float):
        """Draw bounding box and recognition result on frame."""
        color = (0, 255, 0) if student_id != "Unknown" else (0, 0, 255)
        label = f"ID: {student_id} ({score})"
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        return frame

    def _draw_status(self, frame):
        """Draw status bar on the frame."""
        cv2.putText(frame, "Press 'q' to quit", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        if self.section:
            cv2.putText(frame, f"Section: {self.section} | Course: {self.cid} | Slot: {self.time_slot}",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
        return frame

    def recognize(self):
        """Main method to run real-time face recognition."""
        self._load_encodings()
        self._initialize_camera()

        print("[INFO] Starting face recognition... Press 'q' to quit.")
        print(f"[INFO] Session → Section: {self.section} | CID: {self.cid} | Slot: {self.time_slot} | Teacher: {self.teacher_email}")

        sent_ids = set()

        while True:
            ret, frame = self.cam.read()
            if not ret:
                print("[ERROR] Failed to read from camera.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.3, minNeighbors=5, minSize=(80, 80)
            )

            for (x, y, w, h) in faces:
                face_crop = frame[y:y + h, x:x + w]
                embedding = self._get_embedding(face_crop)

                if embedding:
                    student_id, score = self._match_face(embedding)
                    frame = self._draw_result(frame, x, y, w, h, student_id, score)

                    if student_id != "Unknown" and student_id not in sent_ids:
                        self._send_to_django(student_id, score)
                        sent_ids.add(student_id)
                        print(f"[INFO] Student {student_id} marked present!")

            frame = self._draw_status(frame)
            cv2.imshow("Atmos — Face Recognition", frame)

            if cv2.waitKey(1) == ord('q'):
                print("[INFO] Recognition stopped by user.")
                break

        self._release_camera()
        print(f"[INFO] Session complete. {len(sent_ids)} student(s) marked present: {list(sent_ids)}")


if __name__ == "__main__":
    import sys

    section       = sys.argv[1] if len(sys.argv) > 1 else ""
    cid           = sys.argv[2] if len(sys.argv) > 2 else ""
    time_slot     = sys.argv[3] if len(sys.argv) > 3 else ""
    teacher_email = sys.argv[4] if len(sys.argv) > 4 else ""

    if not all([section, cid, time_slot, teacher_email]):
        print("Usage: python recognize.py <section> <cid> <time_slot> <teacher_email>")
        print("Example: python recognize.py A 1 9-10 teacher@email.com")
        sys.exit(1)

    recognizer = FaceRecognizer(
        section=section,
        cid=cid,
        time_slot=time_slot,
        teacher_email=teacher_email
    )
    recognizer.recognize()