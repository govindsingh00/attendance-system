# TODO: Real-time face recognition using webcam
# Will compare live face embeddings against trained model

import cv2

cam = cv2.VideoCapture(0)
print("Recognition will run here. Press q to quit.")

while True:
    ret, frame = cam.read()
    cv2.imshow("Recognition", frame)
    if cv2.waitKey(1) == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()