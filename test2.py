import sys
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox, QFileDialog
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from keras.models import load_model
import datetime

# Constants for video processing and model
IMAGE_HEIGHT , IMAGE_WIDTH = 64, 64
SEQUENCE_LENGTH = 5
CLASSES_LIST = ["NonViolence","Violence"]

class VideoThread(QThread):
    frame_processed = pyqtSignal(np.ndarray)
    video_finished = pyqtSignal()

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.is_playing = False
        self.start_time = None
        self.frames_list = []

    def run(self):
        self.cap = cv2.VideoCapture(self.video_path)
        self.is_playing = True
        self.start_time = datetime.datetime.now()
        while self.is_playing:
            ret, frame = self.cap.read()
            if not ret:
                self.video_finished.emit()
                break
            resized_frame = cv2.resize(frame, (IMAGE_WIDTH, IMAGE_HEIGHT))
            self.frame_processed.emit(resized_frame)
            self.msleep(30)  # Adjust sleep time for desired frame rate

    def stop_playback(self):
        self.is_playing = False
        self.cap.release()

    def get_start_time(self):
        return self.start_time

    def get_elapsed_time(self):
        return datetime.datetime.now() - self.start_time if self.start_time else None

class ModelLoaderThread(QThread):
    model_loaded = pyqtSignal(object)

    def run(self):
        model_path = 'C:/Users/WEP/Documents/AI/security/artificail-eye/violence3.keras'

        # Load the Keras model
        model = load_model(model_path)
        self.model_loaded.emit(model)

class ViolenceDetectionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Video processing variables
        self.video_thread = None
        self.model = None  # Initialize model as None
        self.model_loader_thread = ModelLoaderThread()
        self.violence_detected = False  # Variable to track if violence has been detected

        # Connect signals
        self.model_loader_thread.model_loaded.connect(self.on_model_loaded)

        # Variables for processed frame and prediction
        self.processed_frame = None
        self.predicted_class_name = ''

    def initUI(self):
        self.setWindowTitle('Violence Detection App')

        # Create start button
        self.start_button = QPushButton('Start Detection')
        self.start_button.clicked.connect(self.start_detection)

        # Create stop button
        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_detection)
        self.stop_button.setEnabled(False)

        # Create video widget for displaying video feed
        self.video_widget = QVideoWidget(self)
        self.video_widget.setFixedSize(640, 480)  # Set widget size to match video frame size

        # Create media player
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)

        # Create vertical layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.video_widget)
        self.setLayout(layout)

    def start_detection(self):
        video_path, _ = QFileDialog.getOpenFileName(self, "Open video file")
        if video_path:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.video_thread = VideoThread(video_path)
            self.video_thread.frame_processed.connect(self.process_frame)
            self.video_thread.video_finished.connect(self.on_video_finished)
            self.video_thread.start()

            # Start playing video in video widget
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
            self.media_player.play()

    def stop_detection(self):
        if self.video_thread is not None:
            self.video_thread.stop_playback()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.violence_detected = False  # Reset violence detected flag

        # Stop playing video in video widget
        self.media_player.stop()

    def process_frame(self, frame):
        self.processed_frame = frame

        if self.model is not None:
            # Resize the Frame to fixed Dimensions.
            resized_frame = cv2.resize(frame, (IMAGE_HEIGHT, IMAGE_WIDTH))
            
            # Normalize the resized frame.
            normalized_frame = resized_frame / 255
            
            # Appending the pre-processed frame into the frames list
            self.video_thread.frames_list.append(normalized_frame)

            # If we have enough frames in the list to make a prediction
            if len(self.video_thread.frames_list) == SEQUENCE_LENGTH:
                # Convert the list to a numpy array and add a dimension at the 0th index
                frames_array = np.expand_dims(np.array(self.video_thread.frames_list), axis=0)
                
                # Make a prediction
                predicted_labels_probabilities = self.model.predict(frames_array)
                predicted_label = np.argmax(predicted_labels_probabilities[0])
                predicted_class_name = CLASSES_LIST[predicted_label]
                print(predicted_class_name)

                # If violence is detected, show a notification
                if predicted_class_name == 'Violence':
                   
                    self.show_violence_notification()
                    self.violence_detected = True  # Set violence detected flag

                # Remove the oldest frame from the list
                self.video_thread.frames_list.pop(0)

    def on_model_loaded(self, model):
        self.model = model

    def show_violence_notification(self):
        if self.violence_detected:
            QMessageBox.warning(self, 'Violence Detected', 'Violence has been detected in the video!')

    def on_video_finished(self):
        if not self.violence_detected:
            QMessageBox.information(self, 'No Violence Detected', 'No violence was detected in the video!')

    def paintEvent(self, event):
        if self.predicted_class_name:
            painter = QPainter(self)
            painter.setPen(Qt.red)
            painter.setFont(QFont('Arial', 20))
            painter.drawText(20, 40, f'Predicted: {self.predicted_class_name}')

    def closeEvent(self, event):
        if self.video_thread is not None:
            self.video_thread.quit()
        self.model_loader_thread.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ViolenceDetectionApp()
    window.show()
    sys.exit(app.exec_())
