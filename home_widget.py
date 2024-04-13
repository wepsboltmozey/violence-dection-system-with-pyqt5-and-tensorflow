from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import QSound

import cv2
import mysql.connector as connector
import re
import numpy as np
from keras.models import load_model
from datetime import datetime
from home import Ui_Home
from notify import Alert
from view import Preview




class EditProfileDialog(QDialog):
    user_details_updated = pyqtSignal(dict)

    def __init__(self, user_details):
        super().__init__()
        self.setWindowTitle("Edit Profile")
        self.setStyleSheet("background-color: rgb(13, 30, 64); color: rgb(255, 255, 255);")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.user_details = user_details

        # Add labels and corresponding fields for each user detail
        fields = [
            ("Username:", "username"),
            ("Contact:", "contact"),
            ("Email:", "email"),
            ("Work Code:", "workCode"),
            ("Sector of Work:", "workSector"),
            ("Photo:", "photo"),
            ("Password:", "password"),
            ("Confirm Password:", "confirmPassword")
        ]

        for label_text, field_name in fields:
            hbox = QHBoxLayout()
            label = QLabel(label_text)
            label.setStyleSheet("color: rgb(255, 255, 255);")
            hbox.addWidget(label)

            if field_name == "photo":
                # Corrected: Directly access the "photo" key without using .get("path", "")
                self.photo_edit = QLineEdit(self.user_details.get("photo", ""))
                browse_button = QPushButton("Browse Image")
                browse_button.setStyleSheet("background-color: rgb(48, 131, 59); color: white;")
                browse_button.clicked.connect(self.browse_image)
                hbox.addWidget(self.photo_edit)
                hbox.addWidget(browse_button)

            elif field_name == "workSector":
                # Create radio buttons for selecting sector of work
                self.security_radio = QRadioButton("Security")
                self.healthy_radio = QRadioButton("Healthy")
                self.security_radio.setStyleSheet("color: rgb(255, 255, 255);")
                self.healthy_radio.setStyleSheet("color: rgb(255, 255, 255);")
                hbox.addWidget(self.security_radio)
                hbox.addWidget(self.healthy_radio)    
                
                # Check the appropriate radio button based on user's current sector of work
                current_sector = self.user_details.get("workSector", "")
                if current_sector == "Security":
                    self.security_radio.setChecked(True)
                elif current_sector == "Healthy":
                    self.healthy_radio.setChecked(True)

            else:
                # For other fields, use QLineEdit
                edit_field = QLineEdit(str(self.user_details.get(field_name, "")))
                edit_field.setStyleSheet("border-radius: 15px;")
                hbox.addWidget(edit_field)
                
                # Assigning QLineEdit objects to attributes
                if field_name == "username":
                    self.username_edit = edit_field
                elif field_name == "contact":
                    self.contact_edit = edit_field
                elif field_name == "email":
                    self.email_edit = edit_field
                elif field_name == "workCode":
                    self.work_code_edit = edit_field
                elif field_name == "password":
                    self.password_edit = edit_field
                elif field_name == "confirmPassword":
                    self.confirm_password_edit = edit_field

            self.layout.addLayout(hbox)


        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setStyleSheet("background-color: rgb(48, 131, 59); color: white; padding: 10px 20px;")
        self.save_button.clicked.connect(self.save_profile)
        self.layout.addWidget(self.save_button)


    def browse_image(self):
        # Open a file dialog to browse for an image file
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "",
                                                    "Image Files (*.png *.jpg *.jpeg)", options=options)
        if file_path:
            self.photo_edit.setText(file_path)

    def save_profile(self):
        new_contact = self.contact_edit.text()
        new_email = self.email_edit.text()
        new_work_code = self.work_code_edit.text()
        new_sector_of_work = "Security" if self.security_radio.isChecked() else "Healthy"
        new_photo_path = self.photo_edit.text()
        new_password = self.password_edit.text()
        new_confirm_password = self.confirm_password_edit.text()

        self.user_details_updated.emit({
            "contact": new_contact,
            "email": new_email,
            "workCode": new_work_code,
            "workSector": new_sector_of_work,
            "photo": new_photo_path
        })

        # Validate the input fields as needed
        if new_password != new_confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return

        try:
            connection = connector.connect(
                host="localhost",
                user="root",
                password="",
                database="cameradb"
            )
            cursor = connection.cursor()

            # Update user's details in the database
            query = """
                UPDATE user
                SET email = %s, contact = %s, photo = %s, workSector = %s, password = %s
                WHERE workCode = %s
            """
            cursor.execute(query, (new_email, new_contact, new_photo_path, new_sector_of_work, new_password, new_work_code))
            connection.commit()

            # Fetch the updated user details from the database
            updated_user_details = {
                "contact": new_contact,
                "email": new_email,
                "workCode": new_work_code,
                "workSector": new_sector_of_work,
                "photo": new_photo_path
            }

            # Emit the signal with the updated user details
            self.user_details_updated.emit(updated_user_details)

            QMessageBox.information(self, "Success", "Profile updated successfully!")
            self.accept()

        except connector.Error as e:
            QMessageBox.critical(self, "Error", f"Failed to update profile: {e}")

        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()


# Constants
IMAGE_HEIGHT, IMAGE_WIDTH = 64, 64
SEQUENCE_LENGTH = 5
CLASSES_LIST = ["NonViolence", "Violence"]
CONFIDENCE_THRESHOLD = 0.90
VIDEO_OUTPUT_DIR = 'C:/Users/WEP/Documents/AI/security/artificail-eye/video/'
model_path = 'C:/Users/WEP/Documents/AI/security/artificail-eye/model/violence3.keras'


# VideoThread class
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    alert_signal = pyqtSignal()
    video_saved_signal = pyqtSignal(str)

    def __init__(self, model_path):
        super().__init__()
        self._run_flag = True
        self.model = load_model(model_path)
        self.video_writer = None
        self.violence_detected = False
        self.video_filename = ""

    def run(self):
        video_reader = cv2.VideoCapture(0)
        frames_list = []

        while self._run_flag:
            success, cv_img = video_reader.read()
            if success:
                self.change_pixmap_signal.emit(cv_img)
                if self.video_writer is not None:
                    self.video_writer.write(cv_img)  # Write frame to video file
                resized_frame = cv2.resize(cv_img, (IMAGE_HEIGHT, IMAGE_WIDTH))
                normalized_frame = resized_frame / 255
                frames_list.append(normalized_frame)
                if len(frames_list) == SEQUENCE_LENGTH:
                    predicted_labels_probabilities = self.model.predict(np.expand_dims(frames_list, axis=0))[0]
                    predicted_label = np.argmax(predicted_labels_probabilities)
                    predicted_class_name = CLASSES_LIST[predicted_label]
                    frames_list.pop(0)
                    if predicted_class_name == "Violence" and not self.violence_detected and predicted_labels_probabilities[predicted_label] >= CONFIDENCE_THRESHOLD:
                        self.violence_detected = True
                        self.alert_signal.emit()
            else:
                break

        video_reader.release()
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_saved_signal.emit(self.video_filename)

    def start_recording(self, filename):
        self.video_filename = filename
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(self.video_filename, fourcc, 20.0, (640, 480))

    def stop(self):
        self._run_flag = False
        self.wait()
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
            self.video_saved_signal.emit(self.video_filename)

# home widget manager 
class HomeWidget(QWidget, Ui_Home):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(1100,670)
        self.setWindowTitle("SMART CAMERA SYSTEM")
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.connection = connector.connect(
            host="localhost",
            user="root",
            password="",
            database="cameradb"
        )
        
    
        self.label_2.mousePressEvent = self.show_menu
        self.user_details = {}
        self.edit_profile_dialog = EditProfileDialog(self.user_details)
        self.edit_profile_dialog.user_details_updated.connect(self.update_user_details)
     

        # Connect button clicks to functions
        self.homebutton.clicked.connect(self.show_home_widget)
        self.preview.clicked.connect(self.show_preview_widget)
        self.alertN.clicked.connect(self.show_alerts_widget)
        
        
        

    
        self.preview = Preview()
        self.alerts = Alert()
       
       
      
       


        

        # set playing area 
        self.camera.setLayout(QVBoxLayout())
        self.videoView = QLabel()
        self.videoView.setScaledContents(True) 
        self.videoView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        self.camera.layout().addWidget(self.videoView)


        self.user_details = {}

        self.start.clicked.connect(self.start_video)
        self.stop.clicked.connect(self.stop_video)


        # Set dialog for violence detection alert
        self.alert_dialog = QDialog(self)
        self.alert_dialog.setWindowTitle('Alert')
        self.alert_label = QLabel('Violence detected!', self.alert_dialog)
        self.alert_dialog.setLayout(QVBoxLayout())
        self.alert_dialog.layout().addWidget(self.alert_label)

        
        

    
    @pyqtSlot(np.ndarray)
    def update_camera_label(self, cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.videoView.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    @pyqtSlot()
    def update_alert(self):
        # Play an alarm sound when violence is detected
        self.alert_sound = QSound('C:/Users/WEP/Documents/AI/security/artificail-eye/resources/Alarm.wav')
        self.alert_sound.play()
        self.alert_dialog.show()
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO notification (datetime, notification, file) VALUES (%s, %s, %s)",
                       (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'Violence detected', self.video_filename))
        self.connection.commit()
        cursor.close()


    def start_video(self):
        self.start_time = datetime.now()
        self.startTime.setText(self.start_time.strftime('%H:%M:%S'))
        self.date.setText(self.start_time.strftime('%Y-%m-%d'))
        self.timer.start(1000)

        # # Generate a unique filename for each video recording
        self.video_filename = f"{VIDEO_OUTPUT_DIR}{self.start_time.strftime('%Y%m%d_%H%M%S')}.mp4"
        # self.video_thread.start_recording(self.video_filename)

        self.thread = VideoThread(model_path)
        self.thread.change_pixmap_signal.connect(self.update_camera_label)
        self.thread.alert_signal.connect(self.update_alert)
        self.thread.video_saved_signal.connect(self.on_video_saved)
        self.thread.start()
        self.thread.start_recording(self.video_filename)

    def stop_video(self):
        if self.thread.isRunning():
            self.thread.stop()
        self.timer.stop()
        self.save_video_data()

        # Check if an alert was triggered and save the alert information with the video
        if self.thread.violence_detected:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO notification (datetime, notification, file) VALUES (%s, %s, %s)",
                        (self.start_time.strftime('%Y-%m-%d %H:%M:%S'), 'Violence detected', self.video_filename))
            self.connection.commit()
            cursor.close()

    def on_video_saved(self, filename):
        print(f"Video saved: {filename}")

    def update_time(self):
        elapsed_time = datetime.now() - self.start_time
        self.timeOn.setText(str(elapsed_time).split('.')[0])

    def save_video_data(self):
        cursor = self.connection.cursor()
        elapsed_time = datetime.now() - self.start_time
        # Save the video file path to the database
        cursor.execute("INSERT INTO video (starttime, date, timetaken, videofile) VALUES (%s, %s, %s, %s)",
                       (self.start_time.strftime('%Y-%m-%d %H:%M:%S'), self.start_time.date(), str(elapsed_time).split('.')[0], self.video_filename))
        self.connection.commit()
        cursor.close()
    

    def set_user_details(self, user_details):
        self.user_details = user_details
        self.update_user_profile()

    def update_user_profile(self):
        # Display user's photo (profile picture) in label_2
        user_photo_path = self.user_details.get("photo")
        if user_photo_path:
            user_photo = QPixmap(user_photo_path)
            rounded_photo = self.create_rounded_pixmap(user_photo)
            self.label_2.setPixmap(rounded_photo)


    def show_home_widget(self):
        self.mainWidget.show()
        self.preview.hide()
        self.alerts.hide()
        
        

    def show_preview_widget(self):
        self.preview.setParent(self.mainWidget.parent())
        self.mainWidget.hide()
        self.alerts.hide()
        self.preview.setGeometry(self.mainWidget.geometry())
        self.preview.show()

    def show_alerts_widget(self):
        self.alerts.setParent(self.mainWidget.parent())
        self.mainWidget.hide()
        self.preview.hide()
        self.alerts.setGeometry(self.mainWidget.geometry())
        self.alerts.show()    
   

    def show_menu(self, event):
        menu = QMenu(self.label_2)

        # Only show Edit Profile if user is logged in
        if self.user_details:
            edit_profile_action = QAction("Edit Profile", self)
            edit_profile_action.triggered.connect(self.edit_profile)
            menu.addAction(edit_profile_action)

        sign_out_action = QAction("Sign Out", self)
        sign_out_action.triggered.connect(self.sign_out)
        menu.addAction(sign_out_action)

        # Show the menu at the cursor position
        menu.exec_(self.label_2.mapToGlobal(event.pos()))

    def edit_profile(self):
        # Open Edit Profile dialog with user details if user is logged in
        if self.user_details:
            edit_profile_dialog = EditProfileDialog(self.user_details)
            edit_profile_dialog.exec_()
        else:
            QMessageBox.warning(self, "Error", "User not logged in!")


    def sign_out(self):
        self.hide()

    def create_rounded_pixmap(self, pixmap):
        # Create a round mask
        mask = QBitmap(pixmap.size())
        mask.fill(Qt.white)
        painter = QPainter(mask)
        painter.setBrush(Qt.black)
        painter.drawEllipse(0, 0, pixmap.width(), pixmap.height())
        painter.end()

        # Apply the mask to the pixmap
        rounded_pixmap = pixmap.copy()
        rounded_pixmap.setMask(mask)
        return rounded_pixmap

    
       

    def update_user_details(self, updated_user_details):
       
        # Update fields in the edit form
        self.edit_profile_dialog.contact_edit.setText(updated_user_details["contact"])
        self.edit_profile_dialog.email_edit.setText(updated_user_details["email"])
        self.edit_profile_dialog.work_code_edit.setText(updated_user_details["workCode"])
        # Update radio buttons in the edit form
        if updated_user_details["workSector"] == "Security":
            self.edit_profile_dialog.security_radio.setChecked(True)
        else:
            self.edit_profile_dialog.healthy_radio.setChecked(True)
        # Update photo edit field in the edit form
        self.edit_profile_dialog.photo_edit.setText(updated_user_details["photo"])     
