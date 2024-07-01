import sys
from disptime import *

class MyForm(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        QtCore.QObject.connect(self.ui.pushButtonStart, QtCore.SIGNAL('clicked()'), self.startDisplay)
        QtCore.QObject.connect(self.ui.pushButtonStop, QtCore.SIGNAL('clicked()'), self.stopDisplay)
        self.ui.pushButtonStop.setEnabled(False)

        self.time1 = None
        self.showlcd()

    def showlcd(self):  
        if self.time1 != None:
            time2 = QtCore.QTime(self.time1).secsTo(QtCore.QTime.currentTime())
            self.ui.lcdNumber.display(time2)

    def startDisplay(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.showlcd)
        self.timer.start(1000)
        self.time1 = QtCore.QTime.currentTime() 

        self.ui.pushButtonStart.setEnabled(False)
        self.ui.pushButtonStop.setEnabled(True)

    def stopDisplay(self):
        self.timer.stop()
        self.ui.pushButtonStart.setEnabled(True)
        self.ui.pushButtonStop.setEnabled(False)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MyForm()
    myapp.show()
    sys.exit(app.exec_())
