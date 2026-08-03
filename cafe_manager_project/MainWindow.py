import socket
import sys
from decimal import Decimal

from PyQt5 import uic
from PyQt5.QtCore import QDate, Qt, QTimer, QTime, QDateTime
from PyQt5.QtWidgets import (
    QStackedWidget,
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from db_helper import DB, DB_CONFIG
from ingredientwindow import IngredientWindow
from menu_manage import MenuManageDialog

form_menu = uic.loadUiType("menu.ui")[0]

def make_item(text, alignment=Qt.AlignCenter):
    item = QTableWidgetItem(str(text))
    item.setTextAlignment(alignment)
    return item

class Menu(QWidget, form_menu):
    def __init__(self, show_inventory, show_ingred, show_menu_manage):
        super().__init__()
        self.setupUi(self)
        self.db = DB(**DB_CONFIG)

        self.time_label.setGeometry(30, 140, 300, 25)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.timeout.connect(self.update_running_time)
        self.timer.start(1000)

        self.start_time = QTime.currentTime()

        self.toolButton.clicked.connect(show_inventory)
        self.toolButton_2.clicked.connect(show_ingred)
        self.toolButton_3.clicked.connect(show_menu_manage)

        self.show_ip()
        self.load_sales()
        self.load_ingredients()

        self.update_time()
        self.refresh_summary()

    def refresh_summary(self):
        self.load_sales()
        self.load_ingredients()

    def update_time(self):
            current = QDateTime.currentDateTime()
            self.time_label_2.setText(current.toString("현재 시간 : yyyy-MM-dd hh:mm"))

    def show_ip(self):
        try:
            ip = socket.gethostbyname(socket.gethostname())
            self.ip_label.setText(f"IP : {ip}")
        except Exception:
            ip = "확인 불가"


    def update_running_time(self):
        sec = self.start_time.secsTo(QTime.currentTime())

        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60

        self.time_label.setText(
            f"접속 시간 : {h:02}:{m:02}:{s:02}"
        )

    def load_sales(self, keyword=""):
        try:
            sales = self.db.get_sales(keyword)

            total_quantity = 0
            total_amount = 0

            for row_index, sale in enumerate(sales):
                sales_amount = (
                    sale["price"] * sale["sales_quantity"]
                )
                total_quantity += sale["sales_quantity"]
                total_amount += sales_amount

            self.label_3.setText(
                f"총 판매량: {total_quantity:,}잔"
                f"\n총 매출액: {total_amount:,}원"
            )
            self.label_3.adjustSize()

        except RuntimeError as error:
                    QMessageBox.critical(
                        self,
                        "판매 내역 조회 실패",
                        str(error),
                    )

    def load_ingredients(self, keyword=""):
        try:
            rows = self.db.get_ingredients(keyword)
            total_stock = 0
            total_sale = 0

            for row_index, ingredient in enumerate(rows):
                stock = Decimal(str(ingredient["stock"]))
                minimum = Decimal(str(ingredient["minimum_stock"]))
                if stock == 0:
                    total_sale += 1
                elif stock <= minimum:
                    total_stock += 1
            self.label_4.setText(
                f"주문 필요: {total_stock:,}건\n"
                f"재고 없음: {total_sale:,}건"
            )
            self.label_4.adjustSize()

            if total_sale > 0:
                self.label_4.setStyleSheet(
                    """
                    QLabel{
                        color:red;
                    }
                    """
                )

            elif total_stock > 0:
                self.label_4.setStyleSheet(
                    """
                    QLabel{
                        color:#FF5E00;
                    }
                    """
                )
            else:
                self.label_4.setStyleSheet(
                    ""
                )

                

        except RuntimeError as error:
            QMessageBox.critical(self, "조회 실패", str(error))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
                
        self.db = DB(**DB_CONFIG)
        self.ingredient_window = None

        self.setWindowTitle("카페 판매 및 재고 관리")
        self.resize(1050, 700)

        # QStackedWidget 생성
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 페이지 생성
        self.page1 = Menu(self.show_inventory, self.show_inventory2, self.menu_show)
        self.page2 = self.create_menu_page()
        self.page3 = IngredientWindow(self.db, self)

        # 페이지 등록
        self.stack.addWidget(self.page1)   # index 0
        self.stack.addWidget(self.page2)   # index 1
        self.stack.addWidget(self.page3)   # index 2

        self.page3.backbtn.clicked.connect(self.show_menu)

        self.connect_signals()
        self.load_menu_combo()
        self.load_sales()
        
    def menu_show(self):
        self.hide()

        dialog = MenuManageDialog(
            self.db,
            parent=self,
        )
        dialog.exec_()

        self.load_menu_combo()
        self.page1.refresh_summary()

        self.show()
    # -------------------------
    # 첫 번째 페이지
    # -------------------------
    def create_menu_page(self):
        page = QWidget()

        main_layout = QVBoxLayout(page)

        title = QLabel("카페 판매 관리")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(title)

        # 검색 영역
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("상품 검색"))

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("상품명의 일부를 입력하세요. 예: 라떼")
        search_layout.addWidget(self.search_edit, 1)

        self.search_button = QPushButton("검색")
        self.show_all_button = QPushButton("전체 보기")
        self.back_btn = QPushButton("뒤로가기")

        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.show_all_button)
        search_layout.addSpacing(20)
        search_layout.addWidget(self.back_btn)

        main_layout.addLayout(search_layout)

        # 판매 정보 수평 배치
        input_group = QGroupBox("판매 정보")
        input_layout = QHBoxLayout(input_group)

        self.sale_id_edit = QLineEdit()
        self.sale_id_edit.setReadOnly(True)
        self.sale_id_edit.setPlaceholderText("자동 생성")
        self.sale_id_edit.setFixedWidth(80)

        self.sale_date_edit = QDateEdit()
        self.sale_date_edit.setCalendarPopup(True)
        self.sale_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.sale_date_edit.setDate(QDate.currentDate())
        self.sale_date_edit.setFixedWidth(125)

        self.menu_combo = QComboBox()
        self.menu_combo.setMinimumWidth(220)

        self.price_edit = QLineEdit()
        self.price_edit.setReadOnly(True)
        self.price_edit.setFixedWidth(120)

        self.sales_quantity_spin = QSpinBox()
        self.sales_quantity_spin.setRange(0, 100_000)
        self.sales_quantity_spin.setSuffix(" 잔")
        self.sales_quantity_spin.setFixedWidth(110)

        input_layout.addWidget(QLabel("번호"))
        input_layout.addWidget(self.sale_id_edit)
        input_layout.addWidget(QLabel("날짜"))
        input_layout.addWidget(self.sale_date_edit)
        input_layout.addWidget(QLabel("상품명"))
        input_layout.addWidget(self.menu_combo, 1)
        input_layout.addWidget(QLabel("가격"))
        input_layout.addWidget(self.price_edit)
        input_layout.addWidget(QLabel("판매량"))
        input_layout.addWidget(self.sales_quantity_spin)

        main_layout.addWidget(input_group)

        # 버튼 영역
        button_layout = QHBoxLayout()

        self.insert_button = QPushButton("등록")
        self.update_button = QPushButton("수정")
        self.delete_button = QPushButton("삭제")
        self.clear_button = QPushButton("초기화")
        self.refresh_button = QPushButton("새로고침")

        button_layout.addWidget(self.insert_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.refresh_button)

        main_layout.addLayout(button_layout)

        # 판매 목록
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(6)
        self.sales_table.setHorizontalHeaderLabels(
            ["번호", "날짜", "상품명", "가격", "판매량", "매출액"]
        )
        self.sales_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.sales_table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.sales_table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.sales_table.verticalHeader().setVisible(False)
        self.sales_table.verticalHeader().setDefaultSectionSize(36)
        self.sales_table.setAlternatingRowColors(True)

        header = self.sales_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.resizeSection(0, 65)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.resizeSection(1, 120)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.resizeSection(3, 110)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.resizeSection(4, 90)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.resizeSection(5, 125)

        self.sales_table.setStyleSheet(
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

        main_layout.addWidget(self.sales_table)

        ## 최 하단 설정

        self.summary_label = QLabel("총 판매량: 0잔 | 총 매출액: 0원")
        self.summary_label.setAlignment(Qt.AlignRight)
        self.summary_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; padding: 8px;"
        )

        main_layout.addWidget(self.summary_label)
        page.setLayout(main_layout)

        return page

    def connect_signals(self):
        self.search_button.clicked.connect(self.search_sales)
        self.show_all_button.clicked.connect(self.show_all_sales)
        self.search_edit.returnPressed.connect(self.search_sales)
        self.search_edit.textChanged.connect(self.search_sales)
        self.back_btn.clicked.connect(self.show_menu)

        self.menu_combo.currentIndexChanged.connect(self.update_price_display)

        self.insert_button.clicked.connect(self.insert_sale)
        self.update_button.clicked.connect(self.update_sale)
        self.delete_button.clicked.connect(self.delete_sale)
        self.clear_button.clicked.connect(self.clear_inputs)
        self.refresh_button.clicked.connect(self.load_sales)

        self.sales_table.cellClicked.connect(self.select_sale)

    def load_menu_combo(self):
        try:
            menus = self.db.get_all_menus()

            self.menu_combo.blockSignals(True)
            self.menu_combo.clear()

            for menu in menus:
                self.menu_combo.addItem(
                    menu["product_name"],
                    {
                        "menu_id": menu["menu_id"],
                        "price": menu["price"],
                    },
                )

            self.menu_combo.blockSignals(False)
            self.update_price_display()

        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "메뉴 조회 실패",
                str(error),
            )

    def update_price_display(self):
        data = self.menu_combo.currentData()

        if not data:
            self.price_edit.clear()
            return

        self.price_edit.setText(f'{data["price"]:,} 원')

    def load_sales(self, keyword=""):
        try:
            sales = self.db.get_sales(keyword)
            self.sales_table.setRowCount(len(sales))

            total_quantity = 0
            total_amount = 0

            for row_index, sale in enumerate(sales):
                sales_amount = (
                    sale["price"] * sale["sales_quantity"]
                )
                total_quantity += sale["sales_quantity"]
                total_amount += sales_amount

                values = [
                    sale["sale_id"],
                    sale["sale_date"],
                    sale["product_name"],
                    f'{sale["price"]:,}',
                    sale["sales_quantity"],
                    f"{sales_amount:,}",
                ]

                for column, value in enumerate(values):
                    alignment = (
                        Qt.AlignLeft | Qt.AlignVCenter
                        if column == 2
                        else Qt.AlignCenter
                    )
                    self.sales_table.setItem(
                        row_index,
                        column,
                        make_item(value, alignment),
                    )

            self.summary_label.setText(
                f"총 판매량: {total_quantity:,}잔 | "
                f"총 매출액: {total_amount:,}원"
            )

        except RuntimeError as error:
            QMessageBox.critical(
                self,
                "판매 내역 조회 실패",
                str(error),
            )

    def search_sales(self):
        self.load_sales(self.search_edit.text().strip())

    def show_all_sales(self):
        self.search_edit.clear()
        self.load_sales()

    def insert_sale(self):
        menu_data = self.menu_combo.currentData()

        if not menu_data:
            QMessageBox.warning(
                self,
                "입력 오류",
                "등록할 메뉴를 선택하세요.",
            )
            return

        try:
            new_id = self.db.insert_sale(
                self.sale_date_edit.date().toString(
                    "yyyy-MM-dd"
                ),
                menu_data["menu_id"],
                self.sales_quantity_spin.value(),
            )

            QMessageBox.information(
                self,
                "등록 완료",
                f"판매 정보가 등록되었습니다.\n번호: {new_id}",
            )
            self.clear_inputs()
            self.load_sales(self.search_edit.text().strip())

        except RuntimeError as error:
            QMessageBox.critical(self, "등록 실패", str(error))

    def update_sale(self):
        sale_id = self.sale_id_edit.text().strip()
        menu_data = self.menu_combo.currentData()

        if not sale_id:
            QMessageBox.warning(
                self,
                "선택 오류",
                "수정할 판매 내역을 선택하세요.",
            )
            return

        if not menu_data:
            return

        try:
            changed = self.db.update_sale(
                int(sale_id),
                self.sale_date_edit.date().toString(
                    "yyyy-MM-dd"
                ),
                menu_data["menu_id"],
                self.sales_quantity_spin.value(),
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
                "판매 정보가 수정되었습니다.",
            )
            self.clear_inputs()
            self.load_sales(self.search_edit.text().strip())

        except RuntimeError as error:
            QMessageBox.critical(self, "수정 실패", str(error))

    def delete_sale(self):
        sale_id = self.sale_id_edit.text().strip()

        if not sale_id:
            QMessageBox.warning(
                self,
                "선택 오류",
                "삭제할 판매 내역을 선택하세요.",
            )
            return

        answer = QMessageBox.question(
            self,
            "삭제 확인",
            "선택한 판매 내역을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            return

        try:
            deleted = self.db.delete_sale(int(sale_id))

            if deleted == 0:
                QMessageBox.warning(
                    self,
                    "삭제 실패",
                    "삭제할 판매 내역을 찾을 수 없습니다.",
                )
                return

            QMessageBox.information(
                self,
                "삭제 완료",
                "판매 내역이 삭제되었습니다.",
            )
            self.clear_inputs()
            self.load_sales(self.search_edit.text().strip())

        except RuntimeError as error:
            QMessageBox.critical(self, "삭제 실패", str(error))

    def select_sale(self, row, column):
        sale_id_item = self.sales_table.item(row, 0)
        date_item = self.sales_table.item(row, 1)
        product_item = self.sales_table.item(row, 2)
        quantity_item = self.sales_table.item(row, 4)

        if any(
            item is None
            for item in (
                sale_id_item,
                date_item,
                product_item,
                quantity_item,
            )
        ):
            return

        self.sale_id_edit.setText(sale_id_item.text())
        self.sale_date_edit.setDate(
            QDate.fromString(date_item.text(), "yyyy-MM-dd")
        )

        index = self.menu_combo.findText(product_item.text())
        if index >= 0:
            self.menu_combo.setCurrentIndex(index)

        self.sales_quantity_spin.setValue(
            int(quantity_item.text().replace(",", ""))
        )

    def clear_inputs(self):
        self.sale_id_edit.clear()
        self.sale_date_edit.setDate(QDate.currentDate())
        self.sales_quantity_spin.setValue(0)

        if self.menu_combo.count() > 0:
            self.menu_combo.setCurrentIndex(0)

        self.sales_table.clearSelection()


    # -------------------------
    # 두 번째 페이지
    # -------------------------
    def create_inventory_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        self.label = QLabel("재고 화면")

        btn_layout = QHBoxLayout()
        back_btn = QPushButton("뒤로가기")

        btn_layout.addStretch()
        btn_layout.addWidget(back_btn)

        layout.addWidget(self.label)
        layout.addLayout(btn_layout)
        

        page.setLayout(layout)

        back_btn.clicked.connect(self.show_menu)

        return page

    # -------------------------
    # 페이지 전환
    # -------------------------
    def show_inventory(self):
        self.stack.setCurrentIndex(1)

    def show_inventory2(self):
        self.stack.setCurrentIndex(2)

    def show_menu(self):
        self.page1.refresh_summary()
        self.stack.setCurrentIndex(0)


# app = QApplication(sys.argv)

# window = MainWindow()
# window.show()

# sys.exit(app.exec_())