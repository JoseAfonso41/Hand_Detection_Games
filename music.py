import cv2
import mediapipe as mp
import pygame
import time
import random

# Initialize Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialize video capture
cap = cv2.VideoCapture(0)

# Check if camera opened successfully
if not cap.isOpened():
    print("Unable to open camera")
    exit()

# Initialize pygame for music playback
pygame.mixer.init()
pygame.mixer.music.load("C:/Users/zeze_/Contacts/Desktop/Musica_hand/musica_hand.mp3")  # Replace with your audio file path

# Initialize variables
closed_hand_count = 0
max_hand_count = 100  # Maximum hand count for the bar
hand_states = {}  # Dictionary to track the state of each hand (open or closed)
music_playing = False  # To track if the music is currently playing
next_music_change_time = time.time()  # To track when music will pause/resume
start_time = None  # To track when we start filling the bar
end_time = None  # To track the time when bar is full

# Randomize the next music interval (between 5 and 10 seconds)
def random_music_interval():
    return random.uniform(5, 10)

# Start the music initially
pygame.mixer.music.play()
music_playing = True
next_music_change_time += random_music_interval()

# Initialize Mediapipe Hands object
with mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5) as hands:
    while True:
        # Check if it's time to pause or resume music
        current_time = time.time()
        if current_time >= next_music_change_time:
            if music_playing:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
            music_playing = not music_playing
            next_music_change_time = current_time + random_music_interval()

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

        # Draw hand landmarks on the frame and detect open/closed hand
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                handedness_label = results.multi_handedness[hand_idx].classification[0].label
                
                # Get frame dimensions
                h, w, _ = flipped_frame.shape

                # Count the number of fingers raised (based on the handedness)
                finger_count = 0
                finger_tips = [4, 8, 12, 16, 20]
                for i, tip_idx in enumerate(finger_tips[1:]):
                    if hand_landmarks.landmark[tip_idx].y < hand_landmarks.landmark[tip_idx - 2].y:
                        finger_count += 1
                if handedness_label == "Right":
                    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
                        finger_count += 1
                else:
                    if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x:
                        finger_count += 1

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
                    cv2.rectangle(flipped_frame, (0, 0), (200, 60), (255, 0, 0), -1)
                    cv2.putText(flipped_frame, f"Open Hand {hand_idx+1}", (0, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
                    
                    # Mark hand as open
                    hand_states[hand_idx] = "Open"
                else:
                    current_hand_status = "Closed"
                    cv2.rectangle(flipped_frame, (0, 0), (200, 60), (255, 0, 0), -1)
                    cv2.putText(flipped_frame, f"Closed Hand {hand_idx+1}", (0, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)

                    # Check if this hand was previously open
                    if hand_idx in hand_states and hand_states[hand_idx] == "Open":
                        if music_playing:
                            # Count this as a closed hand only after being opened first (when music is playing)
                            closed_hand_count += 1
                            closed_hand_count = min(closed_hand_count, max_hand_count)  # Ensure the count doesn't exceed the maximum
                            print(f"Hand {hand_idx+1} completed cycle, Closed Hand Detected (while playing): {closed_hand_count} times")
                            
                            # Start time tracking when the bar starts filling
                            if closed_hand_count == 1:
                                start_time = time.time()

                            # If the bar is full, stop counting and mark the end time
                            if closed_hand_count == max_hand_count:
                                end_time = time.time()
                        else:
                            # Decrease the count if music is paused
                            closed_hand_count -= 1
                            closed_hand_count = max(closed_hand_count, 0)  # Ensure it doesn't go below 0
                            print(f"Hand {hand_idx+1} closed while paused: {closed_hand_count} times")

                        # Mark this hand as closed, and reset cycle tracking
                        hand_states[hand_idx] = "Closed"

        # Draw the progress bar
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

        # If the bar is full, calculate and display the total time
        if closed_hand_count == max_hand_count and start_time and end_time:
            total_time = end_time - start_time
            cv2.putText(flipped_frame, f"Time taken: {total_time:.2f} seconds", 
                        (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

        # Display the frame
        cv2.imshow("Hand Detection with Progress Bar", flipped_frame)

        # Check for the 'q' key to exit
        if cv2.waitKey(1) == ord("q"):
            break

        # If the bar is full, keep the final frame with the time for a few seconds
        if closed_hand_count == max_hand_count:
            cv2.waitKey(5000)  # Wait for 5 seconds to show the time before closing
            break

# Release the video capture and close all windows
cap.release()
pygame.mixer.quit()
cv2.destroyAllWindows()
