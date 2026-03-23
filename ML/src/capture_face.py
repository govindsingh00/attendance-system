import cv2
import os

student_id = input("Enter student ID: ")
save_dir = f"datasets/{student_id}"
os.makedirs(save_dir, exist_ok=True)

cam = cv2.VideoCapture(0)
count = 0

while count < 5:
    ret, frame = cam.read()
    cv2.imshow("Press s to capture", frame)
    if cv2.waitKey(1) == ord('s'):
        cv2.imwrite(f"{save_dir}/{count}.jpg", frame)
        count += 1
        print(f"Captured {count}/5")

cam.release()
cv2.destroyAllWindows()
print("Done!")