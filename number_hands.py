import cv2
import mediapipe as mp
import random
import time
import math

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
max_detections = 10  # Number of correct hand detections required
current_number = random.randint(1, 4)  # Random number between 1 and 4
previous_number = current_number
start_time = time.time()  # Start time to track total duration
correct_time_threshold = 2  # 2 seconds required to hold correct hand count
detected_hands_start_time = None  # Time when correct number of hands first detected
progress = 0  # Progress for the circle (0 to 100)

# Modify this to detect more hands (up to 4 hands)
with mp_hands.Hands(static_image_mode=False, max_num_hands=4, min_detection_confidence=0.5) as hands:
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

        # Count the number of detected hands
        hand_count = 0
        if results.multi_hand_landmarks:
            hand_count = len(results.multi_hand_landmarks)
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw the hand landmarks on the flipped frame
                mp_drawing.draw_landmarks(
                    flipped_frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
                )

        # Detect if the correct number of hands is shown for the required duration
        if hand_count == current_number:
            if detected_hands_start_time is None:
                detected_hands_start_time = time.time()  # Start counting if first time detection
            else:
                elapsed_time = time.time() - detected_hands_start_time
                progress = min((elapsed_time / correct_time_threshold) * 100, 100)  # Update progress
                
                if elapsed_time >= correct_time_threshold:
                    # Successfully held for 2 seconds, move to next number
                    correct_detection_count += 1
                    print(f"Correct! Total Correct Detections: {correct_detection_count}")
                    
                    # Reset for next round
                    detected_hands_start_time = None
                    progress = 0  # Reset progress

                    # Generate a new number between 1 and 4, ensuring it's not the same as the previous
                    while True:
                        new_number = random.randint(1, 4)
                        if new_number != current_number:
                            current_number = new_number
                            break
        else:
            # Reset if incorrect hand count detected
            detected_hands_start_time = None
            progress = 0  # Reset progress

        # Draw the progress bar and numbers on the flipped frame
        bar_x, bar_y = 10, 100  # Starting position of the bar
        bar_width = 400  # Total width of the bar (when filled)
        bar_height = 30  # Height of the bar

        # Calculate how much of the bar should be filled based on the correct_detection_count
        filled_width = int((correct_detection_count / max_detections) * bar_width)

        # Draw the filled part of the bar
        cv2.rectangle(flipped_frame, (bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height), (0, 255, 0), -1)
        # Draw the outline of the bar
        cv2.rectangle(flipped_frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)

        # Display the current count on the bar
        cv2.putText(flipped_frame, f"Correct Detections: {correct_detection_count}/{max_detections}", 
                    (bar_x, bar_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Display the current number in the center of the screen
        (text_width, text_height), _ = cv2.getTextSize(f"{current_number}", cv2.FONT_HERSHEY_SIMPLEX, 4, 5)
        number_x = (w - text_width) // 2
        number_y = (h + text_height) // 2
        cv2.putText(flipped_frame, f"{current_number}", (number_x, number_y), cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 5)

        # Draw a progress circle around the number
        radius = 100  # Radius of the circle
        circle_center = (number_x + text_width // 2, number_y - text_height // 2)
        angle = int(progress * 3.6)  # Convert progress (0-100) to angle (0-360)

        # Draw the circular progress
        cv2.ellipse(flipped_frame, circle_center, (radius, radius), -90, 0, angle, (0, 255, 0), 10)

        # Display the final frame
        cv2.imshow("Hand Detection Game", flipped_frame)

        # Check for the 'q' key to exit
        if cv2.waitKey(1) == ord("q"):
            break

        # Check if the target has been reached
        if correct_detection_count >= max_detections:
            end_time = time.time()  # End time
            total_time = end_time - start_time  # Calculate total time
            print(f"You've reached the goal! Total Time: {total_time:.2f} seconds")
            
            # Display the success message and time on the final frame with smaller font size
            cv2.putText(flipped_frame, "You've reached the goal!", 
                        (50, h - 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)  # Smaller font size
            cv2.putText(flipped_frame, f"Time taken: {total_time:.2f} seconds", 
                        (50, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)  # Smaller font size
            cv2.imshow("Hand Detection Game", flipped_frame)
            cv2.waitKey(0)  # Wait for a key press to exit
            break

# Release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()
