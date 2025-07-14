import cv2
import mediapipe as mp
import pyautogui
import time
import sys
import os
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import ImageGrab
from datetime import datetime

# === Setup ===
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)

last_action_time = 0
cooldown = 1.5  # seconds
draw_mode = False
draw_points = []

os.makedirs("screenshots", exist_ok=True)

class Overlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gesture Controller")
        self.setGeometry(100, 100, 300, 80)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        layout = QtWidgets.QHBoxLayout()

        self.draw_btn = QtWidgets.QPushButton("Draw")
        self.erase_btn = QtWidgets.QPushButton("Erase")
        self.snap_btn = QtWidgets.QPushButton("Screenshot")

        layout.addWidget(self.draw_btn)
        layout.addWidget(self.erase_btn)
        layout.addWidget(self.snap_btn)
        self.setLayout(layout)

        self.draw_btn.clicked.connect(self.enable_draw)
        self.erase_btn.clicked.connect(self.clear_drawing)
        self.snap_btn.clicked.connect(self.take_screenshot)

    def enable_draw(self):
        global draw_mode
        draw_mode = True

    def clear_drawing(self):
        global draw_points
        draw_points.clear()

    def take_screenshot(self):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/screenshot_{now}.png"
        im = ImageGrab.grab()
        im.save(filename)
        print(f"📸 Screenshot saved: {filename}")

# === Gesture Detection ===
def detect_gesture(landmarks):
    tip_ids = [4, 8, 12, 16, 20]
    fingers = []

    for i in range(1, 5):
        fingers.append(landmarks[tip_ids[i]].y < landmarks[tip_ids[i] - 2].y)

    thumb = landmarks[4].x > landmarks[3].x
    pinky_only = fingers == [True, False, False, False]
    all_up = all(fingers)
    index_up = fingers == [True, False, False, False]
    peace = fingers[0] and fingers[1] and not fingers[2] and not fingers[3]

    if not any(fingers) and not thumb:
        return "fist"
    elif peace:
        return "peace"
    elif index_up:
        return "scroll_down"
    elif all_up:
        return "scroll_up"
    elif thumb and not any(fingers):
        return "volume_up"
    elif pinky_only:
        return "volume_down"
    return None

# === App + Camera ===
app = QtWidgets.QApplication([])
overlay = Overlay()
overlay.show()
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (640, 480))
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)
            h, w, _ = frame.shape
            lm = hand.landmark
            lm_pos = [(int(p.x * w), int(p.y * h)) for p in lm]
            gesture = detect_gesture(lm)

            if gesture == "fist" and time.time() - last_action_time > cooldown:
                pyautogui.press("space")
                print("✊ Play/Pause")
                last_action_time = time.time()

            elif gesture == "peace" and time.time() - last_action_time > cooldown:
                cx, cy = lm_pos[8]
                draw_points.append((cx, cy))
                print("✌️ Drawing...")
                last_action_time = time.time()

            elif gesture == "scroll_down" and time.time() - last_action_time > cooldown:
                pyautogui.scroll(-500)
                print("👇 Scroll Down")
                last_action_time = time.time()

            elif gesture == "scroll_up" and time.time() - last_action_time > cooldown:
                pyautogui.scroll(500)
                print("👆 Scroll Up")
                last_action_time = time.time()

            elif gesture == "volume_up" and time.time() - last_action_time > cooldown:
                pyautogui.press("volumeup")
                print("🔊 Volume Up")
                last_action_time = time.time()

            elif gesture == "volume_down" and time.time() - last_action_time > cooldown:
                pyautogui.press("volumedown")
                print("🔉 Volume Down")
                last_action_time = time.time()

    for i in range(1, len(draw_points)):
        cv2.line(frame, draw_points[i - 1], draw_points[i], (0, 0, 255), 2)

    cv2.imshow("Gesture Controller", frame)
    QtWidgets.QApplication.processEvents()

    if cv2.waitKey(1) & 0xFF in [ord('q'), 27]:
        break

cap.release()
cv2.destroyAllWindows()
sys.exit()
