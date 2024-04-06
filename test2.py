import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2
import datetime


class CameraThread(QThread):
    frameCaptured = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.is_running = False

    def run(self):
        self.is_running = True
        cap = cv2.VideoCapture(0)
        start_time = datetime.datetime.now()

        while self.is_running:
            ret, frame = cap.read()
            if ret:
                self.frameCaptured.emit(frame)

        end_time = datetime.datetime.now()
        time_taken = end_time - start_time
        self.is_running = False
        cap.release()
        cv2.destroyAllWindows()


class VideoRecorderApp(QWidget):
    def __init__(self):
        super().__init__()

        self.camera_thread = CameraThread()
        self.camera_thread.frameCaptured.connect(self.update_frame)
        self.is_recording = False

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Video Recorder")

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)

        self.datetime_label = QLabel(self)
        self.starttime_label = QLabel(self)
        self.time_taken_label = QLabel(self)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.cancel_button = QPushButton("Cancel")

        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.cancel_button.clicked.connect(self.cancel_recording)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.cancel_button)

        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("Date & Time: "))
        info_layout.addWidget(self.datetime_label)
        info_layout.addWidget(QLabel("Start Time: "))
        info_layout.addWidget(self.starttime_label)
        info_layout.addWidget(QLabel("Time Taken: "))
        info_layout.addWidget(self.time_taken_label)

        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addLayout(info_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def start_recording(self):
        if not self.is_recording:
            self.camera_thread.start()
            self.is_recording = True
            self.starttime_label.setText(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

    def stop_recording(self):
        if self.is_recording:
            self.camera_thread.is_running = False
            self.is_recording = False
            self.stop_button.setEnabled(False)
            self.start_button.setEnabled(True)
            self.time_taken_label.setText(str(datetime.datetime.now() - datetime.datetime.strptime(self.starttime_label.text(), "%Y-%m-%d %H:%M:%S")))

    def cancel_recording(self):
        if self.is_recording:
            self.camera_thread.is_running = False
            self.is_recording = False
        self.close()

    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(img))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoRecorderApp()
    window.show()
    sys.exit(app.exec_())
