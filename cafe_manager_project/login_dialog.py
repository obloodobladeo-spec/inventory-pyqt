import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox
from db_helper import DB, DB_CONFIG
from PyQt5.QtCore import Qt
from PyQt5 import uic

form_login = uic.loadUiType("login.ui")[0]

class LoginDialog(QDialog, form_login):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle("관리자 권한 확인")
        self.db = DB(**DB_CONFIG)

        self.password.setEchoMode(QLineEdit.Password)


        # 로그인 버튼 설정
        self.btn_login.clicked.connect(self.try_login) # 클릿 했을 때 시그널
        self.btn_login.setDefault(True)

        # # 숫자 패드 기능 추가
        buttons = [self.btn_0, self.btn_1, self.btn_2, self.btn_3, self.btn_4, self.btn_5, self.btn_6, self.btn_7, self.btn_8, self.btn_9]
        self.btn_0.clicked.connect(lambda: self.input_number("0"))
        self.btn_1.clicked.connect(lambda: self.input_number("1"))
        self.btn_2.clicked.connect(lambda: self.input_number("2"))
        self.btn_3.clicked.connect(lambda: self.input_number("3"))
        self.btn_4.clicked.connect(lambda: self.input_number("4"))
        self.btn_5.clicked.connect(lambda: self.input_number("5"))
        self.btn_6.clicked.connect(lambda: self.input_number("6"))
        self.btn_7.clicked.connect(lambda: self.input_number("7"))
        self.btn_8.clicked.connect(lambda: self.input_number("8"))
        self.btn_9.clicked.connect(lambda: self.input_number("9"))
        self.btn_backsp.clicked.connect(self.password.backspace)

        # 타 버튼 기능 추가
        self.btn_clear.clicked.connect(lambda: self.password.clear())
        # self.btn_backsp.click.connect(self.password.)

        # # 취소 버튼)
        self.btn_rgt.clicked.connect(self.try_exit)

        # 숫자 버튼 기능
        # self.btn

    def input_number(self, number):
        self.password.insert(number)

    def try_login(self):
        uid = self.username.text().strip()
        pw = self.password.text().strip()
        if not uid or not pw:
            QMessageBox.warning(self, "오류", "아이디와 비밀번호를 모두 입력하세요.")
            return

        print(uid, pw)
        ok = self.db.verify_user(uid, pw)
        print(ok)
        if ok:
            self.accept()
        else:
            QMessageBox.critical(self, "실패", "아이디 또는 비밀번호가 올바르지 않습니다.")
            self.password.clear()

    def try_exit(self): # 버튼에 넣었던 함수
        return self.reject()