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
from keras.models import load_model
from preview import Ui_preview
import mysql.connector as connector

IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64
SEQUENCE_LENGTH = 10
CLASSES_LIST = ["NonViolence", "Violence"]
model_path = 'C:/Users/WEP/Documents/AI/security/artificail-eye/violence3.keras'


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
    
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, video_path):
        super().__init__()
        self._run_flag = True
        self.video_path = video_path
        self.model = load_model(model_path)

    def run(self):
        video_reader = cv2.VideoCapture(self.video_path)
        frames_list = []

        while self._run_flag:
            success, cv_img = video_reader.read()
            if success:
                resized_frame = cv2.resize(cv_img, (IMAGE_HEIGHT, IMAGE_WIDTH))
                normalized_frame = resized_frame / 255
                frames_list.append(normalized_frame)
                if len(frames_list) == SEQUENCE_LENGTH:
                    predicted_labels_probabilities = self.model.predict(np.expand_dims(frames_list, axis=0))[0]
                    predicted_label = np.argmax(predicted_labels_probabilities)
                    predicted_class_name = CLASSES_LIST[predicted_label]
                    frames_list.pop(0)
                    if predicted_class_name == "Violence":
                        self.change_pixmap_signal.emit(cv_img)
                        break
            else:
                break
        video_reader.release()

    def stop(self):
        self._run_flag = False
        self.wait()


class Preview(QWidget, Ui_preview):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Initialize media player and video widget
        self.view.setLayout(QVBoxLayout())
        self.player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)
        self.view.layout().addWidget(self.video_widget)

        # Connect buttons and slider
        self.play.clicked.connect(self.toggle_play)
        self.pause.clicked.connect(self.toggle_play)
        self.playerSlider.sliderMoved.connect(self.set_position)
        self.cancelView.clicked.connect(self.clear_view)
        self.deviceVid.clicked.connect(self.start_video)
        # self.dataVid.clicked.connect(self.browse_database_video)
        

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


        # Set dialog for violence detection alert
        self.alert_dialog = QDialog(self)
        self.alert_dialog.setWindowTitle('Alert')
        self.alert_label = QLabel('Violence detected!', self.alert_dialog)
        self.alert_dialog.setLayout(QVBoxLayout())
        self.alert_dialog.layout().addWidget(self.alert_label)

        
        self.show()


    @pyqtSlot(np.ndarray)
    def update_alert(self, image):
        self.alert_dialog.show()

    def start_video(self):
        video_path, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.flv *.ts *.mts *.avi)")
        if video_path != '':
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
            self.player.play()
            self.thread = VideoThread(video_path)
            self.thread.change_pixmap_signal.connect(self.update_alert)
            self.thread.start()

    def stop_video(self):
        self.player.stop()
        if self.thread.isRunning():
            self.thread.stop()
    

        

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

    

    # def browse_database_video(self):
    #     cursor = self.connection.cursor()
    #     cursor.execute("SELECT id, VideoFile FROM video")
    #     videos = cursor.fetchall()

    #     dialog = VideoDialog(videos)
    #     if dialog.exec() == QDialog.Accepted:
    #         video_id = dialog.list_widget.currentItem().data(Qt.UserRole)
    #         cursor.execute("SELECT path FROM video WHERE id = %s", (video_id,))
    #         path = cursor.fetchone()[0]
    #         self.player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
    #         self.player.play()
    #         self.(path)

    def update_play_time(self):
        position = self.player.position() / 1000
        duration = self.player.duration() / 1000
        self.playTime.setText(f"{position:.2f}/{duration:.2f}")
        self.playerSlider.setMaximum(int(duration))  # Convert duration to integer
        self.playerSlider.setValue(int(position))  # Ensure position is also integer


    