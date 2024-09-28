import cv2
import mediapipe as mp
import time


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if not cap.isOpened():
    print("Unable to open camera")
    exit()

# Initialize variables
bar_position = 0  # 0 is center, negative to left, positive to right
max_bar_position = 20  # Bar's maximum deviation from center (20 to left, -20 to right)
left_hand_count = 0
right_hand_count = 0
hand_states = {}  # Dictionary to track the state of each hand (open or closed)
start_time = None  # To track when we start filling the bar
end_time = None  # To track the time when bar is full

# Speed factor for adjusting bar movement (can tweak for game balance)
speed_factor = 1  # Adjusted to make 1 closure equal 1 point

# Initialize Mediapipe Hands object
with mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5) as hands:
    while True:
        # Read the frame from the video capture
        ret, frame = cap.read()
        if not ret:
            print("Error reading frame from camera")
            break

        # Flip the frame
        flipped_frame = cv2.flip(frame, 1)

        # Convert the frame to RGB for Mediapipe
        frame_rgb = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)

        # Process the frame with Mediapipe
        results = hands.process(frame_rgb)

        # Get frame dimensions
        h, w, _ = flipped_frame.shape
        middle_x = w // 2  # Middle of the screen

        # Draw a vertical line in the middle of the screen
        cv2.line(flipped_frame, (middle_x, 0), (middle_x, h), (255, 255, 255), 2)

        # Draw hand landmarks on the frame and detect open/closed hand
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                handedness_label = results.multi_handedness[hand_idx].classification[0].label

                # Draw the hand landmarks on the flipped frame
                mp_drawing.draw_landmarks(
                    flipped_frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
                )

                # Get the x and y coordinates of the middle finger tip (landmark 12)
                hand_center_x = int(hand_landmarks.landmark[12].x * w)
                hand_center_y = int(hand_landmarks.landmark[12].y * h)

                # Determine if the hand is on the left or right side of the screen
                if hand_center_x < middle_x:
                    hand_side = "Left"
                else:
                    hand_side = "Right"

                # Count the number of fingers raised (open/closed detection)
                x, y = int(hand_landmarks.landmark[12].x * w), int(hand_landmarks.landmark[12].y * h)
                x1, y1 = int(hand_landmarks.landmark[9].x * w), int(hand_landmarks.landmark[9].y * h)
                
                if y < y1:  # Hand open
                    hand_states[hand_idx] = "Open"
                else:  # Hand closed
                    if hand_idx in hand_states and hand_states[hand_idx] == "Open":
                        if hand_side == "Left":
                            # Left side pushing the bar to the right
                            left_hand_count += 1
                            bar_position += speed_factor
                        else:
                            # Right side pushing the bar to the left
                            right_hand_count += 1
                            bar_position -= speed_factor

                        hand_states[hand_idx] = "Closed"

        # Limit the bar's movement to within the maximum range
        bar_position = max(-max_bar_position, min(bar_position, max_bar_position))

        # Draw the competitive progress bar (centered at the middle)
        bar_x, bar_y = middle_x - 200, 50  # Starting position of the bar
        bar_width = 400  # Total width of the bar (full range)
        bar_height = 30  # Height of the bar

        # Calculate the current bar's filled position based on bar_position
        center_filled_width = int((bar_position / max_bar_position) * (bar_width // 2))

        # Draw the filled part of the bar (positive: right, negative: left)
        if center_filled_width > 0:
            cv2.rectangle(flipped_frame, (middle_x, bar_y), 
                          (middle_x + center_filled_width, bar_y + bar_height), (0, 255, 0), -1)
        elif center_filled_width < 0:
            cv2.rectangle(flipped_frame, (middle_x + center_filled_width, bar_y), 
                          (middle_x, bar_y + bar_height), (0, 255, 0), -1)

        # Draw the outline of the progress bar
        cv2.rectangle(flipped_frame, (middle_x - bar_width // 2, bar_y), 
                      (middle_x + bar_width // 2, bar_y + bar_height), (255, 255, 255), 2)

        # Display the current bar position
        cv2.putText(flipped_frame, f"Left: {left_hand_count} | Right: {right_hand_count}", 
                    (bar_x, bar_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # If the bar reaches either extreme, declare a winner
        if bar_position == max_bar_position:
            cv2.putText(flipped_frame, "Left side wins!", (middle_x - 200, h // 2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)
        elif bar_position == -max_bar_position:
            cv2.putText(flipped_frame, "Right side wins!", (middle_x - 200, h // 2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 5)

        # Display the frame
        cv2.imshow("Hand Detection Competitive Game", flipped_frame)

        # Check for the 'q' key to exit
        if cv2.waitKey(1) == ord("q"):
            break

        # If either side wins, wait a few seconds before exiting
        if bar_position == max_bar_position or bar_position == -max_bar_position:
            cv2.waitKey(5000)  # Wait for 5 seconds to show the winner before closing
            break


cap.release()
cv2.destroyAllWindows()
