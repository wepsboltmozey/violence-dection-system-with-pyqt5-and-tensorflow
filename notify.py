from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtMultimedia import *
import mysql.connector as connector
from PyQt5 import QtCore, QtGui, QtWidgets

from alerts import Ui_Form

class VideoDialog(QDialog):
    def __init__(self, file_path, parent=None):
        super(VideoDialog, self).__init__(parent)
        self.setWindowTitle("Video Preview")
        self.setFixedSize(700, 500)  # Adjust size as needed
        self.setStyleSheet("background-color: rgb(13, 30, 64); color: rgb(255, 255, 255);")

        self.file_path = file_path

        # Create a QMediaPlayer
        self.player = QMediaPlayer(self)

        # Create a QVideoWidget
        self.video_widget = QVideoWidget(self)
        self.video_widget.setFixedSize(650, 450)
        self.player.setVideoOutput(self.video_widget)
        

        # Create a QSlider for video playback control
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)  # Range set to 0 initially
        self.slider.sliderMoved.connect(self.set_position)  # Connect slider to set_position function

        # Create a QLabel to display current video time
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignCenter)

        # Set up the layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.video_widget)
        layout.addWidget(self.slider)
        layout.addWidget(self.time_label)
        self.setLayout(layout)

        # Play the video
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.file_path)))
        self.player.durationChanged.connect(self.set_duration)
        self.player.positionChanged.connect(self.update_position)
        self.player.play()

    def set_duration(self, duration):
        self.slider.setRange(0, duration // 1000)  # Set slider range based on video duration in seconds

    def update_position(self, position):
        if position >= 0:
            self.slider.setValue(position // 1000)  # Set slider value based on current position in seconds
            self.update_time_label(position)

    def set_position(self, position):
        self.player.setPosition(position * 1000)  # Set video playback position in milliseconds

    def update_time_label(self, position):
        duration = self.player.duration()
        formatted_time = QTime(0, (position // 1000) // 60, (position // 1000) % 60)
        formatted_duration = QTime(0, (duration // 1000) // 60, (duration // 1000) % 60)
        self.time_label.setText(f"{formatted_time.toString('mm:ss')} / {formatted_duration.toString('mm:ss')}")

    def closeEvent(self, event):
        self.player.stop()  # Stop video playback when closing the dialog
        super(VideoDialog, self).closeEvent(event)



class Alert(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.connection = connector.connect(
            host="localhost",
            user="root",
            password="",
            database="cameradb"
        )
        
        self.refresh.mousePressEvent = self.update_alerts
        self.update_alerts()


    def update_alerts(self, event=None):
        if self.scrollAreaWidgetContents.layout() is None:
            self.scrollAreaWidgetContents.setLayout(QVBoxLayout())

        layout = self.scrollAreaWidgetContents.layout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        if layout:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # Fetch and display alerts from the database
        cursor = self.connection.cursor()
        cursor.execute("SELECT datetime, notification, file FROM notification ORDER BY datetime DESC")
        alerts = cursor.fetchall()
        cursor.close()

        for datetime, notification, file in alerts:
            notify_widget = self.create_notify_widget(notification, datetime, file)
            self.scrollAreaWidgetContents.layout().addWidget(notify_widget)
    
    def create_notify_widget(self, notification, datetime, file):
        # Create the main widget and set its style
        notify_widget = QWidget()
        notify_widget.setFixedSize(670, 100) 
        notify_widget.setStyleSheet("""
            QWidget {
                border-radius: 20px;
                background-color: rgb(13, 30, 64);
                color: white;
                margin: 10px;
            }
        """)

        # Create a layout for the notify_widget
        notify_layout = QHBoxLayout()
        notify_widget.setLayout(notify_layout)

        # Create the time label and add it to the layout
        time_label = QLabel(str(datetime))
        time_label.setStyleSheet("margin-left: 10px; margin-top: 10px; padding:10px")
        notify_layout.addWidget(time_label, alignment=Qt.AlignTop | Qt.AlignLeft)

        # Create the notification label and add it to the layout
        notification_label = QLabel(notification)
        notification_label.setStyleSheet("margin: 10px;")
        notify_layout.addWidget(notification_label, alignment=Qt.AlignCenter)

        # Create the preview button and add it to the layout
        preview_button = QPushButton("Preview")
        preview_button.setStyleSheet("margin-right: 10px; margin-bottom: 10px;padding: 10px")
        preview_button.clicked.connect(lambda: self.preview_video(file))
        
        
        # Create the preview button and add it to the layout
        preview_button = QPushButton("Preview")
        preview_button.setStyleSheet("""
            QPushButton {
                font: 8pt "Segoe UI";
                background-color: rgb(48, 131, 59);
                border-radius: 15px;
                color: white;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #0D1E40;
                border-radius: 15px;
                color: white;
            }
        """)
        preview_button.clicked.connect(lambda: self.preview_video(file))
        
        # Create a horizontal layout to properly align the preview button to the right
        button_layout = QHBoxLayout()
        button_layout.addWidget(preview_button, alignment=Qt.AlignCenter)
        
        # Add the button layout to the main notify_layout
        notify_layout.addLayout(button_layout)
        return notify_widget

    def preview_video(self, file):
        # Create and show the video dialog
        self.video_dialog = VideoDialog(file, self)
        self.video_dialog.show()