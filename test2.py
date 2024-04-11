# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QWidget, QDialog
# from PyQt5.QtCore import *
# from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
# from PyQt5.QtMultimediaWidgets import QVideoWidget
# import cv2
# import numpy as np
# from keras.models import load_model

# # Constants
# IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64
# SEQUENCE_LENGTH = 10
# CLASSES_LIST = ["NonViolence", "Violence"]
# model_path = 'C:/Users/WEP/Documents/AI/security/artificail-eye/violence3.keras'

# class VideoThread(QThread):
#     change_pixmap_signal = pyqtSignal(np.ndarray)

#     def __init__(self, video_path):
#         super().__init__()
#         self._run_flag = True
#         self.video_path = video_path
#         self.model = load_model(model_path)

#     def run(self):
#         video_reader = cv2.VideoCapture(self.video_path)
#         frames_list = []

#         while self._run_flag:
#             success, cv_img = video_reader.read()
#             if success:
#                 resized_frame = cv2.resize(cv_img, (IMAGE_HEIGHT, IMAGE_WIDTH))
#                 normalized_frame = resized_frame / 255
#                 frames_list.append(normalized_frame)
#                 if len(frames_list) == SEQUENCE_LENGTH:
#                     predicted_labels_probabilities = self.model.predict(np.expand_dims(frames_list, axis=0))[0]
#                     predicted_label = np.argmax(predicted_labels_probabilities)
#                     predicted_class_name = CLASSES_LIST[predicted_label]
#                     frames_list.pop(0)
#                     if predicted_class_name == "Violence":
#                         self.change_pixmap_signal.emit(cv_img)
#                         break
#             else:
#                 break
#         video_reader.release()

#     def stop(self):
#         self._run_flag = False
#         self.wait()

# class App(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Violence Detection")
#         self.setGeometry(100, 100, 800, 600)
#         self.v_layout = QVBoxLayout()
#         self.setLayout(self.v_layout)

#         # Create a video player widget
#         self.video_widget = QVideoWidget()
#         self.v_layout.addWidget(self.video_widget)

#         # Create a media player object
#         self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
#         self.media_player.setVideoOutput(self.video_widget)

#         # Create buttons
#         self.start_button = QPushButton('Start')
#         self.start_button.clicked.connect(self.start_video)
#         self.v_layout.addWidget(self.start_button)

#         self.stop_button = QPushButton('Stop')
#         self.stop_button.clicked.connect(self.stop_video)
#         self.v_layout.addWidget(self.stop_button)

#         # Set dialog for violence detection alert
#         self.alert_dialog = QDialog(self)
#         self.alert_dialog.setWindowTitle('Alert')
#         self.alert_label = QLabel('Violence detected!', self.alert_dialog)
#         self.alert_dialog.setLayout(QVBoxLayout())
#         self.alert_dialog.layout().addWidget(self.alert_label)

#         # Set central widget
#         self.central_widget = QWidget()
#         self.central_widget.setLayout(self.v_layout)
#         self.setCentralWidget(self.central_widget)

#         self.show()

#     @pyqtSlot(np.ndarray)
#     def update_alert(self, image):
#         self.alert_dialog.show()

#     def start_video(self):
#         video_path, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.flv *.ts *.mts *.avi)")
#         if video_path != '':
#             self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
#             self.media_player.play()
#             self.thread = VideoThread(video_path)
#             self.thread.change_pixmap_signal.connect(self.update_alert)
#             self.thread.start()

#     def stop_video(self):
#         self.media_player.stop()
#         if self.thread.isRunning():
#             self.thread.stop()

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = App()
#     sys.exit(app.exec_())
