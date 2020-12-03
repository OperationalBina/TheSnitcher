import cv2


class CameraLiveview:

    def __init__(self):
        self.state = 0
        self._threat_json = [
            {
                'msg': 'threat detected!',
                'position': [0, 0]
            },
            {
                'msg': 'No threat!',
                'position': [0, 0]
            }
        ]
        self.api_json = self._threat_json[self.state]

    def display(self):
        cap = cv2.VideoCapture(0)
        count = 0
        while True:
            ret, frame = cap.read()
            # cv2.imshow('Live Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if count == 100:
                self.state = 1 - self.state
                self.api_json = self._threat_json[self.state]
                count = 0
            count += 1
        cap.release()
        cv2.destroyAllWindows()
