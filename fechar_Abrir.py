import cv2
import mediapipe as mp


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


cap = cv2.VideoCapture(0)


if not cap.isOpened():
    print("Unable to open camera")
    exit()


closed_hand_count = 0
max_hand_count = 200  
hand_states = {}  # Dictionary to track the state of each hand 

# Initialize Mediapipe Hands object
with mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5) as hands:
    while True:
        # Read the frame from the video capture
        ret, frame = cap.read()
        if not ret:
            print("Error reading frame from camera")
            break

        # Convert the frame to RGB for Mediapipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with Mediapipe
        results = hands.process(frame_rgb)

        # Draw hand landmarks on the frame and detect open/closed hand
        if results.multi_hand_landmarks:
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Draw the hand landmarks
                mp_drawing.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
                )
                
                # Get frame dimensions
                h, w, _ = frame.shape
                
                # Get the coordinates for landmarks 12 (middle finger tip) and 9 (middle finger base)
                x, y = int(hand_landmarks.landmark[12].x * w), int(hand_landmarks.landmark[12].y * h)
                x1, y1 = int(hand_landmarks.landmark[9].x * w), int(hand_landmarks.landmark[9].y * h)
                
                # Detect if hand is open or closed
                if y < y1:
                    current_hand_status = "Open"
                    cv2.rectangle(frame, (0, 0), (200, 60), (255, 0, 0), -1)
                    cv2.putText(frame, f"Open Hand {hand_idx+1}", (0, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)
                    
                    # Mark hand as open
                    hand_states[hand_idx] = "Open"
                else:
                    current_hand_status = "Closed"
                    cv2.rectangle(frame, (0, 0), (200, 60), (255, 0, 0), -1)
                    cv2.putText(frame, f"Closed Hand {hand_idx+1}", (0, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)

                    # Check if this hand was previously open
                    if hand_idx in hand_states and hand_states[hand_idx] == "Open":
                        # Count this as a closed hand only after being opened first
                        closed_hand_count += 1
                        closed_hand_count = min(closed_hand_count, max_hand_count)  # Ensure the count doesn't exceed the maximum
                        print(f"Hand {hand_idx+1} completed cycle, Closed Hand Detected: {closed_hand_count} times")

                        # Mark this hand as closed, and reset cycle tracking
                        hand_states[hand_idx] = "Closed"

        # Draw the progress bar
        bar_x, bar_y = 10, 100  
        bar_width = 400  
        bar_height = 30  

        # Calculate how much of the bar should be filled based on the closed_hand_count
        filled_width = int((closed_hand_count / max_hand_count) * bar_width)

        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height), (0, 255, 0), -1)
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)

        
        cv2.putText(frame, f"Closed Hand Count: {closed_hand_count}/{max_hand_count}", 
                    (bar_x, bar_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        
        cv2.imshow("Hand Detection with Progress Bar", frame)

        # Check for the 'q' key to exit
        if cv2.waitKey(1) == ord("q"):
            break


cap.release()
cv2.destroyAllWindows()
