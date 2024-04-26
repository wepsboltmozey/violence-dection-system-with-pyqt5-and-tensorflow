import cv2
import numpy as np
from keras.models import load_model

IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64
SEQUENCE_LENGTH = 16
THRESHOLD_CONFIDENCE = 0.93
CONSECUTIVE_FRAMES_THRESHOLD = 10
VIOLENCE_COUNT_THRESHOLD = 5
CLASSES_LIST = ["violence", "non-violence"]
model_path = 'C:/Users/WEP/Documents/AI/security/artificail-eye/model/violence3.keras'
# Load the trained model
model = load_model(model_path)

def predict_video():
    # Use the default camera
    video_reader = cv2.VideoCapture(0)

    # Declare a list to store video frames we will extract.
    frames_list = []
    
    # Counter for consecutive frames with high confidence prediction
    violence_count = 0
    
    # Continuously display the camera view and make predictions
    while True:
        success, frame = video_reader.read()
        if not success:
            break

        # Display the current frame
        cv2.imshow('Camera View', frame)

        # Resize the Frame to fixed Dimensions.
        resized_frame = cv2.resize(frame, (IMAGE_HEIGHT, IMAGE_WIDTH))
        
        # Normalize the resized frame.
        normalized_frame = resized_frame / 255
        
        # Appending the pre-processed frame into the frames list
        frames_list.append(normalized_frame)
        
        # If we have enough frames for a prediction, make the prediction
        if len(frames_list) == SEQUENCE_LENGTH:
            # Passing the pre-processed frames to the model and get the predicted probabilities.
            predicted_labels_probabilities = model.predict(np.expand_dims(frames_list, axis=0))[0]

            # Get the index of class with highest probability.
            predicted_label = np.argmax(predicted_labels_probabilities)

            # Check if the prediction is 'violence' with high confidence
            if predicted_label == 0 and predicted_labels_probabilities[predicted_label] >= THRESHOLD_CONFIDENCE:
                violence_count += 1
                if violence_count >= VIOLENCE_COUNT_THRESHOLD:
                    print(f'Violence detected with high confidence over {CONSECUTIVE_FRAMES_THRESHOLD} frames.')
                    violence_count = 0  # Reset the counter after reporting
            else:
                violence_count = 0  # Reset the counter if any frame does not meet the criteria

            # Clear the frames list to start predicting on next set of frames
            frames_list = []

        # Check if the user pressed the 'q' key to break out of the loop
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_reader.release()
    cv2.destroyAllWindows()

# Perform continuous prediction using the device camera.
predict_video()
