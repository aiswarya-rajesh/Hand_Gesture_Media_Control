
import cv2
import time
import mediapipe as mp
from pynput.keyboard import Controller

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize Keyboard controller
keyboard = Controller()

# Get webcam
cap = cv2.VideoCapture(0)

# Finger tip landmarks
tip_ids = [4, 8, 12, 16, 20]

# Gesture control variables
prev_gesture = None
gesture_delay = 1.5  # seconds
last_gesture_time = 0

def fingers_up(hand_landmarks):
    fingers = []

    # Thumb
    if hand_landmarks.landmark[tip_ids[0]].x < hand_landmarks.landmark[tip_ids[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for id in range(1, 5):
        if hand_landmarks.landmark[tip_ids[id]].y < hand_landmarks.landmark[tip_ids[id] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

def perform_action(gesture_name):
    global last_gesture_time, prev_gesture

    current_time = time.time()
    if gesture_name != prev_gesture or (current_time - last_gesture_time) > gesture_delay:
        print(f"Gesture Detected: {gesture_name}")
        prev_gesture = gesture_name
        last_gesture_time = current_time

        # Map gesture to actions
        if gesture_name == "Fist":
            keyboard.press('k')  # Play/Pause
            keyboard.release('k')
        elif gesture_name == "Palm":
            keyboard.press('s')  # Stop (customizable)
            keyboard.release('s')
        elif gesture_name == "Volume Down":
            keyboard.press('down')
            keyboard.release('down')
        elif gesture_name == "Volume Up":
            keyboard.press('up')
            keyboard.release('up')
        elif gesture_name == "Mute":
            keyboard.press('m')
            keyboard.release('m')
        elif gesture_name == "Next":
            keyboard.press('n')
            keyboard.release('n')
        elif gesture_name == "Previous":
            keyboard.press('p')
            keyboard.release('p')
        elif gesture_name == "Increase Speed":
            keyboard.press('>')
            keyboard.release('>')
        elif gesture_name == "Decrease Speed":
            keyboard.press('<')
            keyboard.release('<')

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesture_text = ""

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lm_list = hand_landmarks.landmark
            fingers = fingers_up(hand_landmarks)

            if fingers == [0, 0, 0, 0, 0]:
                gesture_text = "Fist"
            elif fingers == [1, 1, 1, 1, 1]:
                gesture_text = "Palm"
            elif fingers == [0, 1, 0, 0, 0]:
                gesture_text = "Volume Down"
            elif fingers == [0, 1, 1, 0, 0]:
                gesture_text = "Volume Up"
            elif fingers == [0, 1, 0, 0, 1]:
                gesture_text = "Mute"
            elif fingers == [1, 1, 0, 0, 0]:
                gesture_text = "Next"
            elif fingers == [1, 0, 0, 0, 1]:
                gesture_text = "Previous"
            elif fingers == [0, 1, 1, 1, 0]:
                gesture_text = "Increase Speed"
            elif fingers == [0, 1, 1, 1, 1]:
                gesture_text = "Decrease Speed"

            if gesture_text:
                perform_action(gesture_text)

            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.putText(frame, gesture_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 0, 0), 3)

    cv2.imshow("Hand Gesture Media Controller", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
