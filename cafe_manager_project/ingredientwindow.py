from decimal import Decimal

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QInputDialog,
    QWidget
)

from db_helper import DB, DB_CONFIG

def make_item(text, alignment=Qt.AlignCenter):
    item = QTableWidgetItem(str(text))
    item.setTextAlignment(alignment)
    return item

class IngredientWindow(QWidget):
    """원재료 재고 관리 전용 창."""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db

        self.init_ui()
        self.connect_signals()
        self.load_ingredients()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel("원재료 재고 관리")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(title)

        # 검색 영역
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("원재료 검색"))

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("원재료명을 입력하세요.")
        search_layout.addWidget(self.search_edit, 1)

        self.search_button = QPushButton("검색")
        self.show_all_button = QPushButton("전체 보기")
        self.backbtn = QPushButton("뒤로가기")

        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.show_all_button)
        search_layout.addSpacing(20)
        search_layout.addWidget(self.backbtn)

        main_layout.addLayout(search_layout)

        # 원재료 입력 영역
        input_group = QGroupBox("원재료 정보")
        input_layout = QHBoxLayout(input_group)

        self.ingredient_id_edit = QLineEdit()
        self.ingredient_id_edit.setReadOnly(True)
        self.ingredient_id_edit.setPlaceholderText("자동 생성")
        self.ingredient_id_edit.setFixedWidth(80)

        self.ingredient_name_edit = QLineEdit()
        self.ingredient_name_edit.setPlaceholderText("예: 원두")

        self.stock_spin = QDoubleSpinBox()
        self.stock_spin.setRange(0, 1_000_000)
        self.stock_spin.setDecimals(1)
        self.stock_spin.setFixedWidth(120)

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["개", "g", "kg", "ml", "L", "박스"])
        self.unit_combo.setEditable(True)
        self.unit_combo.setFixedWidth(90)

        self.minimum_stock_spin = QDoubleSpinBox()
        self.minimum_stock_spin.setRange(0, 1_000_000)
        self.minimum_stock_spin.setDecimals(1)
        self.minimum_stock_spin.setFixedWidth(120)

        input_layout.addWidget(QLabel("번호"))
        input_layout.addWidget(self.ingredient_id_edit)
        input_layout.addWidget(QLabel("원재료명"))
        input_layout.addWidget(self.ingredient_name_edit, 1)
        input_layout.addWidget(QLabel("현재 재고"))
        input_layout.addWidget(self.stock_spin)
        input_layout.addWidget(QLabel("단위"))
        input_layout.addWidget(self.unit_combo)
        input_layout.addWidget(QLabel("최소 재고"))
        input_layout.addWidget(self.minimum_stock_spin)

        main_layout.addWidget(input_group)

        # 버튼 영역
        button_layout = QHBoxLayout()

        self.insert_button = QPushButton("등록")
        self.update_button = QPushButton("수정")
        self.delete_button = QPushButton("삭제")
        self.order_button = QPushButton("주문")
        self.clear_button = QPushButton("초기화")
        self.refresh_button = QPushButton("새로고침")

        button_layout.addWidget(self.insert_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.order_button)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.refresh_button)

        main_layout.addLayout(button_layout)

        # 원재료 목록
        self.ingredient_table = QTableWidget()
        self.ingredient_table.setColumnCount(6)
        self.ingredient_table.setHorizontalHeaderLabels(
            ["번호", "원재료명", "현재 재고", "단위", "최소 재고", "상태"]
        )
        self.ingredient_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.ingredient_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.ingredient_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.ingredient_table.verticalHeader().setVisible(False)
        self.ingredient_table.verticalHeader().setDefaultSectionSize(34)
        self.ingredient_table.setAlternatingRowColors(True)

        header = self.ingredient_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.resizeSection(0, 65)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.resizeSection(2, 120)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.resizeSection(3, 85)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.resizeSection(4, 120)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.resizeSection(5, 100)

        self.ingredient_table.setStyleSheet(
            """
            QHeaderView::section {
                background: #e9ecef;
                font-weight: bold;
                border: 1px solid #d6d6d6;
                padding: 6px;
            }
            QTableWidget {
                gridline-color: #dddddd;
                alternate-background-color: #f8f9fa;
            }
            """
        )

        main_layout.addWidget(self.ingredient_table)

    def connect_signals(self):
        self.search_button.clicked.connect(self.search_ingredients)
        self.show_all_button.clicked.connect(self.show_all_ingredients)
        self.search_edit.returnPressed.connect(self.search_ingredients)

        self.insert_button.clicked.connect(self.insert_ingredient)
        self.update_button.clicked.connect(self.update_ingredient)
        self.delete_button.clicked.connect(self.delete_ingredient)
        self.order_button.clicked.connect(self.order_ingredient)
        self.clear_button.clicked.connect(self.clear_inputs)
        self.refresh_button.clicked.connect(self.load_ingredients)

        self.ingredient_table.cellClicked.connect(self.select_ingredient)

    def load_ingredients(self, keyword=""):
        try:
            rows = self.db.get_ingredients(keyword)
            self.ingredient_table.setRowCount(len(rows))

            for row_index, ingredient in enumerate(rows):
                stock = Decimal(str(ingredient["stock"]))
                minimum = Decimal(str(ingredient["minimum_stock"]))
                is_low = stock <= minimum
                status = status = "재고 없음" if stock == 0 else \
                    "주문 필요" if is_low else "정상"
                # status = "주문 필요" if is_low else "정상"

                values = [
                    ingredient["ingredient_id"],
                    ingredient["ingredient_name"],
                    f"{stock:,.2f}".rstrip("0").rstrip("."),
                    ingredient["unit"],
                    f"{minimum:,.2f}".rstrip("0").rstrip("."),
                    status,
                ]

                for column, value in enumerate(values):
                    alignment = (
                        Qt.AlignLeft | Qt.AlignVCenter
                        if column == 1
                        else Qt.AlignCenter
                    )
                    item = make_item(value, alignment)

                    if stock == 0:
                        item.setBackground(QColor("#f59e75"))
                    
                    elif is_low:
                        item.setBackground(QColor("#fff3cd"))


                    self.ingredient_table.setItem(
                        row_index,
                        column,
                        item,
                    )

        except RuntimeError as error:
            QMessageBox.critical(self, "조회 실패", str(error))

    def search_ingredients(self):
        self.load_ingredients(self.search_edit.text().strip())

    def show_all_ingredients(self):
        self.search_edit.clear()
        self.load_ingredients()

    def insert_ingredient(self):
        name = self.ingredient_name_edit.text().strip()
        stock = self.stock_spin.value()
        unit = self.unit_combo.currentText().strip()
        minimum_stock = self.minimum_stock_spin.value()

        if not name:
            QMessageBox.warning(
                self,
                "입력 오류",
                "원재료명을 입력하세요.",
            )
            return

        if not unit:
            QMessageBox.warning(
                self,
                "입력 오류",
                "단위를 입력하세요.",
            )
            return

        try:
            new_id = self.db.insert_ingredient(
                name,
                stock,
                unit,
                minimum_stock,
            )
            QMessageBox.information(
                self,
                "등록 완료",
                f"원재료가 등록되었습니다.\n번호: {new_id}",
            )
            self.clear_inputs()
            self.load_ingredients()

        except RuntimeError as error:
            QMessageBox.critical(self, "등록 실패", str(error))

    def update_ingredient(self):
        ingredient_id = self.ingredient_id_edit.text().strip()

        if not ingredient_id:
            QMessageBox.warning(
                self,
                "선택 오류",
                "수정할 원재료를 표에서 선택하세요.",
            )
            return

        name = self.ingredient_name_edit.text().strip()
        unit = self.unit_combo.currentText().strip()

        if not name or not unit:
            QMessageBox.warning(
                self,
                "입력 오류",
                "원재료명과 단위를 입력하세요.",
            )
            return

        try:
            changed = self.db.update_ingredient(
                int(ingredient_id),
                name,
                self.stock_spin.value(),
                unit,
                self.minimum_stock_spin.value(),
            )

            if changed == 0:
                QMessageBox.warning(
                    self,
                    "수정 결과",
                    "변경된 내용이 없습니다.",
                )
                return

            QMessageBox.information(
                self,
                "수정 완료",
                "원재료 정보가 수정되었습니다.",
            )
            self.clear_inputs()
            self.load_ingredients()

        except RuntimeError as error:
            QMessageBox.critical(self, "수정 실패", str(error))

    def delete_ingredient(self):
        ingredient_id = self.ingredient_id_edit.text().strip()

        if not ingredient_id:
            QMessageBox.warning(
                self,
                "선택 오류",
                "삭제할 원재료를 표에서 선택하세요.",
            )
            return

        answer = QMessageBox.question(
            self,
            "삭제 확인",
            f"'{self.ingredient_name_edit.text()}' 원재료를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        try:
            deleted = self.db.delete_ingredient(int(ingredient_id))

            if deleted == 0:
                QMessageBox.warning(
                    self,
                    "삭제 실패",
                    "삭제할 원재료를 찾을 수 없습니다.",
                )
                return

            QMessageBox.information(
                self,
                "삭제 완료",
                "원재료가 삭제되었습니다.",
            )
            self.clear_inputs()
            self.load_ingredients()

        except RuntimeError as error:
            QMessageBox.critical(self, "삭제 실패", str(error))

    def order_ingredient(self):
        ingredient_id = self.ingredient_id_edit.text().strip()

        if not ingredient_id:
            QMessageBox.warning(
                self,
                "선택 오류",
                "주문할 원재료를 표에서 선택하세요.",
            )
            return

        quantity, ok = QInputDialog.getDouble(
            self,
            "원재료 주문",
            f"{self.ingredient_name_edit.text()} 주문 수량:",
            1.0,
            0.01,
            1_000_000,
            2,
        )

        if not ok:
            return

        try:
            self.db.order_ingredient(
                int(ingredient_id),
                quantity,
            )
            QMessageBox.information(
                self,
                "주문 완료",
                "주문 수량이 재고에 반영되었습니다.",
            )
            self.clear_inputs()
            self.load_ingredients()

        except RuntimeError as error:
            QMessageBox.critical(self, "주문 실패", str(error))

    def select_ingredient(self, row, column):
        items = [
            self.ingredient_table.item(row, index)
            for index in range(5)
        ]

        if any(item is None for item in items):
            return

        self.ingredient_id_edit.setText(items[0].text())
        self.ingredient_name_edit.setText(items[1].text())
        self.stock_spin.setValue(
            float(items[2].text().replace(",", ""))
        )
        self.unit_combo.setCurrentText(items[3].text())
        self.minimum_stock_spin.setValue(
            float(items[4].text().replace(",", ""))
        )

    def clear_inputs(self):
        self.ingredient_id_edit.clear()
        self.ingredient_name_edit.clear()
        self.stock_spin.setValue(0)
        self.unit_combo.setCurrentIndex(0)
        self.minimum_stock_spin.setValue(0)
        self.ingredient_table.clearSelection()
        self.ingredient_name_edit.setFocus()