from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import cv2
import mysql.connector as connector
import re
import numpy as np
import tensorflow as tf
import datetime

from facial_recognition import Facial
from home import Ui_Home
from model_file import ModelLoaderThread
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


# Constants for video processing and model
IMAGE_HEIGHT = 224
IMAGE_WIDTH = 224
CLASSES_LIST = ['Non-Violence', 'Violence']

class CameraThread(QThread):
    frame_processed = pyqtSignal(np.ndarray)
    update_start_time = pyqtSignal(str)
    update_elapsed_time = pyqtSignal(str)
    update_date = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_capturing = False
        self.start_time = None

    def run(self):
        self.cap = cv2.VideoCapture(0)
        self.is_capturing = True
        self.start_time = datetime.datetime.now()
        self.update_start_time.emit(self.start_time.strftime("%H:%M:%S")) 
        while self.is_capturing:
            ret, frame = self.cap.read()
            if not ret:
                break
            resized_frame = cv2.resize(frame, (IMAGE_WIDTH, IMAGE_HEIGHT))
            self.frame_processed.emit(resized_frame)
            elapsed_time = datetime.datetime.now() - self.start_time
            self.update_elapsed_time.emit(str(elapsed_time))
            current_date = datetime.datetime.now().strftime("%m/%d/%y")
            self.update_date.emit(current_date)
            self.msleep(5)

    def stop_capture(self):
        self.is_capturing = False
        self.cap.release()

    def get_start_time(self):
        return self.start_time

    def get_elapsed_time(self):
        return datetime.datetime.now() - self.start_time if self.start_time else None



class HomeWidget(QWidget, Ui_Home):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("INTELLIGENT CAMERA SYSTEM")
        
    
        self.label_2.mousePressEvent = self.show_menu
        self.user_details = {}
        self.edit_profile_dialog = EditProfileDialog(self.user_details)
        self.edit_profile_dialog.user_details_updated.connect(self.update_user_details)
     
        self.start.clicked.connect(self.start_capture_and_detection)
        self.stop.clicked.connect(self.stop_capture_and_detection)


        # Connect button clicks to functions
        self.homebutton.clicked.connect(self.show_home_widget)
        self.preview.clicked.connect(self.show_preview_widget)
        self.facialbutton.clicked.connect(self.show_facial_widget)
        

    
        self.preview = Preview()
        self.facial = Facial()
      
       


        # Video processing variables
        self.camera_thread = CameraThread()
        self.model = None  # Initialize model as None
        self.model_loader_thread = ModelLoaderThread()

        # Connect signals
        self.camera_thread.frame_processed.connect(self.process_frame)
        self.model_loader_thread.model_loaded.connect(self.on_model_loaded)
        self.camera_thread.update_start_time.connect(self.startTime.setText)
        self.camera_thread.update_elapsed_time.connect(self.timeOn.setText)
        self.camera_thread.update_date.connect(self.date.setText)

        # Variables for processed frame and prediction
        self.processed_frame = None
        self.predicted_class_name = ''


        # set playing area 
        self.camera.setLayout(QVBoxLayout())
        self.videoView = QLabel()
        self.camera.layout().addWidget(self.videoView, stretch=1)

        self.user_details = {}

      

    def update_start_time_label(self, start_time):
        self.startTime.setText(start_time)

    def update_elapsed_time_label(self, elapsed_time):
        self.timeOn.setText(elapsed_time)

    def update_date_label(self, current_date):
        self.date.setText(current_date)    

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
        # You can update other user details here if needed

    def start_capture_and_detection(self):
        self.start.setEnabled(False)
        self.stop.setEnabled(True)
        self.camera_thread.start()

    def stop_capture_and_detection(self):
        self.camera_thread.stop_capture()
        self.start.setEnabled(True)
        self.stop.setEnabled(False)

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
            self.videoView.setPixmap(pixmap)
            self.videoView.setScaledContents(True)

    def paintEvent(self, event):
        if self.predicted_class_name:
            painter = QPainter(self)
            painter.setPen(Qt.red)
            painter.setFont(QFont('Arial', 20))
            painter.drawText(20, 40, f'Predicted: {self.predicted_class_name}')

    def closeEvent(self, event):
        self.camera_thread.quit()
        self.model_loader_thread.quit()    



    # end of detection 


    def show_home_widget(self):
        self.mainWidget.show()
        self.preview.hide()
        self.facial.hide()
        

    def show_preview_widget(self):
        self.preview.setParent(self.mainWidget.parent())
        self.mainWidget.hide()
        self.facial.hide()
        # self.edit.hide()
        self.preview.setGeometry(self.mainWidget.geometry())
        self.preview.show()
        

    def show_facial_widget(self):
        self.facial.setParent(self.mainWidget.parent())
        self.mainWidget.hide()
        self.preview.hide()
        # self.edit.hide()
        self.facial.setGeometry(self.mainWidget.geometry())
        self.facial.show()

   

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
        self.camera_thread.stop_capture()
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
