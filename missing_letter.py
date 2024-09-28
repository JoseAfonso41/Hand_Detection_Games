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
closed_hand_count = 0
max_hand_count = 30  # Number of correct hand closures required
hand_states = {}  # Dictionary to track the state of each hand (open or closed)
last_hand_closed = None  # To track which hand was closed last
start_time = None  # Start time to track duration (initialized later)
attempt_started = False  # Flag to check if the first attempt has been made

# List of words to choose from (Portuguese words, 4 or 5 letters)
word_list = ['casa', 'mesa', 'pato', 'porta', 'sala', 'vento', 'bola', 'parede', 'carro', 'livro']

def get_word_with_missing_letter():
    word = random.choice(word_list)
    missing_index = random.randint(0, len(word) - 1)
    missing_letter = word[missing_index].upper()  # Ensure it's in uppercase
    word_with_missing = word[:missing_index] + '_' + word[missing_index+1:]
    return word_with_missing, missing_letter

# Function to generate a random uppercase letter that is not the same as the correct letter
def get_random_letter(exclude_letter):
    random_letter = chr(random.randint(65, 90))  # Get random uppercase letter (A-Z)
    while random_letter == exclude_letter:
        random_letter = chr(random.randint(65, 90))
    return random_letter

# Initial random word with a missing letter
word_with_missing, missing_letter = get_word_with_missing_letter()
# Two options: one is correct (missing letter), and one is a random incorrect letter
correct_letter_position = random.choice([0, 1])  # Randomly choose whether correct letter is left or right
incorrect_letter = get_random_letter(missing_letter)

left_letter = missing_letter if correct_letter_position == 0 else incorrect_letter
right_letter = missing_letter if correct_letter_position == 1 else incorrect_letter

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
                    
                    # Update letter options and word after any closure attempt
                    if hand_idx == 0 and hand_states.get(hand_idx) == "Open":
                        # Left hand closure attempt
                        if left_letter == missing_letter:
                            # Correct letter chosen
                            closed_hand_count += 1
                            print(f"Correct: Left letter chosen. Count: {closed_hand_count}")
                        else:
                            # Incorrect letter chosen
                            print(f"Incorrect: Left letter chosen.")

                        # Generate new random word and letters for the next attempt
                        word_with_missing, missing_letter = get_word_with_missing_letter()
                        correct_letter_position = random.choice([0, 1])
                        incorrect_letter = get_random_letter(missing_letter)
                        left_letter = missing_letter if correct_letter_position == 0 else incorrect_letter
                        right_letter = missing_letter if correct_letter_position == 1 else incorrect_letter
                        hand_states.clear()
                        last_hand_closed = None
                        if not attempt_started:
                            start_time = time.time()  # Start time on the first attempt
                            attempt_started = True

                    elif hand_idx == 1 and hand_states.get(hand_idx) == "Open":
                        # Right hand closure attempt
                        if right_letter == missing_letter:
                            # Correct letter chosen
                            closed_hand_count += 1
                            print(f"Correct: Right letter chosen. Count: {closed_hand_count}")
                        else:
                            # Incorrect letter chosen
                            print(f"Incorrect: Right letter chosen.")

                        # Generate new random word and letters for the next attempt
                        word_with_missing, missing_letter = get_word_with_missing_letter()
                        correct_letter_position = random.choice([0, 1])
                        incorrect_letter = get_random_letter(missing_letter)
                        left_letter = missing_letter if correct_letter_position == 0 else incorrect_letter
                        right_letter = missing_letter if correct_letter_position == 1 else incorrect_letter
                        hand_states.clear()
                        last_hand_closed = None
                        if not attempt_started:
                            start_time = time.time()  # Start time on the first attempt
                            attempt_started = True

                    # Reset hand state after handling closure
                    hand_states[hand_idx] = "Closed"

        # Draw the progress bar and word on the screen
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

        # Display the word with missing letter at the top of the screen
        cv2.putText(flipped_frame, f"{word_with_missing.upper()}", (w // 2 - 100, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4)

        # Display the two letter options at the bottom left and right
        left_letter_box_coords = (50, 300)
        right_letter_box_coords = (w - 200, 300)
        box_thickness = 3
        box_color = (0, 0, 0)  # Black box color

        # Draw box around left letter
        (text_width, text_height), _ = cv2.getTextSize(f"{left_letter}", cv2.FONT_HERSHEY_SIMPLEX, 3, 5)
        cv2.rectangle(flipped_frame, (left_letter_box_coords[0] - 10, left_letter_box_coords[1] - text_height - 10),
                      (left_letter_box_coords[0] + text_width + 10, left_letter_box_coords[1] + 10), box_color, -1)
        cv2.putText(flipped_frame, f"{left_letter}", left_letter_box_coords, cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 5)

        # Draw box around right letter
        (text_width, text_height), _ = cv2.getTextSize(f"{right_letter}", cv2.FONT_HERSHEY_SIMPLEX, 3, 5)
        cv2.rectangle(flipped_frame, (right_letter_box_coords[0] - 10, right_letter_box_coords[1] - text_height - 10),
                      (right_letter_box_coords[0] + text_width + 10, right_letter_box_coords[1] + 10), box_color, -1)
        cv2.putText(flipped_frame, f"{right_letter}", right_letter_box_coords, cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 5)

        # Display the final frame
        cv2.imshow("Hand Detection with Progress Bar and Letters", flipped_frame)

        # Check for the 'q' key to exit
        if cv2.waitKey(1) == ord("q"):
            break

        # Check if the target has been reached
        if closed_hand_count >= max_hand_count:
            end_time = time.time()  # End time
            total_time = end_time - start_time  # Calculate total time
            print(f"You've reached the goal! Time taken: {total_time:.2f} seconds")
            
            # Display time taken on the final frame
            cv2.putText(flipped_frame, f"Time taken: {total_time:.2f} seconds", 
                        (50, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.imshow("Hand Detection with Progress Bar and Letters", flipped_frame)
            cv2.waitKey(0)  # Wait for a key press to exit
            break

# Release the video capture and close all windows
cap.release()
cv2.destroyAllWindows()
