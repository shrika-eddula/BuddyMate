import cv2
import mediapipe as mp
import time


class PoseDetector:

    def __init__(self, mode = False, upBody = False, smooth=True, detectionCon = False, trackCon = 0.5):

        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode, self.upBody, self.smooth, self.detectionCon, self.trackCon)

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        #print(results.pose_landmarks)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)

        return img

    def getPosition(self, img, draw=True):
        lmList= []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                #print(id, lm)
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return lmList

def evaluate_motor_response(lmList):
    if not lmList:
        return 1  # No response (1 point)

    # Extracting keypoints from lmList
    right_shoulder = lmList[12]
    right_elbow = lmList[14]
    right_wrist = lmList[16]

    left_shoulder = lmList[11]
    left_elbow = lmList[13]
    left_wrist = lmList[15]

    # Calculate the distance between shoulder and wrist keypoints
    def calculate_distance(a, b):
        return ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5

    distance_right = calculate_distance(right_shoulder, right_wrist)
    distance_left = calculate_distance(left_shoulder, left_wrist)

    # Evaluate motor response based on the distance thresholds
    if distance_right <= 60 and distance_left <= 60:
        return 6  # Obeys commands for movement (6 points)
    elif distance_right <= 100 and distance_left <= 100:
        return 5  # Purposeful movement to painful stimulus (5 points)
    elif distance_right <= 150 and distance_left <= 150:
        return 4  # Withdraws in response to pain (4 points)
    elif distance_right <= 200 and distance_left <= 200:
        return 3  # Flexion in response to pain (decorticate posturing) (3 points)
    elif distance_right <= 250 and distance_left <= 250:
        return 2  # Extension response in response to pain (decerebrate posturing) (2 points)
    else:
        return 1  # No response (1 point)

def main():
    cap = cv2.VideoCapture(0)
    pTime = 0
    detector = PoseDetector()
    while True:
        success, img = cap.read()
        img = detector.findPose(img)
        lmList = detector.getPosition(img)
        print(lmList)

        # Evaluate motor response
        motor_response_score = evaluate_motor_response(lmList)
        print("Motor Response Score:", motor_response_score)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, f"FPS: {int(fps)}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
        cv2.putText(img, f"Motor Response Score: {motor_response_score}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()