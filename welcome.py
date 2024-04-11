from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# from facial_recognition import Facial
from home_widget import HomeWidget

from welcome_widget import Ui_welcome

from login import Ui_login
from register import Ui_Register
import mysql.connector as connector
import re




class Register(QWidget, Ui_Register):
    registration_successful = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Register")
        self.submit.clicked.connect(self.register_user)
        self.cancel.clicked.connect(self.close)
        self.browse.clicked.connect(self.browse_image)
        self.password.setEchoMode(QLineEdit.Password)
        self.password_2.setEchoMode(QLineEdit.Password)

    def browse_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Image", "",
                                                  "Image Files (*.png *.jpg *.jpeg)", options=options)
        if fileName:
            self.browse.setText(fileName)

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email)

    def validate_phone(self, phone):
        pattern = r'^[0-9]{10}$'
        return re.match(pattern, phone)

    def validate_password(self, password):
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        return True

    def validate_work_code(self, work_code):
        pattern = r'^\d{2,}$'  # At least two digits
        return re.match(pattern, work_code)

    def register_user(self):
        username = self.username.text()
        password = self.password.text()
        email = self.email.text()
        workCode = self.work_code.text()
        contact = self.contact.text()
        photo = self.browse.text()
        workSector = "Security" if self.security.isChecked() else "Healthy"

        if not all([workCode, username, password, email, contact, photo]):
            QMessageBox.warning(self, "Error", "All fields are required")
            return

        if not self.validate_email(email):
            QMessageBox.warning(self, "Error", "Invalid email address")
            return

        if not self.validate_phone(contact):
            QMessageBox.warning(self, "Error", "Invalid phone number")
            return

        if not self.validate_password(password):
            QMessageBox.warning(self, "Error", "Password should be at least 8 characters long, "
                                                "contain at least one uppercase letter, one lowercase letter, "
                                                "and one digit")
            return

        if password != self.password_2.text():
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return

        if not self.validate_work_code(workCode):
            QMessageBox.warning(self, "Error", "Invalid work code. It should be at least two digits")
            return

        try:
            connection = connector.connect(
                host="localhost",
                user="root",
                password="",
                database="cameradb"
            )
            cursor = connection.cursor()

            query = "INSERT INTO user (workCode, username, contact, email, photo, workSector, password) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (workCode, username, contact, email, photo, workSector, password))
            connection.commit()

            QMessageBox.information(self, "Success", "Registration successful")
            self.close()  # Close registration window
            self.registration_successful.emit()  # Emit signal

        except connector.Error as e:
            QMessageBox.critical(self, "Error", f"Failed to register user: {e}")

        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

class Login(QWidget, Ui_login):
    # Define a signal
    login_successful = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Login")
        self.regbutton.clicked.connect(self.show_register_widget)
        self.loginbutton.clicked.connect(self.login_user)
        self.password.setEchoMode(QLineEdit.Password)

    def show_register_widget(self):
        self.register_widget = Register()
        self.register_widget.show()
        self.hide()

    def login_user(self):
        username = self.username.text()
        password = self.password.text()

        if not all([username, password]):
            QMessageBox.warning(self, "Error", "Username and password are required")
            return

        try:
            connection = connector.connect(
                host="localhost",
                user="root",
                password="",
                database="cameradb"
            )
            cursor = connection.cursor()

            query = "SELECT * FROM user WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user_details = cursor.fetchone()

            if user_details:
                column_names = [column[0] for column in cursor.description]
                user_details_dict = dict(zip(column_names, user_details))
                user_photo_path = user_details_dict.get("photo")
                QMessageBox.information(self, "Success", "Login successful")
                # Emit the signal with the user's details
                self.login_successful.emit(user_details_dict)
            else:
                QMessageBox.warning(self, "Error", "Invalid username or password")

        except connector.Error as e:
            QMessageBox.critical(self, "Error", f"Failed to login: {e}")

        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

        self.hide()


class Welcome(QWidget, Ui_welcome):
    login_successful = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Welcome")
        self.register_widget = Register()
        self.register_widget.registration_successful.connect(self.show_login_widget)

        self.login_widget = Login()
        self.login_widget.login_successful.connect(self.login_success_handler)

       
        self.Home = HomeWidget()

        self.login.clicked.connect(self.show_login_widget)

    def show_login_widget(self):
        self.login_widget.show()

    def login_success_handler(self, user_details_dict):
        self.Home.set_user_details(user_details_dict)
        self.Home.show()
        self.hide()