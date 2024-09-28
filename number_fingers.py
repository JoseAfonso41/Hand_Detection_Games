import cv2
import mediapipe as mp
import random
import time

# Initialize Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialize video capture
cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if not cap.isOpened():
    print("Unable to open camera")
    exit()

# Initialize variables
correct_detection_count = 0
max_detections = 10  # Number of correct finger detections required
current_number = random.randint(1, 10)  # Random number between 1 and 10
previous_number = current_number
start_time = time.time()  # Start time to track total duration
correct_time_threshold = 2  # 2 seconds required to hold correct finger count
detected_fingers_start_time = None  # Time when correct number of fingers first detected
progress = 0  # Progress for the circle (0 to 100)

# Helper function to count the number of raised fingers
def count_fingers(hand_landmarks, handedness_label):
    # Landmarks for the tips of each finger: Thumb (4), Index (8), Middle (12), Ring (16), Pinky (20)
    finger_tips = [4, 8, 12, 16, 20]
    finger_count = 0

    # Check if each finger is raised: tip is higher (in y-coordinate) than the knuckle (landmark - 2)
    for i, tip_idx in enumerate(finger_tips[1:]):  # Skipping thumb for now
        if hand_landmarks.landmark[tip_idx].y < hand_landmarks.landmark[tip_idx - 2].y:
            finger_count += 1

    # Special logic for thumb based on the hand (left or right)
    if handedness_label == "Right":
        if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:  # Thumb is up if it's to the left of its base (for right hand)
            finger_count += 1
    else:  # Left hand
        if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:  # Thumb is up if it's to the right of its base (for left hand)
            finger_count += 1

    return finger_count

# Modify this to detect more hands (up to 2 hands)
with mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5) as hands:
    while True:
        # Read the frame from the video capture
        ret, frame = cap.read()
        if not ret:
            print("Error reading frame from camera")
            break

        # Flip the camera image horizontally
        flipped_frame = cv2.flip(frame, 1)

        # Convert the frame to RGB for Mediapipe
        frame_rgb = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)

        # Process the frame with Mediapipe
        results = hands.process(frame_rgb)

        # Get frame dimensions
        h, w, _ = flipped_frame.shape

        # Count the number of fingers raised
        total_fingers_raised = 0
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                handedness_label = results.multi_handedness[hand_idx].classification[0].label
                # Count the number of raised fingers on each hand
                total_fingers_raised += count_fingers(hand_landmarks, handedness_label)

                # Draw the hand landmarks on the flipped frame
                mp_drawing.draw_landmarks(
                    flipped_frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
                )

        # Detect if the correct number of fingers is raised for the required duration
        if total_fingers_raised == current_number:
            if detected_fingers_start_time is None:
                detected_fingers_start_time = time.time()  # Start counting if first time detection
            else:
                elapsed_time = time.time() - detected_fingers_start_time
                if elapsed_time >= correct_time_threshold:
                    # Correct number of fingers detected for 2 seconds
                    correct_detection_count += 1
                    print(f"Correct count: {correct_detection_count}/{max_detections}")
                    
                    # Generate a new random number between 1 and 10 (different from the previous one)
                    while current_number == previous_number:
                        current_number = random.randint(1, 10)
                    previous_number = current_number
                    
                    # Reset detection timer
                    detected_fingers_start_time = None
                    progress = 0
                else:
                    progress = min((elapsed_time / correct_time_threshold) * 100, 100)
        else:
            # Reset the timer if the count is incorrect
            detected_fingers_start_time = None
            progress = 0

        # Draw the number in the center of the screen
        text_size = cv2.getTextSize(f"{current_number}", cv2.FONT_HERSHEY_SIMPLEX, 5, 10)[0]
        text_x = (w - text_size[0]) // 2
        text_y = (h + text_size[1]) // 2
        cv2.putText(flipped_frame, f"{current_number}", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255), 10)

        # Draw a circle around the number, filling it based on the progress
        center_x, center_y = w // 2, h // 2
        radius = 150
        thickness = 10
        cv2.circle(flipped_frame, (center_x, center_y), radius, (255, 255, 255), thickness)
        end_angle = int(360 * (progress / 100))
        cv2.ellipse(flipped_frame, (center_x, center_y), (radius, radius), 0, 0, end_angle, (0, 255, 0), thickness)

        # Draw the progress bar for correct answers at the top left
        bar_x, bar_y = 10, 50
        bar_width = 400
        bar_height = 30
        filled_width = int((correct_detection_count / max_detections) * bar_width)

        # Draw the filled part of the bar
        cv2.rectangle(flipped_frame, (bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height), (0, 255, 0), -1)
        # Draw the outline of the bar
        cv2.rectangle(flipped_frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)
        # Display the current count on the bar
        cv2.putText(flipped_frame, f"Correct: {correct_detection_count}/{max_detections}", 
                    (bar_x, bar_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Display the final frame
        cv2.imshow("Finger Count Game", flipped_frame)

        # Check for the 'q' key to exit
        if cv2.waitKey(1) == ord("q"):
            break

        # Check if the game is completed
        if correct_detection_count >= max_detections:
            end_time = time.time()
            total_time = end_time - start_time
            print(f"Game completed in {total_time:.2f} seconds")
            
            # Display total time on screen
            cv2.putText(flipped_frame, f"Game completed in {total_time:.2f} seconds", 
                        (50, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.imshow("Finger Count Game", flipped_frame)
            cv2.waitKey(0)  # Wait for key press to exit
            break

# Release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()
