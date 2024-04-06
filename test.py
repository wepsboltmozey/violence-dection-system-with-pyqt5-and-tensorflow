import sys
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QImage, QPixmap, QPainter, QFont
import tensorflow as tf
import datetime

# Constants for video processing and model
IMAGE_HEIGHT = 224
IMAGE_WIDTH = 224
CLASSES_LIST = ['Non-Violence', 'Violence']

class CameraThread(QThread):
    frame_processed = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.is_capturing = False
        self.start_time = None

    def run(self):
        self.cap = cv2.VideoCapture(0)
        self.is_capturing = True
        self.start_time = datetime.datetime.now()
        while self.is_capturing:
            ret, frame = self.cap.read()
            if not ret:
                break
            resized_frame = cv2.resize(frame, (IMAGE_WIDTH, IMAGE_HEIGHT))
            self.frame_processed.emit(resized_frame)
            self.msleep(30)  # Adjust sleep time for desired frame rate

    def stop_capture(self):
        self.is_capturing = False
        self.cap.release()

    def get_start_time(self):
        return self.start_time

    def get_elapsed_time(self):
        return datetime.datetime.now() - self.start_time if self.start_time else None

class ModelLoaderThread(QThread):
    model_loaded = pyqtSignal(object)

    def run(self):
        model_path = 'C:/Users/WEP/Desktop/INTELLIGENT SECURITY CAMERA SYSTEM/violence/'  # Update path to saved model folder
        model = tf.saved_model.load(model_path)
        self.model_loaded.emit(model)

class ViolenceDetectionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Video processing variables
        self.camera_thread = CameraThread()
        self.model = None  # Initialize model as None
        self.model_loader_thread = ModelLoaderThread()

        # Connect signals
        self.camera_thread.frame_processed.connect(self.process_frame)
        self.model_loader_thread.model_loaded.connect(self.on_model_loaded)

        # Variables for processed frame and prediction
        self.processed_frame = None
        self.predicted_class_name = ''

    def initUI(self):
        self.setWindowTitle('Violence Detection App')

        # Create start button
        self.start_button = QPushButton('Start Capture and Detection')
        self.start_button.clicked.connect(self.start_capture_and_detection)

        # Create stop button
        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_capture_and_detection)
        self.stop_button.setEnabled(False)

        # Create label for displaying video feed
        self.video_label = QLabel(self)
        self.video_label.setFixedSize(640, 480)  # Set label size to match video frame size

        # Create vertical layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.video_label)
        self.setLayout(layout)

    def start_capture_and_detection(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.camera_thread.start()

    def stop_capture_and_detection(self):
        self.camera_thread.stop_capture()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def process_frame(self, frame):
        self.processed_frame = frame

        if self.model is not None:
            frame = self.processed_frame / 255.0  # Normalize pixel values (0-1)
            frame = np.expand_dims(frame, axis=0)  # Add batch dimension
            predicted_labels_probabilities = self.model(frame)
            predicted_label = np.argmax(predicted_labels_probabilities[0])
            self.predicted_class_name = CLASSES_LIST[predicted_label]

            if self.predicted_class_name == 'Violence':
                self.show_violence_notification()

        self.update_video_label()

    def on_model_loaded(self, model):
        self.model = model

    def show_violence_notification(self):
        QMessageBox.information(self, 'Violence Detected', 'Violence has been detected in the video!')

    def update_video_label(self):
        if self.processed_frame is not None:
            frame = cv2.cvtColor(self.processed_frame, cv2.COLOR_BGR2RGB)
            qImg = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qImg)
            self.video_label.setPixmap(pixmap)
            self.video_label.setScaledContents(True)

    def paintEvent(self, event):
        if self.predicted_class_name:
            painter = QPainter(self)
            painter.setPen(Qt.red)
            painter.setFont(QFont('Arial', 20))
            painter.drawText(20, 40, f'Predicted: {self.predicted_class_name}')

    def closeEvent(self, event):
        self.camera_thread.quit()
        self.model_loader_thread.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ViolenceDetectionApp()
    window.show()
    sys.exit(app.exec_())
