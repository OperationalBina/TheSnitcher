import cv2
import numpy as np

class CameraLiveview:

    def __init__(self, Pose):
        self.pose = Pose
        self.api_json = []
        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(0)

    def close(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def display(self):
        while True:
            ret, frame = self.cap.read()
            if ret == True:
                img = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
                self.api_json = self.pose(img)
            else:
                print('Unable to read frame, stops processing')
                break
