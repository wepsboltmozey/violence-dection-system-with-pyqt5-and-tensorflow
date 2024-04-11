# import sys
# import cv2
# import numpy as np
# from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QDialog
# from PyQt5.QtCore import *
# from PyQt5.QtGui import QImage, QPixmap
# from keras.models import load_model
# from datetime import datetime
# import mysql.connector as connector

# # Constants
# IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64
# SEQUENCE_LENGTH = 10
# CLASSES_LIST = ["NonViolence", "Violence"]
# model_path = 'C:/Users/WEP/Documents/AI/security/artificail-eye/violence3.keras'
# video_output_path = 'C:/Users/WEP/Documents/AI/security/artificail-eye/sreenshot/output.mp4'

# class VideoThread(QThread):
#     change_pixmap_signal = pyqtSignal(np.ndarray)
#     alert_signal = pyqtSignal()

#     def __init__(self):
#         super().__init__()
#         self._run_flag = True
#         self.model = load_model(model_path)
#         self.video_writer = None
#         self.violence_detected = False

#     def run(self):
#         video_reader = cv2.VideoCapture(0)
#         frames_list = []
#         ret, frame = video_reader.read()
#         if ret:
#             height, width, channels = frame.shape
#             self.video_writer = cv2.VideoWriter(video_output_path, cv2.VideoWriter_fourcc(*'mp4v'), 20, (width, height))

#         while self._run_flag:
#             success, cv_img = video_reader.read()
#             if success:
#                 self.change_pixmap_signal.emit(cv_img)
#                 self.video_writer.write(cv_img)  # Write frame to video file
#                 resized_frame = cv2.resize(cv_img, (IMAGE_HEIGHT, IMAGE_WIDTH))
#                 normalized_frame = resized_frame / 255
#                 frames_list.append(normalized_frame)
#                 if len(frames_list) == SEQUENCE_LENGTH:
#                     predicted_labels_probabilities = self.model.predict(np.expand_dims(frames_list, axis=0))[0]
#                     predicted_label = np.argmax(predicted_labels_probabilities)
#                     predicted_class_name = CLASSES_LIST[predicted_label]
#                     frames_list.pop(0)
#                     if predicted_class_name == "Violence" and not self.violence_detected:
#                         self.violence_detected = True
#                         self.alert_signal.emit()
#             else:
#                 break
#         video_reader.release()
#         self.video_writer.release()

#     def stop(self):
#         self._run_flag = False
#         self.wait()

# class App(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Violence Detection")
#         self.setGeometry(100, 100, 800, 600)
#         self.start_time = None
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.update_time)
#         self.connection = connector.connect(
#             host="localhost",
#             user="root",
#             password="",
#             database="cameradb"
#         )

#         self.v_layout = QVBoxLayout()
#         self.setLayout(self.v_layout)

#         # Create a label to display the camera feed
#         self.camera_label = QLabel()
#         self.v_layout.addWidget(self.camera_label)

#         # Create buttons
#         self.start_button = QPushButton('Start')
#         self.start_button.clicked.connect(self.start_video)
#         self.v_layout.addWidget(self.start_button)

#         self.stop_button = QPushButton('Stop')
#         self.stop_button.clicked.connect(self.stop_video)
#         self.v_layout.addWidget(self.stop_button)

#         # Create labels for start time, date, and elapsed time
#         self.start_time_label = QLabel('Start Time: ')
#         self.date_label = QLabel('Date: ')
#         self.elapsed_time_label = QLabel('Elapsed Time: 00:00:00')
#         self.v_layout.addWidget(self.start_time_label)
#         self.v_layout.addWidget(self.date_label)
#         self.v_layout.addWidget(self.elapsed_time_label)

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
#     def update_camera_label(self, cv_img):
#         qt_img = self.convert_cv_qt(cv_img)
#         self.camera_label.setPixmap(qt_img)

#     def convert_cv_qt(self, cv_img):
#         rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
#         h, w, ch = rgb_image.shape
#         bytes_per_line = ch * w
#         convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
#         p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
#         return QPixmap.fromImage(p)

#     @pyqtSlot()
#     def update_alert(self):
#         self.alert_dialog.show()

#     def start_video(self):
#         self.start_time = datetime.now()
#         self.start_time_label.setText('Start Time: ' + self.start_time.strftime('%H:%M:%S'))
#         self.date_label.setText('Date: ' + self.start_time.strftime('%Y-%m-%d'))
#         self.timer.start(1000)  # Update the elapsed time every second

#         self.thread = VideoThread()
#         self.thread.change_pixmap_signal.connect(self.update_camera_label)
#         self.thread.alert_signal.connect(self.update_alert)
#         self.thread.start()

#     def stop_video(self):
#         if self.thread.isRunning():
#             self.thread.stop()
#         self.timer.stop()
#         self.save_video_data()

#     def update_time(self):
#         elapsed_time = datetime.now() - self.start_time
#         self.elapsed_time_label.setText('Elapsed Time: ' + str(elapsed_time).split('.')[0])

#     def save_video_data(self):
#         cursor = self.connection.cursor()
#         elapsed_time = datetime.now() - self.start_time
#         cursor.execute("INSERT INTO video (starttime, date, timetaken, videofile) VALUES (%s, %s, %s, %s)",
#                        (self.start_time, self.start_time.date(), str(elapsed_time).split('.')[0], video_output_path))
#         self.connection.commit()
#         cursor.close()

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = App()
#     sys.exit(app.exec_())
