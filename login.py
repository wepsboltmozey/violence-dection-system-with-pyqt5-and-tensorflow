
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_login(object):
    def setupUi(self, login):
        login.setObjectName("login")
        login.resize(487, 325)
        login.setStyleSheet("#login{\n"
"color: rgb(255, 255, 255);\n"
"background-color: rgb(13, 30, 64);\n"
"alignment: center;\n"
"}\n"
"")
        self.cam = QtWidgets.QLabel(login)
        self.cam.setGeometry(QtCore.QRect(210, 0, 60, 57))
        self.cam.setText("")
        self.cam.setPixmap(QtGui.QPixmap("resources/camera.png"))
        self.cam.setObjectName("cam")
        self.log = QtWidgets.QLabel(login)
        self.log.setGeometry(QtCore.QRect(200, 50, 371, 51))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.log.setFont(font)
        self.log.setStyleSheet("color: rgb(255, 255, 255);")
        self.log.setObjectName("log")
        self.label_3 = QtWidgets.QLabel(login)
        self.label_3.setGeometry(QtCore.QRect(30, 110, 81, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_3.setObjectName("label_3")
        self.passwd = QtWidgets.QLabel(login)
        self.passwd.setGeometry(QtCore.QRect(30, 150, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.passwd.setFont(font)
        self.passwd.setStyleSheet("color: rgb(255, 255, 255);")
        self.passwd.setObjectName("passwd")
        self.username = QtWidgets.QLineEdit(login)
        self.username.setGeometry(QtCore.QRect(170, 110, 211, 22))
        self.username.setStyleSheet("#username{\n"
"border-radius: 15px;\n"
"}")
        self.username.setObjectName("username")
        self.password = QtWidgets.QLineEdit(login)
        self.password.setGeometry(QtCore.QRect(170, 150, 211, 22))
        self.password.setStyleSheet("#username{\n"
"border-radius: 15px;\n"
"}")
        self.password.setObjectName("password")
        self.loginbutton = QtWidgets.QPushButton(login)
        self.loginbutton.setGeometry(QtCore.QRect(320, 190, 111, 31))
        self.loginbutton.setStyleSheet("#loginbutton{\n"
"background-color: rgb(48, 131, 59);\n"
"border-radius: 15px;\n"
"color: white;\n"
"padding: 10px 20px;\n"
"}\n"
"\n"
"#loginbutton:hover {\n"
"background-color: #0D1E40;\n"
"border-radius: 15px;\n"
"color: white;\n"
"}\n"
"")
        self.loginbutton.setObjectName("loginbutton")
        self.label_8 = QtWidgets.QLabel(login)
        self.label_8.setGeometry(QtCore.QRect(20, 240, 291, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label_8.setFont(font)
        self.label_8.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_8.setObjectName("label_8")
        self.regbutton = QtWidgets.QPushButton(login)
        self.regbutton.setGeometry(QtCore.QRect(90, 270, 111, 31))
        self.regbutton.setStyleSheet("#regbutton{\n"
"background-color: rgb(48, 131, 59);\n"
"border-radius: 15px;\n"
"color: white;\n"
"padding: 10px 20px;\n"
"}\n"
"\n"
"#regbutton:hover {\n"
"background-color: #0D1E40;\n"
"border-radius: 15px;\n"
"color: white;\n"
"}\n"
"")
        self.regbutton.setObjectName("regbutton")

        self.retranslateUi(login)
        QtCore.QMetaObject.connectSlotsByName(login)

    def retranslateUi(self, login):
        _translate = QtCore.QCoreApplication.translate
        login.setWindowTitle(_translate("login", "Login"))
        self.log.setText(_translate("login", "LOG IN"))
        self.label_3.setText(_translate("login", "username"))
        self.passwd.setText(_translate("login", "password"))
        self.loginbutton.setText(_translate("login", "login"))
        self.label_8.setText(_translate("login", "If you don\'t have an account."))
        self.regbutton.setText(_translate("login", "register"))
