from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import mysql.connector as connector
from PyQt5 import QtCore, QtGui, QtWidgets

from alerts import Ui_Form

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
        self.update_alerts()

        self.refresh.mousePressEvent = self.update_alerts

    def update_alerts(self, event=None):
        if self.scrollAreaWidgetContents.layout() is None:
            self.scrollAreaWidgetContents.setLayout(QVBoxLayout())

        layout = self.scrollAreaWidgetContents.layout()
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        for i in reversed(range(layout.count())): 
            layout.itemAt(i).widget().deleteLater()

        cursor = self.connection.cursor()
        cursor.execute("SELECT datetime, notification, file FROM notification ORDER BY datetime DESC")
        alerts = cursor.fetchall()
        cursor.close()

        for alert in alerts:
            datetime, notification, file = alert
            notify = self.create_notify_widget(notification, datetime, file)
            layout.addWidget(notify)

    
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
        # Implement the logic to preview the video
        pass
