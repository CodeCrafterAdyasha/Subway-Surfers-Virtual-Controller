import cv2
import mediapipe as mp
from pynput.keyboard import Key, Controller
import time

# -------------------------------------------
# INITIAL SETUP
# -------------------------------------------

keyboard = Controller()

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

pTime = 0
current_action = "IDLE"

# -------------------------------------------
# STATE MEMORY (PREVENT REPEAT)
# -------------------------------------------

gesture_state = {
    'left': False,
    'right': False,
    'jump': False,
    'slide': False,
    'hover': False
}

# -------------------------------------------
# LANE BOUNDARIES
# -------------------------------------------

LEFT_BOUND = 0.35
RIGHT_BOUND = 0.65

# -------------------------------------------
# FINGER TIPS
# -------------------------------------------

FINGER_TIPS = [
    mp_hands.HandLandmark.THUMB_TIP,
    mp_hands.HandLandmark.INDEX_FINGER_TIP,
    mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
    mp_hands.HandLandmark.RING_FINGER_TIP,
    mp_hands.HandLandmark.PINKY_TIP
]

# -------------------------------------------
# UTILITY FUNCTIONS
# -------------------------------------------

def press_and_release(key):
    keyboard.press(key)
    keyboard.release(key)

def count_extended_fingers(hand):
    fingers = [False] * 5

    # Thumb
    if hand.landmark[mp_hands.HandLandmark.THUMB_TIP].y < \
       hand.landmark[mp_hands.HandLandmark.THUMB_MCP].y:
        fingers[0] = True

    # Other fingers
    for i in range(1, 5):
        tip = FINGER_TIPS[i].value
        pip = tip - 2
        if hand.landmark[tip].y < hand.landmark[pip].y:
            fingers[i] = True

    return fingers

def draw_lanes(img, w, h):
    lx = int(LEFT_BOUND * w)
    rx = int(RIGHT_BOUND * w)
    cv2.line(img, (lx, 0), (lx, h), (200, 200, 200), 2)
    cv2.line(img, (rx, 0), (rx, h), (200, 200, 200), 2)

# -------------------------------------------
# MAIN LOOP
# -------------------------------------------

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    image = cv2.flip(image, 1)
    h, w, _ = image.shape

    draw_lanes(image, w, h)

    image.flags.writeable = False
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    image.flags.writeable = True

    current_action = "IDLE"

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]

        thumb = hand.landmark[mp_hands.HandLandmark.THUMB_TIP]
        index = hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        center_x = (thumb.x + index.x) / 2

        fingers = count_extended_fingers(hand)

        mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS)

        # -----------------------------
        # JUMP → OPEN PALM
        # -----------------------------
        if all(fingers):
            if not gesture_state['jump']:
                press_and_release(Key.up)
                gesture_state['jump'] = True
            current_action = "JUMP"
        else:
            gesture_state['jump'] = False

        # -----------------------------
        # SLIDE → THUMB + PINKY
        # -----------------------------
        if fingers[0] and fingers[4] and not fingers[1] and not fingers[2] and not fingers[3]:
            if not gesture_state['slide']:
                press_and_release(Key.down)
                gesture_state['slide'] = True
            current_action = "SLIDE"
        else:
            gesture_state['slide'] = False

        # -----------------------------
        # HOVERBOARD → ✌️ INDEX + MIDDLE
        # (Thumb ignored – FIXED)
        # -----------------------------
        if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
            if not gesture_state['hover']:
                press_and_release(Key.space)
                gesture_state['hover'] = True
            current_action = "HOVERBOARD"
        else:
            gesture_state['hover'] = False

        # -----------------------------
        # LEFT / RIGHT → HAND POSITION
        # -----------------------------
        if center_x < LEFT_BOUND:
            if not gesture_state['left']:
                press_and_release(Key.left)
                gesture_state['left'] = True
            gesture_state['right'] = False
            current_action = "LEFT"

        elif center_x > RIGHT_BOUND:
            if not gesture_state['right']:
                press_and_release(Key.right)
                gesture_state['right'] = True
            gesture_state['left'] = False
            current_action = "RIGHT"

        else:
            gesture_state['left'] = False
            gesture_state['right'] = False
            if current_action == "IDLE":
                current_action = "CENTER"

        # DEBUG (optional)
        cv2.putText(image, f"Fingers: {fingers}", (10, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

    # FPS
    cTime = time.time()
    fps = int(1 / (cTime - pTime)) if cTime != pTime else 0
    pTime = cTime

    cv2.putText(image, f"FPS: {fps}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    cv2.putText(image, f"Action: {current_action}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Subway Surfers Virtual Controller", image)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
