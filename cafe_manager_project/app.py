import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from login_dialog import LoginDialog
from MainWindow import MainWindow
from PyQt5 import uic

form_class = uic.loadUiType("Kiosk.ui")[0]

class Window(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("키오스크")
        self.admin_window = 0
        self.setting.clicked.connect(self.AdminWindow)

    def AdminWindow(self):
        login = LoginDialog()
        if login.exec_() == LoginDialog.Accepted: 

            self.admin_window = MainWindow()
            self.admin_window.show()

            self.close() 


# 개인 묘듈을 사용할 때 필요한 기능

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = Window()
    main.show()

    sys.exit(app.exec_())