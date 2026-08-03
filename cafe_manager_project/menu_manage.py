import sys

from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
)

from db_helper import DB, DB_CONFIG

CATEGORIES = ["커피", "에이드", "음료", "기타"]
COLUMN_COUNT = 4

form_class = uic.loadUiType("menuedit.ui")[0]


class MenuInputDialog(QDialog):
    """메뉴 추가와 메뉴 수정에 공통으로 사용하는 입력창."""

    def __init__(
        self,
        db,
        category,
        menu_id=None,
        parent=None,
        ):

        super().__init__(parent)
        self.db = db
        self.menu_id = menu_id

        self.setWindowTitle(
            "메뉴 추가" if menu_id is None else "메뉴 수정"
        )
        self.setFixedSize(420, 260)

        self.name_edit = QLineEdit()

        self.price_spin = QSpinBox()
        self.price_spin.setRange(0, 10_000_000)
        self.price_spin.setSingleStep(500)
        self.price_spin.setSuffix(" 원")

        self.category_combo = QComboBox()
        self.category_combo.addItems(CATEGORIES)
        self.category_combo.setCurrentText(category)

        form_layout = QFormLayout()
        form_layout.addRow("메뉴명", self.name_edit)
        form_layout.addRow("가격", self.price_spin)
        form_layout.addRow("카테고리", self.category_combo)

        self.delete_button = QPushButton("삭제")
        self.save_button = QPushButton("저장")
        self.cancel_button = QPushButton("취소")

        self.delete_button.setVisible(menu_id is not None)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.save_button.clicked.connect(self.save_menu)
        self.cancel_button.clicked.connect(self.reject)
        self.delete_button.clicked.connect(self.delete_menu)

        if self.menu_id is not None:
            self.load_menu()

    def load_menu(self):
        try:
            menu = self.db.get_menu(self.menu_id)

            if menu is None:
                QMessageBox.warning(
                    self,
                    "조회 실패",
                    "선택한 메뉴를 찾을 수 없습니다.",
                )
                self.reject()
                return

            self.name_edit.setText(menu["product_name"])
            self.price_spin.setValue(menu["price"])
            self.category_combo.setCurrentText(
                menu["category"]
            )

        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "조회 실패",
                str(error),
            )
            self.reject()

    def save_menu(self):
        product_name = self.name_edit.text().strip()
        price = self.price_spin.value()
        category = self.category_combo.currentText()

        if not product_name:
            QMessageBox.warning(
                self,
                "입력 오류",
                "메뉴명을 입력하세요.",
            )
            self.name_edit.setFocus()
            return

        try:
            if self.menu_id is None:
                self.db.insert_menu(
                    product_name,
                    price,
                    category,
                )
            else:
                self.db.update_menu(
                    self.menu_id,
                    product_name,
                    price,
                    category,
                )

            self.accept()

        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "저장 실패",
                str(error),
            )

    def delete_menu(self):
        answer = QMessageBox.question(
            self,
            "삭제 확인",
            "선택한 메뉴를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        try:
            deleted = self.db.delete_menu(self.menu_id)

            if deleted == 0:
                QMessageBox.warning(
                    self,
                    "삭제 실패",
                    "삭제할 메뉴를 찾을 수 없습니다.",
                )
                return

            self.accept()

        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "삭제 실패",
                str(error),
            )


class MenuManageDialog(QDialog, form_class):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("키오스크 메뉴 관리")

        self.db = db
        self.current_category = "커피"

        # Designer objectName이 아래와 같아야 함
        self.coffeeButton.clicked.connect(
            lambda: self.change_category("커피")
        )
        self.adeButton.clicked.connect(
            lambda: self.change_category("에이드")
        )
        self.drinkButton.clicked.connect(
            lambda: self.change_category("음료")
        )
        self.etcButton.clicked.connect(
            lambda: self.change_category("기타")
        )
        self.closeButton.clicked.connect(self.close)

        self.category_buttons = {
            "커피": self.coffeeButton,
            "에이드": self.adeButton,
            "음료": self.drinkButton,
            "기타": self.etcButton,
        }

        self.load_menu_cards()

    def change_category(self, category):
        self.current_category = category
        self.load_menu_cards()

    def clear_menu_grid(self):
        while self.menuGridLayout.count():
            item = self.menuGridLayout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def load_menu_cards(self):
        try:
            menu_list = self.db.get_menus_by_category(
                self.current_category
            )
        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "조회 실패",
                str(error),
            )
            return

        self.clear_menu_grid()

        for index, menu in enumerate(menu_list):
            row = index // COLUMN_COUNT
            column = index % COLUMN_COUNT

            card = self.create_menu_card(menu)

            self.menuGridLayout.addWidget(
                card,
                row,
                column,
            )

        # 마지막 메뉴 바로 다음 칸에 추가 버튼 배치
        add_index = len(menu_list)
        add_row = add_index // COLUMN_COUNT
        add_column = add_index % COLUMN_COUNT

        self.menuGridLayout.addWidget(
            self.create_add_button(),
            add_row,
            add_column,
        )

        # 4개 열을 균등하게 사용
        for column in range(COLUMN_COUNT):
            self.menuGridLayout.setColumnStretch(
                column,
                1,
            )

        # 카드가 위쪽에 붙도록 아래쪽에 남는 공간 배분
        self.menuGridLayout.setRowStretch(
            add_row + 1,
            1,
        )

        self.update_category_button_style()

    def create_menu_card(self, menu):
        button = QToolButton()

        if menu["category"] == "커피":
                    button.setIcon(QIcon("icon/coffeeicon.png"))
                    button.setIconSize(QSize(60, 60))
        elif menu["category"] == "에이드":
            button.setIcon(QIcon("icon/adeicon.png"))
            button.setIconSize(QSize(60, 60))
        elif menu["category"] == "음료":
            button.setIcon(QIcon("icon/sodaicon.png"))
            button.setIconSize(QSize(60, 60))
        elif menu["category"] == "기타":
            button.setIcon(QIcon("icon/teaicon.png"))
            button.setIconSize(QSize(60, 60))
                

        if menu["product_name"] == '쿠키앤크림프라페':
            button.setText(
                '쿠키앤크림\n프라페\n\n'
                f'{menu["price"]:,}원'
            )
        else:
            button.setText(
                f'{menu["product_name"]}\n\n'
                f'{menu["price"]:,}원'
            )

        button.setToolButtonStyle(
            Qt.ToolButtonTextUnderIcon
        )

        button.setMinimumSize(135, 160)
        button.setMaximumSize(135, 160)

        button.setStyleSheet(
            """
            QToolButton {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
                padding: 10px;
            }

            QToolButton:hover {
                background-color: #fff5df;
                border: 2px solid #f0a500;
            }

            QToolButton:pressed {
                background-color: #ffe8b8;
            }
            """
        )

        button.clicked.connect(
            lambda checked=False,
                   menu_id=menu["menu_id"]:
            self.open_edit_dialog(menu_id)
        )

        return button

    def create_add_button(self):
        button = QPushButton("+\n메뉴 추가")
        button.setMinimumSize(135, 160)
        button.setMaximumSize(135, 160)
        

        button.setStyleSheet(
            """
            QPushButton {
                background-color: #fafafa;
                color: #777777;
                border: 2px dashed #bdbdbd;
                border-radius: 12px;
                font-size: 15px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #fff8e8;
                color: #f29f05;
                border-color: #f29f05;
            }

            QPushButton:pressed {
                background-color: #ffe8b8;
            }
            """
        )

        button.clicked.connect(
            self.open_add_dialog
        )

        return button

    def update_category_button_style(self):
        for category, button in self.category_buttons.items():
            if category == self.current_category:
                button.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #f4a51c;
                        border-radius:15px;
                        color: white;
                        border: none;
                        font-weight: bold;
                    }
                    """
                )
            else:
                button.setStyleSheet("""
                    QPushButton{
                        background:white;
                        border:1px solid #BDBDBD;
                        border-radius:15px;
                    }

                    QPushButton:hover{
                        background:white;
                    }

                    QPushButton:pressed{
                        background:white;
                    }
                    """
                )

    def open_add_dialog(self):
        dialog = MenuInputDialog(
            self.db,
            self.current_category,
            parent=self,
        )

        if dialog.exec_() == QDialog.Accepted:
            # 추가할 때 다른 카테고리를 선택했으면
            # 저장된 카테고리 화면으로 이동
            self.current_category = (
                dialog.category_combo.currentText()
            )
            self.load_menu_cards()

    def open_edit_dialog(self, menu_id):
        dialog = MenuInputDialog(
            self.db,
            self.current_category,
            menu_id=menu_id,
            parent=self,
        )

        if dialog.exec_() == QDialog.Accepted:
            self.current_category = (
                dialog.category_combo.currentText()
            )
            self.load_menu_cards()
