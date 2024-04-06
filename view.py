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
from preview import Ui_preview  # Assuming Ui_preview is a file in your project containing UI definitions
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
        self.draw.clicked.connect(self.ImageDraw)

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

        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self.video_widget)
        self.rubberBand.setStyleSheet("border: 2px solid blue; background-color: rgba(0, 0, 255, 50);")
        self.origin = QPoint()  

        # Load violence detection model
        self.model_loader_thread = ModelLoaderThread()
        self.model_loader_thread.model_loaded.connect(self.on_model_loaded)
        self.model = None
        self.model_loader_thread.start()

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

    @pyqtSlot()
    def ImageDraw(self):
        # Pause the video
        self.player.pause()

        # Show the QRubberBand
        self.rubberBand.show()

        # Connect mouse events to handle drawing of the rectangle
        self.video_widget.mousePressEvent = self.mousePress
        self.video_widget.mouseMoveEvent = self.mouseMove
        self.video_widget.mouseReleaseEvent = self.mouseRelease

    def mousePress(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()

    def mouseMove(self, event):
        if not self.origin.isNull():
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseRelease(self, event):
        # Hide the QRubberBand
        self.rubberBand.hide()

        # Get the selected area
        selected_area = self.rubberBand.geometry()

        # Get the coordinates of the video content area
        video_geometry = self.video_widget.geometry()

        # Intersect the selected area with the video content area
        selected_area.intersected(video_geometry)

        # Crop the frame to the selected area
        cropped_frame = self.video_widget.grab(selected_area)

        # Convert the QPixmap to a QImage
        cropped_image = cropped_frame.toImage()

        # Convert the QImage to a QPixmap
        cropped_pixmap = QPixmap.fromImage(cropped_image)

        # Show the cropped image in a dialog for the user to name and save
        name, ok = QInputDialog.getText(self, 'Save Image', 'Enter image name:')
        if ok and name:
            # Save the image to the database
            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)
            cropped_pixmap.save(buffer, "PNG")  # Save the pixmap as PNG format
            img_data = buffer.data().toBase64().data()
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO picture (name, data) VALUES (%s, %s)", (name, img_data))
            self.connection.commit()
            QMessageBox.information(self, "Image Saved", "Image has been saved to the database.")

        # Resume playing the video
        self.player.play()

    def detect_violence(self, video_path):
        if self.model is None:
            print("Violence detection model not loaded.")
            return

        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames_list = []

        for _ in range(frame_count):
            ret, frame = cap.read()
            if not ret:
                break

            # Resize frame to match the expected input size of the model
            resized_frame = cv2.resize(frame, (64, 64))
            # Convert frame to RGB (if not already)
            if resized_frame.shape[2] == 1:
                resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_GRAY2RGB)
            elif resized_frame.shape[2] == 4:
                resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGRA2RGB)
            # Normalize the resized frame
            normalized_frame = resized_frame.astype(np.float32) / 255.0
            # Append normalized frame to the list of frames
            frames_list.append(normalized_frame)

        cap.release()

        # Stack frames along the first axis to create a batch
        frames_batch = np.stack(frames_list, axis=0)

        # Expand dimensions to match expected input shape
        frames_batch = np.expand_dims(frames_batch, axis=0)

        # Perform violence prediction using your model
        try:
            prediction = self.model(frames_batch)
            predicted_class_name, confidence = self.process_prediction(prediction)
            if predicted_class_name == 'Violence' and confidence > 0.5:
                QMessageBox.warning(self, "Violence Detected", "Violence has been detected in the video.")
        except Exception as e:
            print(f"Error predicting violence: {e}")

    def process_prediction(self, prediction):
        # Assuming your prediction method returns a tuple (class_index, confidence)
        class_index = np.argmax(prediction)
        class_name = CLASSES_LIST[class_index]
        confidence = prediction[0][class_index]
        return class_name, confidence
