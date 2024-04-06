import numpy as np
from facial import Ui_facial
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QMessageBox, QPushButton, QVBoxLayout, QListWidget, QListWidgetItem, QDialog
import cv2
import face_recognition
import mysql.connector as connector

class ImageSelectionDialog(QDialog):
    def __init__(self, filenames):
        super().__init__()
        self.setWindowTitle("Select Image")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setStyleSheet("background-color: rgb(13, 30, 64); color: white;")

        # List widget to display image filenames
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background-color: rgb(255, 255, 255); color: black;")
        self.layout.addWidget(self.list_widget)

        # Add filenames to list widget
        for filename in filenames:
            item = QListWidgetItem(filename)
            self.list_widget.addItem(item)

        # Connect signal for item selection
        self.list_widget.itemDoubleClicked.connect(self.accept)

    def selected_filename(self):
        return self.list_widget.currentItem().text() if self.list_widget.currentItem() else None

class Facial(QWidget, Ui_facial):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Connect button signals
        self.browse.clicked.connect(self.select_image_from_database)
        self.startFacial.clicked.connect(self.start_facial_recognition)
        self.cancel_image.clicked.connect(self.cancel_processes)

        # Initialize variables
        self.image = None
        self.known_face_encodings = []
        self.known_face_names = []

    def select_image_from_database(self):
        try:
            # Connect to database
            mydb = connector.connect(
                host="localhost",
                user="root",  # Update with your username if different
                password="",   # Update with your password if different
                database="cameradb"
            )
            mycursor = mydb.cursor()

            # Retrieve filenames from database
            mycursor.execute("SELECT filename FROM picture")
            filenames = [row[0] for row in mycursor]

            # Show image selection dialog
            dialog = ImageSelectionDialog(filenames)
            dialog.exec_()

            selected_filename = dialog.selected_filename()
            if selected_filename:
                # Load image data based on filename
                mycursor.execute("SELECT file FROM picture WHERE filename = %s", (selected_filename,))
                image_data = mycursor.fetchone()[0]

                # Convert image data to bytes with utf-8 encoding
                image_bytes = bytes(image_data, 'utf-8')

                # Decode image
                nparr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                # Check if image was successfully loaded
                if image is not None:
                    # Display image in imageWidget
                    qt_image = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format_BGR888)
                    self.imageWidget.setPixmap(QPixmap.fromImage(qt_image))
                    self.image = image
                else:
                    QMessageBox.critical(self, "Error", "Failed to load image.")
        except Exception as e:
            QMessageBox.critical(self, "Error", "Failed to select image from database: {}".format(e))

    def start_facial_recognition(self):
        if self.image is None:
            QMessageBox.warning(self, "Warning", "Please load an image first.")
            return

        try:
            # Load known face encodings from database
            mydb = connector.connect(
                host="localhost",
                user="root",
                password="",
                database="cameradb"
            )
            mycursor = mydb.cursor()

            mycursor.execute("SELECT face_encodings FROM details")
            for row in mycursor:
                face_encoding = row[0]
                self.known_face_encodings.append(face_encoding)

            mycursor.execute("SELECT * FROM details")
            self.known_face_names = mycursor.fetchall()

            # Perform facial recognition
            results = face_recognition.compare_faces(self.known_face_encodings, face_recognition.face_encodings(self.image)[0])

            if True in results:
                first_match_index = results.index(True)
                name = self.known_face_names[first_match_index][0]
                self.detailView.setText("Face recognized as: {}".format(name))
            else:
                self.detailView.setText("The face is unknown.")
        except Exception as e:
            QMessageBox.critical(self, "Error", "Failed to perform facial recognition: {}".format(e))

    def cancel_processes(self):
        # Clear image and results
        self.imageWidget.clear()
        self.detailView.clear()
        self.image = None
        self.known_face_encodings = []
        self.known_face_names = []
