import sys

from PyQt5 import QtWidgets


from welcome import Welcome

app = QtWidgets.QApplication(sys.argv)

window = Welcome() 
window.show()

app.exec()
