import cv2
import os
class FaceCapture:
    """Handles capturing and saving face images for a student."""

    def __init__(self, student_id: str, save_dir: str = "datasets", max_images: int = 20):
        self.student_id = student_id
        self.save_dir = os.path.join(save_dir, student_id)
        self.max_images = max_images
        self.count = 0
        self.cam = None
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def _setup_directory(self):
        """Create student directory if it doesn't exist."""
        os.makedirs(self.save_dir, exist_ok=True)

    def _initialize_camera(self):
        """Initialize the webcam."""
        self.cam = cv2.VideoCapture(0)
        if not self.cam.isOpened():
            raise RuntimeError("Could not open camera.")

    def _detect_face(self, frame):
        """Detect faces in frame and return faces + annotated frame."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.3, minNeighbors=5, minSize=(80, 80)
        )
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Face Detected", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        return faces, frame

    def _save_image(self, frame):
        """Save a single frame as a JPEG image."""
        img_path = os.path.join(self.save_dir, f"{self.count}.jpg")
        cv2.imwrite(img_path, frame)
        self.count += 1
        print(f"[INFO] Captured {self.count}/{self.max_images}")

    def _release_camera(self):
        """Release camera and close all windows."""
        if self.cam:
            self.cam.release()
        cv2.destroyAllWindows()

    def _draw_status(self, frame):
        """Draw capture status on the frame."""
        cv2.putText(
            frame,
            f"Captured: {self.count}/{self.max_images} | 's' save | 'q' quit",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )
        return frame

    def capture(self):
        """Main method to capture face images."""
        self._setup_directory()
        self._initialize_camera()

        print(f"[INFO] Capturing faces for student: {self.student_id}")
        print("[INFO] Press 's' to save when face is detected, 'q' to quit")

        while self.count < self.max_images:
            ret, frame = self.cam.read()

            if not ret:
                print("[ERROR] Failed to read from camera.")
                break

            faces, frame = self._detect_face(frame)
            frame = self._draw_status(frame)

            cv2.imshow("Face Capture", frame)

            key = cv2.waitKey(1)

            if key == ord('s'):
                if len(faces) == 0:
                    print("[WARNING] No face detected! Please face the camera.")
                elif len(faces) > 1:
                    print("[WARNING] Multiple faces detected! Only one person please.")
                else:
                    self._save_image(frame)
            elif key == ord('q'):
                print("[INFO] Capture stopped by user.")
                break

        self._release_camera()
        print(f"[INFO] Done! {self.count} images saved to '{self.save_dir}'")


if __name__ == "__main__":
    student_id = input("Enter student ID: ").strip()

    if not student_id:
        print("[ERROR] Student ID cannot be empty.")
    else:
        capturer = FaceCapture(student_id=student_id)
        capturer.capture()
