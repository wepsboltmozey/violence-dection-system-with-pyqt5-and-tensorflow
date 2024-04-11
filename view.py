import base64
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtGui import *
import cv2
import numpy as np
import tensorflow as tf   
from model_file import ModelLoaderThread
from preview import Ui_preview
import mysql.connector as connector

# Constants for video processing and model
IMAGE_HEIGHT = 224
IMAGE_WIDTH = 224
CLASSES_LIST = ['Non-Violence', 'Violence']

class VideoDialog(QDialog):
    def __init__(self, videos):
        super().__init__()
        self.setWindowTitle("Select Video")
        self.videos = videos
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.doubleClicked.connect(self.video_selected)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)
        self.populate_list()

    def populate_list(self):
        for video in self.videos:
            item = QListWidgetItem(video[1])
            item.setData(Qt.UserRole, video[0])  # Store video ID as item data
            self.list_widget.addItem(item)

    def video_selected(self, item):
        video_id = item.data(Qt.UserRole)
        self.accept()

class ScreenshotDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Screenshot Name")
        layout = QVBoxLayout()
        self.edit_text = QLineEdit()
        layout.addWidget(self.edit_text)
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_screenshot_name(self):
        if self.exec() == QDialog.Accepted:
            return self.edit_text.text()
        return ""
    
class ViolenceDetectionWorker(QThread):
    detection_result = pyqtSignal(str, float)

    def __init__(self, model, video_path):
        super().__init__()
        self.model = model
        self.video_path = video_path

    def run(self):
        try:
            frames_list = self.extract_frames(self.video_path)
            frames_batch = self.prepare_frames(frames_list)
            prediction = self.model(frames_batch, training=False)
            class_name, confidence = self.process_prediction(prediction)
            self.detection_result.emit(class_name, confidence)
        except Exception as e:
            print(f"Error predicting violence: {e}")

    def extract_frames(self, video_path, num_frames=16):
        frames_list = []
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)

        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue
            resized_frame = cv2.resize(frame, (64, 64))
            normalized_frame = resized_frame.astype(np.float32) / 255.0
            frames_list.append(normalized_frame)

        # If less than num_frames frames were extracted, duplicate the last frame to match the required number
        while len(frames_list) < num_frames:
            frames_list.append(frames_list[-1])

        cap.release()
        return frames_list

    def prepare_frames(self, frames_list):
        frames_batch = np.stack(frames_list, axis=0)
        return frames_batch

    def process_prediction(self, prediction):
        class_index = np.argmax(prediction)
        class_name = CLASSES_LIST[class_index]
        confidence = prediction[0][class_index]
        return class_name, confidence



class Preview(QWidget, Ui_preview):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Initialize media player and video widget
        self.view.setLayout(QVBoxLayout())
        self.player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)
        self.view.layout().addWidget(self.video_widget)

        # Connect buttons and slider
        self.play.clicked.connect(self.toggle_play)
        self.pause.clicked.connect(self.toggle_play)
        self.playerSlider.sliderMoved.connect(self.set_position)
        self.cancelView.clicked.connect(self.clear_view)
        self.deviceVid.clicked.connect(self.browse_device_video)
        self.dataVid.clicked.connect(self.browse_database_video)
        

        # Update play time every second
        self.play_time_timer = QTimer(self)
        self.play_time_timer.timeout.connect(self.update_play_time)
        self.play_time_timer.start(1000)

        # Database connection
        self.connection = connector.connect(
            host="localhost",
            user="root",
            password="",
            database="cameradb"
        )

        self.scene = QGraphicsScene()

        

        # Load violence detection model
        self.model_loader_thread = ModelLoaderThread()
        self.model_loader_thread.model_loaded.connect(self.on_model_loaded)
        self.model = None
        self.model_loader_thread.start()



        self.violence_worker = None

    def on_model_loaded(self, model):
        self.model = model

    def toggle_play(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def set_position(self, position):
        self.player.setPosition(position * 1000)

    def clear_view(self):
        self.scene.clear()
        self.player.stop()

    def browse_device_video(self):
        video_path, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi *.mkv)")
        if video_path:
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
            self.player.play()
            # Check for playback errors
            if self.player.error():
                error_message = self.player.errorString()
                print(f"Error playing video: {error_message}")
            else:
                self.detect_violence(video_path)

    def browse_database_video(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, VideoFile FROM video")
        videos = cursor.fetchall()

        dialog = VideoDialog(videos)
        if dialog.exec() == QDialog.Accepted:
            video_id = dialog.list_widget.currentItem().data(Qt.UserRole)
            cursor.execute("SELECT path FROM video WHERE id = %s", (video_id,))
            path = cursor.fetchone()[0]
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
            self.player.play()
            self.detect_violence(path)

    def update_play_time(self):
        position = self.player.position() / 1000
        duration = self.player.duration() / 1000
        self.playTime.setText(f"{position:.2f}/{duration:.2f}")
        self.playerSlider.setMaximum(int(duration))  # Convert duration to integer
        self.playerSlider.setValue(int(position))  # Ensure position is also integer


    def detect_violence(self, video_path):
        if self.model is None:
            print("Violence detection model not loaded.")
            return

        # Cancel any existing worker
        if self.violence_worker and self.violence_worker.isRunning():
            self.violence_worker.quit()
            self.violence_worker.wait()

        # Create new worker
        self.violence_worker = ViolenceDetectionWorker(self.model, video_path)
        self.violence_worker.detection_result.connect(self.handle_detection_result)
        self.violence_worker.start()

    def handle_detection_result(self, class_name, confidence):
        if class_name == 'Violence' and confidence > 0.5:
            QMessageBox.warning(self, "Violence Detected", "Violence has been detected in the video.")