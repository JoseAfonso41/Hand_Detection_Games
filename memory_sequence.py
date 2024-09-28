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
sequence = [random.randint(1, 5)]  # Starting sequence with a random number between 1 and 5
round_number = 1
correct_time_threshold = 2  # 2 seconds required to hold correct finger count
detected_fingers_start_time = None  # Time when the current number of fingers was first detected
last_detected_fingers = None  # Stores the last detected finger count to detect changes
progress = 0  # Progress for the circle (0 to 100)
game_over = False

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

# Initialize Mediapipe Hands
with mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5) as hands:
    while not game_over:
        # Show the round number
        round_start_time = time.time()
        while time.time() - round_start_time < 1.5:
            ret, frame = cap.read()
            if not ret:
                print("Error reading frame from camera")
                game_over = True
                break

            flipped_frame = cv2.flip(frame, 1)
            h, w, _ = flipped_frame.shape

            # Display the round number
            round_text = f"Round {round_number}"
            cv2.putText(flipped_frame, round_text, (w // 4, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 5)
            cv2.imshow("Finger Count Game", flipped_frame)
            if cv2.waitKey(1) == ord("q"):
                game_over = True
                break

        if game_over:
            break

        # Show the sequence of numbers briefly
        for number in sequence:
            ret, frame = cap.read()
            if not ret:
                print("Error reading frame from camera")
                game_over = True
                break

            flipped_frame = cv2.flip(frame, 1)
            h, w, _ = flipped_frame.shape

            # Display the current number
            text_size = cv2.getTextSize(f"{number}", cv2.FONT_HERSHEY_SIMPLEX, 5, 10)[0]
            text_x = (w - text_size[0]) // 2
            text_y = (h + text_size[1]) // 2
            cv2.putText(flipped_frame, f"{number}", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255), 10)

            # Show the frame with the number
            cv2.imshow("Finger Count Game", flipped_frame)
            cv2.waitKey(1000)  # Wait for 1 second

        # Hide numbers and start finger detection
        detected_fingers_start_time = None
        last_detected_fingers = None  # Reset last detected finger count
        progress = 0
        current_index = 0

        while current_index < len(sequence) and not game_over:
            number = sequence[current_index]
            correct_input = False

            while not correct_input and not game_over:
                ret, frame = cap.read()
                if not ret:
                    print("Error reading frame from camera")
                    game_over = True
                    break

                flipped_frame = cv2.flip(frame, 1)
                h, w, _ = flipped_frame.shape

                # Convert the frame to RGB for Mediapipe
                frame_rgb = cv2.cvtColor(flipped_frame, cv2.COLOR_BGR2RGB)

                # Process the frame with Mediapipe
                results = hands.process(frame_rgb)

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

                # Ensure filling circle logic starts only for numbers between 1 and 5
                if 1 <= total_fingers_raised <= 5:
                    # Reset detection if the number of fingers changes
                    if last_detected_fingers is not None and total_fingers_raised != last_detected_fingers:
                        detected_fingers_start_time = None
                        progress = 0

                    last_detected_fingers = total_fingers_raised  # Update last detected fingers

                    if detected_fingers_start_time is None:
                        detected_fingers_start_time = time.time()  # Start counting if first time detection
                    else:
                        elapsed_time = time.time() - detected_fingers_start_time
                        if elapsed_time >= correct_time_threshold:
                            # Correct number of fingers detected for 2 seconds
                            if total_fingers_raised == number:
                                correct_input = True
                                detected_fingers_start_time = None
                                progress = 0
                            else:
                                # If the number is incorrect, the game ends after 2 seconds
                                game_over = True
                                break
                        else:
                            progress = min((elapsed_time / correct_time_threshold) * 100, 100)
                else:
                    detected_fingers_start_time = None
                    last_detected_fingers = None
                    progress = 0

                # Draw a circle around the number, filling it based on the progress
                center_x, center_y = w // 2, h // 2
                radius = 150
                thickness = 10
                cv2.circle(flipped_frame, (center_x, center_y), radius, (255, 255, 255), thickness)
                end_angle = int(360 * (progress / 100))
                cv2.ellipse(flipped_frame, (center_x, center_y), (radius, radius), 0, 0, end_angle, (0, 255, 0), thickness)

                # Display the final frame
                cv2.imshow("Finger Count Game", flipped_frame)

                # Check for the 'q' key to exit
                if cv2.waitKey(1) == ord("q"):
                    game_over = True
                    break

            if game_over:
                break

            # Move to the next number in the sequence
            current_index += 1

        if not game_over:
            if current_index == len(sequence):
                # If all numbers in the sequence are correctly input, add a new random number to the sequence
                new_number = random.randint(1, 5)
                # Ensure the new number is not the same as the last number in the sequence
                while new_number == sequence[-1]:
                    new_number = random.randint(1, 5)
                sequence.append(new_number)
                round_number += 1

    # Release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()

    # Display the number of rounds survived when the game ends
    print(f"Game Over! You survived {round_number - 1} rounds.")
