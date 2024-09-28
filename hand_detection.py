import cv2
import mediapipe as mp
import random
import time
import os

# Leaderboard file
LEADERBOARD_FILE = "hand_detection_leaderboard.txt"

# Function to save leaderboard time
def save_leaderboard_time(time_taken):
    # If leaderboard file doesn't exist, create it
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'w') as file:
            file.write(f"{time_taken:.2f}\n")
    else:
        # Load current leaderboard
        with open(LEADERBOARD_FILE, 'r') as file:
            times = [float(line.strip()) for line in file.readlines()]

        # Add the new time
        times.append(time_taken)

        # Sort times and keep top 5
        times = sorted(times)[:5]

        # Save back the sorted times
        with open(LEADERBOARD_FILE, 'w') as file:
            for time_val in times:
                file.write(f"{time_val:.2f}\n")

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
closed_hand_count = 0
max_hand_count = 30  
hand_states = {}  # Dictionary to track the state of each hand (open or closed)
left_number = random.randint(1, 99)  # Random number for left side
right_number = random.randint(1, 99)  # Random number for right side
last_hand_closed = None  # To track which hand was closed last
start_time = time.time()  # Start time to track duration

# Modify this to detect more hands (e.g., 4 hands)
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

        # Draw hand landmarks on the flipped frame
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Draw the hand landmarks on the flipped frame
                mp_drawing.draw_landmarks(
                    flipped_frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
                )
                
                # Get the coordinates for landmarks 12 (middle finger tip) and 9 (middle finger base)
                x, y = int(hand_landmarks.landmark[12].x * w), int(hand_landmarks.landmark[12].y * h)
                x1, y1 = int(hand_landmarks.landmark[9].x * w), int(hand_landmarks.landmark[9].y * h)

                # Detect if hand is open or closed
                if y < y1:
                    current_hand_status = "Open"
                    hand_states[hand_idx] = "Open"
                else:
                    current_hand_status = "Closed"
                    
                    # Check if the correct hand is being closed
                    if hand_idx == 0 and left_number > right_number and hand_states.get(hand_idx) == "Open":
                        # Left hand closed, and left number is bigger
                        if last_hand_closed != 'left':
                            closed_hand_count += 1
                            last_hand_closed = 'left'
                            print(f"Correct: Left hand closed. Count: {closed_hand_count}")
                            # Generate new random numbers after successful closure
                            left_number = random.randint(1, 99)
                            right_number = random.randint(1, 99)
                            hand_states.clear()  # Clear states to reset hand tracking
                            last_hand_closed = None  # Reset so it can detect new closure cycle

                    elif hand_idx == 1 and right_number > left_number and hand_states.get(hand_idx) == "Open":
                        # Right hand closed, and right number is bigger
                        if last_hand_closed != 'right':
                            closed_hand_count += 1
                            last_hand_closed = 'right'
                            print(f"Correct: Right hand closed. Count: {closed_hand_count}")
                            # Generate new random numbers after successful closure
                            left_number = random.randint(1, 99)
                            right_number = random.randint(1, 99)
                            hand_states.clear()  # Clear states to reset hand tracking
                            last_hand_closed = None  # Reset so it can detect new closure cycle

                    else:
                        # If the closure was incorrect, generate new numbers anyway
                        if hand_idx == 0 or hand_idx == 1:
                            left_number = random.randint(1, 99)
                            right_number = random.randint(1, 99)
                            hand_states.clear()  # Clear states to reset hand tracking
                            last_hand_closed = None  # Reset so it can detect new closure cycle

                    # Reset hand state after handling closure
                    hand_states[hand_idx] = "Closed"

        # Draw the progress bar and numbers on the flipped frame
        bar_x, bar_y = 10, 100  # Starting position of the bar
        bar_width = 400  # Total width of the bar (when filled)
        bar_height = 30  # Height of the bar

        # Calculate how much of the bar should be filled based on the closed_hand_count
        filled_width = int((closed_hand_count / max_hand_count) * bar_width)

        # Draw the filled part of the bar
        cv2.rectangle(flipped_frame, (bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height), (0, 255, 0), -1)
        # Draw the outline of the bar
        cv2.rectangle(flipped_frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)

        # Display the current count on the bar
        cv2.putText(flipped_frame, f"Closed Hand Count: {closed_hand_count}/{max_hand_count}", 
                    (bar_x, bar_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Display the random numbers with boxes around them
        left_number_box_coords = (50, 300)
        right_number_box_coords = (w - 200, 300)
        box_thickness = 3
        box_color = (0, 0, 0)  # Black box color

        # Draw box around left number
        (text_width, text_height), _ = cv2.getTextSize(f"{left_number}", cv2.FONT_HERSHEY_SIMPLEX, 3, 5)
        cv2.rectangle(flipped_frame, (left_number_box_coords[0] - 10, left_number_box_coords[1] - text_height - 10),
                      (left_number_box_coords[0] + text_width + 10, left_number_box_coords[1] + 10), box_color, -1)
        cv2.putText(flipped_frame, f"{left_number}", left_number_box_coords, cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 5)

        # Draw box around right number
        (text_width, text_height), _ = cv2.getTextSize(f"{right_number}", cv2.FONT_HERSHEY_SIMPLEX, 3, 5)
        cv2.rectangle(flipped_frame, (right_number_box_coords[0] - 10, right_number_box_coords[1] - text_height - 10),
                      (right_number_box_coords[0] + text_width + 10, right_number_box_coords[1] + 10), box_color, -1)
        cv2.putText(flipped_frame, f"{right_number}", right_number_box_coords, cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 5)

        # Display the final frame
        cv2.imshow('Hand Detection Game', flipped_frame)

        # Check if the player has won
        if closed_hand_count >= max_hand_count:
            end_time = time.time()
            time_taken = end_time - start_time
            print(f"Congratulations! You completed the game in {time_taken:.2f} seconds.")
            
            # Save the time to the leaderboard
            save_leaderboard_time(time_taken)
            
            break

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


cap.release()
cv2.destroyAllWindows()
