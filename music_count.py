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
closed_hand_count_correct = 0  # Correct closes while music is playing
closed_hand_count_incorrect = 0  # Incorrect closes while music is paused
hand_states = {}  # Dictionary to track the state of each hand (open or closed)
music_playing = False  # To track if the music is currently playing
music_playing_duration = 0  # Total duration of music played
total_music_time = 20  # Total allowed music playing time in seconds
next_music_change_time = time.time() + random.uniform(5, 10)  # To track when music will pause/resume

# Randomize the next music interval (between 5 and 10 seconds)
def random_music_interval():
    return random.uniform(5, 10)

# Start the music initially
pygame.mixer.music.play()
music_playing = True
music_start_time = time.time()

# Initialize Mediapipe Hands object
with mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5) as hands:
    while True:
        current_time = time.time()

        # Manage music playing/pausing logic
        if current_time >= next_music_change_time:
            if music_playing:
                pygame.mixer.music.pause()
                music_playing = False
                next_music_change_time = current_time + random_music_interval()
            else:
                pygame.mixer.music.unpause()
                music_playing = True
                next_music_change_time = current_time + random_music_interval()
                music_start_time = time.time()

        # Track total music playing duration
        if music_playing:
            music_playing_duration += current_time - music_start_time
            music_start_time = current_time  # Reset start time for accurate tracking

        # If music played for 30 seconds, end the game
        if music_playing_duration >= total_music_time:
            break

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

                # Detect if hand is open or closed (based on middle finger tip and base landmarks)
                x_tip, y_tip = int(hand_landmarks.landmark[12].x * w), int(hand_landmarks.landmark[12].y * h)
                x_base, y_base = int(hand_landmarks.landmark[9].x * w), int(hand_landmarks.landmark[9].y * h)

                if y_tip < y_base:
                    current_hand_status = "Open"
                    hand_states[hand_idx] = "Open"
                else:
                    current_hand_status = "Closed"
                    if hand_idx in hand_states and hand_states[hand_idx] == "Open":
                        # Correct close (if music is playing)
                        if music_playing:
                            closed_hand_count_correct += 1
                        # Incorrect close (if music is paused)
                        else:
                            closed_hand_count_incorrect += 1
                        hand_states[hand_idx] = "Closed"

                # Draw the hand landmarks on the flipped frame
                mp_drawing.draw_landmarks(
                    flipped_frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
                )

        # Display real-time correct and incorrect hand closes
        cv2.putText(flipped_frame, f"Correct Closes: {closed_hand_count_correct}", 
                    (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(flipped_frame, f"Incorrect Closes: {closed_hand_count_incorrect}", 
                    (flipped_frame.shape[1] - 300, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the frame
        cv2.imshow("Hand Detection with Music", flipped_frame)

        # Check for the 'q' key to exit
        if cv2.waitKey(1) == ord("q"):
            break

    # After the game ends, update the same window with the final result
    final_message = f"Game Over! Correct Closes: {closed_hand_count_correct}, Incorrect Closes: {closed_hand_count_incorrect}"
    cv2.putText(flipped_frame, final_message, (50, flipped_frame.shape[0] // 2), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
    
    # Display the final result on the same window
    while True:
        # Show the final frame with results
        cv2.imshow("Hand Detection with Music", flipped_frame)

        # Wait for the user to press 'q' to quit
        if cv2.waitKey(1) == ord("q"):
            break

# Release the video capture and close all windows
cap.release()
pygame.mixer.quit()
cv2.destroyAllWindows()
