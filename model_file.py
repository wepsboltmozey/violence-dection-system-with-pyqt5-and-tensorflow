from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import tensorflow as tf


class ModelLoaderThread(QThread):
    model_loaded = pyqtSignal(object)

    def run(self):
        model_path = 'C:/Users/WEP/Desktop/INTELLIGENT SECURITY CAMERA SYSTEM/violence/'  # Update path to saved model folder
        model = tf.saved_model.load(model_path)
        self.model_loaded.emit(model)
