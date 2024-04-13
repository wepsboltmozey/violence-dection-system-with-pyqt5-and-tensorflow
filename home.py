
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Home(object):
    def setupUi(self, Home):
        Home.setObjectName("Home")
        Home.resize(1100, 455)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        Home.setFont(font)
        Home.setStyleSheet("QWidget#Home{}")
        self.TitleWidget = QtWidgets.QWidget(Home)
        self.TitleWidget.setGeometry(QtCore.QRect(0, 0, 1100, 80))
        self.TitleWidget.setStyleSheet("    Qwidget#TitleWidget{\n"
"\n"
"}\n"
"#TitleWidget{\n"
"background-color: rgb(13, 30, 64);\n"
"margin: 0;\n"
"\n"
"}")
        self.TitleWidget.setObjectName("TitleWidget")
        self.label = QtWidgets.QLabel(self.TitleWidget)
        self.label.setGeometry(QtCore.QRect(20, 10, 61, 61))
        self.label.setStyleSheet("color: rgb(0, 0, 0);\n"
"border-raduis: 50px;")
        self.label.setPixmap(QtGui.QPixmap("resources/camera.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.title = QtWidgets.QLabel(self.TitleWidget)
        self.title.setGeometry(QtCore.QRect(290, 20, 611, 41))
        self.title.setStyleSheet("color: rgb(255, 255, 255);\n"
"font: 700 24pt \"Calibri\";")
        self.title.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.title.setObjectName("title")
        self.label_2 = QtWidgets.QLabel(self.TitleWidget)
        self.label_2.setGeometry(QtCore.QRect(1030, 20, 49, 41))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("resources/avat.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.Button = QtWidgets.QWidget(Home)
        self.Button.setGeometry(QtCore.QRect(0, 80, 1100, 51))
        self.Button.setStyleSheet("background-color: rgb(26, 56, 115);\n"
"\n"
"")
        self.Button.setObjectName("Button")
        self.homebutton = QtWidgets.QPushButton(self.Button)
        self.homebutton.setGeometry(QtCore.QRect(20, 10, 121, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.homebutton.setFont(font)
        self.homebutton.setStyleSheet("#homebutton{\n"
"background-color: rgb(48, 131, 59);\n"
"border-radius: 15px;\n"
"color: white;\n"
"padding: 10px 20px;\n"
"}\n"
"\n"
"#homebutton:hover {\n"
"background-color: #0D1E40;\n"
"border-radius: 15px;\n"
"color: white;\n"
"}\n"
"")
        self.homebutton.setFlat(False)
        self.homebutton.setObjectName("homebutton")
        self.preview = QtWidgets.QPushButton(self.Button)
        self.preview.setGeometry(QtCore.QRect(180, 10, 151, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.preview.setFont(font)
        self.preview.setStyleSheet("#preview{\n"
"background-color: rgb(48, 131, 59);\n"
"border-radius: 15px;\n"
"color: white;\n"
"padding: 10px 20px;\n"
"}\n"
"\n"
"#preview:hover {\n"
"background-color: #0D1E40;\n"
"border-radius: 15px;\n"
"color: white;\n"
"}\n"
"")
        self.preview.setObjectName("preview")
        self.alertN = QtWidgets.QPushButton(self.Button)
        self.alertN.setGeometry(QtCore.QRect(370, 10, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.alertN.setFont(font)
        self.alertN.setStyleSheet("#alertN{\n"
"background-color: rgb(48, 131, 59);\n"
"border-radius: 15px;\n"
"color: white;\n"
"padding: 10px 20px;\n"
"}\n"
"\n"
"#alertN:hover {\n"
"background-color: #0D1E40;\n"
"border-radius: 15px;\n"
"color: white;\n"
"}\n"
"")
        self.alertN.setObjectName("alertN")
        
        self.mainWidget = QtWidgets.QWidget(Home)
        self.mainWidget.setGeometry(QtCore.QRect(0, 130, 1100, 541))
        self.mainWidget.setStyleSheet("#mainWidget{\n"
"background-color: #b0c1d9;\n"
"color: white;\n"
"padding: 10px 20px;\n"
"margin-top: 0;\n"
"margin-left: 0;\n"
"margin-right:0;\n"
"}\n"
"\n"
"\n"
"")
        self.mainWidget.setObjectName("mainWidget")
        self.camera = QtWidgets.QWidget(self.mainWidget)
        self.camera.setGeometry(QtCore.QRect(160, 30, 800, 400))
        self.camera.setStyleSheet("\n"
"\n"
"#camera{\n"
"border-radius: 20;\n"
"background-color: rgb(13, 30, 64);\n"
"color: rgb(255, 255, 255);\n"
"}")
        self.camera.setObjectName("camera")

        self.label_3 = QtWidgets.QLabel(self.mainWidget)
        self.label_3.setGeometry(QtCore.QRect(580, 450, 49, 16))
        self.label_3.setObjectName("label_3")
        self.timeOn = QtWidgets.QLabel(self.mainWidget)
        self.timeOn.setGeometry(QtCore.QRect(670, 450, 49, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        self.timeOn.setFont(font)
        self.timeOn.setObjectName("timeOn")
        self.label_4 = QtWidgets.QLabel(self.mainWidget)
        self.label_4.setGeometry(QtCore.QRect(170, 450, 31, 16))
        self.label_4.setObjectName("label_4")
        self.startTime = QtWidgets.QLabel(self.mainWidget)
        self.startTime.setGeometry(QtCore.QRect(460, 450, 49, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        self.startTime.setFont(font)
        self.startTime.setObjectName("startTime")
        self.label_5 = QtWidgets.QLabel(self.mainWidget)
        self.label_5.setGeometry(QtCore.QRect(350, 450, 61, 16))
        self.label_5.setObjectName("label_5")
        self.date = QtWidgets.QLabel(self.mainWidget)
        self.date.setGeometry(QtCore.QRect(220, 450, 101, 16))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        self.date.setFont(font)
        self.date.setObjectName("date")
        self.stop = QtWidgets.QPushButton(self.mainWidget)
        self.stop.setGeometry(QtCore.QRect(540, 490, 121, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.stop.setFont(font)
        self.stop.setStyleSheet("#stop{\n"
"background-color: rgb(48, 131, 59);\n"
"border-radius: 15px;\n"
"color: white;\n"
"padding: 10px 20px;\n"
"}\n"
"\n"
"#stop:hover {\n"
"background-color: #0D1E40;\n"
"border-radius: 15px;\n"
"color: white;\n"
"}\n"
"")
        self.stop.setFlat(False)
        self.stop.setObjectName("stop")
        self.start = QtWidgets.QPushButton(self.mainWidget)
        self.start.setGeometry(QtCore.QRect(320, 490, 121, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.start.setFont(font)
        self.start.setStyleSheet("#start{\n"
"background-color: rgb(48, 131, 59);\n"
"border-radius: 15px;\n"
"color: white;\n"
"padding: 10px 20px;\n"
"}\n"
"\n"
"#start:hover {\n"
"background-color: #0D1E40;\n"
"border-radius: 15px;\n"
"color: white;\n"
"}\n"
"")
        self.start.setFlat(False)
        self.start.setObjectName("start")

        self.retranslateUi(Home)
        QtCore.QMetaObject.connectSlotsByName(Home)

    def retranslateUi(self, Home):
        _translate = QtCore.QCoreApplication.translate
        Home.setWindowTitle(_translate("Home", "Home"))
        self.title.setText(_translate("Home", "SMART CAMERA SYSTEM"))
        self.homebutton.setText(_translate("Home", "Home"))
        self.preview.setText(_translate("Home", "preview"))
        self.alertN.setText(_translate("Home", "Alerts"))
        self.label_3.setText(_translate("Home", "Time on"))
        self.timeOn.setText(_translate("Home", "04:23:12"))
        self.label_4.setText(_translate("Home", "Date "))
        self.startTime.setText(_translate("Home", "12:03:11"))
        self.label_5.setText(_translate("Home", "Start time"))
        self.date.setText(_translate("Home", "12/04/24"))
        self.stop.setText(_translate("Home", "stop"))
        self.start.setText(_translate("Home", "start"))

