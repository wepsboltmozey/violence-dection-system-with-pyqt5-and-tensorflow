import cv2
import numpy as np
from keras.models import load_model

# Constants
IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64
SEQUENCE_LENGTH = 16
THRESHOLD_CONSECUTIVE_FRAMES = 5
CLASSES_LIST = ["violence", "non violence"]
model_path = 'C:/Users/WEP/Documents/AI/security/artificail-eye/model/violence3.keras'


# Load the trained model
model = load_model(model_path)

def detect_violence_realtime(model, sequence_length=SEQUENCE_LENGTH):
    # Open a connection to the default camera (0)
    cap = cv2.VideoCapture(0)

    # Variable to keep track of consecutive frames classified as violence
    violence_counter = 0
    frames_queue = []

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)


        # Resize the frame to match the input size of your model
        resized_frame = cv2.resize(frame, (IMAGE_HEIGHT, IMAGE_WIDTH))

        # Preprocess the frame
        normalized_frame = resized_frame / 255

        # Add the frame to the frames queue
        frames_queue.append(normalized_frame)

        # If the frames queue has reached the sequence length, make a prediction
        if len(frames_queue) == sequence_length:
            # Predict the class label
            frames_array = np.array(frames_queue)
            frames_array = np.expand_dims(frames_array, axis=0)
            predicted_labels_probabilities = model.predict(frames_array)[0]
            predicted_label = np.argmax(predicted_labels_probabilities)
            predicted_class_name = CLASSES_LIST[predicted_label]

            # If violence is detected, increment the violence counter
            if predicted_class_name == "Violence":
                violence_counter += 1
                print(violence_counter)
            else:
                violence_counter = 0

            # If violence has been detected for a certain number of consecutive frames, take action
            if violence_counter >= THRESHOLD_CONSECUTIVE_FRAMES:
                # Perform the desired action (e.g., alerting authorities)
                print("Violence detected! Take action.")

                # Reset the violence counter
                violence_counter = 0

            # Remove the oldest frame from the queue
            frames_queue.pop(0)

        # Display the frame
        cv2.imshow('Real-time Violence Detection', frame)

        # If 'q' is pressed, break from the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

# Example usage:
detect_violence_realtime(model)

