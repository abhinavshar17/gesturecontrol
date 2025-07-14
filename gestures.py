# gesture_youtube_snip.py

import cv2
import mediapipe as mp
import pyautogui
import time
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import ImageGrab
from threading import Thread

# === Gesture Setup ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
mp_draw = mp.solutions.drawing_utils

last_action_time = 0
cooldown = 2  # seconds

# === Screenshot Overlay Class ===
class ScreenshotOverlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snip Tool")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowState(QtCore.Qt.WindowFullScreen)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
        qp.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())

        self.hide()
        QtWidgets.QApplication.processEvents()
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        img.save("screenshot.png")
        print("📸 Screenshot saved as screenshot.png")
        self.close()

# === Trigger Screenshot Overlay ===
def launch_screenshot_overlay():
    app = QtWidgets.QApplication([])
    overlay = ScreenshotOverlay()
    overlay.show()
    app.exec_()

# === Get Gesture ===
def get_gesture(hand_landmarks):
    tip_ids = [4, 8, 12, 16, 20]
    fingers = []

    # Check Index to Pinky
    for i in range(1, 5):
        tip = hand_landmarks.landmark[tip_ids[i]].y
        base = hand_landmarks.landmark[tip_ids[i] - 2].y
        fingers.append(tip < base)

    # Check Thumb
    thumb_tip = hand_landmarks.landmark[tip_ids[0]].x
    thumb_base = hand_landmarks.landmark[tip_ids[0] - 2].x
    thumb_open = thumb_tip > thumb_base
    fingers.insert(0, thumb_open)

    # Gesture Mapping
    if fingers == [False, False, False, False, False]:
        return "fist"
    elif fingers == [False, True, True, False, False]:
        return "peace"
    elif fingers == [False, True, False, False, False]:
        return "scroll_down"
    elif fingers == [True, True, False, False, False]:
        return "scroll_up"

    return None

# === Webcam Loop ===
cap = cv2.VideoCapture(0)
while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (640, 480))
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            gesture = get_gesture(handLms)

            if gesture == "fist" and time.time() - last_action_time > cooldown:
                pyautogui.press("space")
                print("⏯️ Play/Pause Toggled")
                last_action_time = time.time()

            elif gesture == "peace" and time.time() - last_action_time > cooldown:
                print("✌️ Peace Gesture Detected → Launching Screenshot Tool")
                Thread(target=launch_screenshot_overlay).start()
                last_action_time = time.time()

            elif gesture == "scroll_down" and time.time() - last_action_time > cooldown:
                pyautogui.scroll(-400)
                print("👇 Scroll Down")
                last_action_time = time.time()

            elif gesture == "scroll_up" and time.time() - last_action_time > cooldown:
                pyautogui.scroll(400)
                print("👆 Scroll Up")
                last_action_time = time.time()

    cv2.imshow("Gesture YouTube Snipper", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
sys.exit()
