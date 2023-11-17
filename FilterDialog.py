from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QCheckBox, QPushButton, QScrollArea, QWidget
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, pyqtSignal
import sys

class FilterDialog(QDialog):
    filterApplied = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('筛选供货商')
        if getattr(sys, 'frozen', False):
            self.setWindowIcon(QIcon(sys._MEIPASS + '/vivastock.ico'))
        else:
            self.setWindowIcon(QIcon('vivastock.ico'))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        # self.setFixedSize(200, 250)  # 不再设置固定大小
        self.resize(300, 400)  # 初始大小，但用户可以调整
        self.layout = QVBoxLayout(self)

        self.supplier_checkboxes = []

        font = QFont()
        font.setPointSize(14)

        # 创建一个QWidget作为滚动区域的容器
        self.scrollWidget = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollWidget)  # 注意这里的布局是设置给scrollWidget的

        # 在这里添加供货商复选框，根据数据库中的供货商动态生成
        suppliers = self.parent().get_suppliers()
        for supplier in suppliers:
            checkbox = QCheckBox(supplier)
            checkbox.setFont(font)
            self.supplier_checkboxes.append(checkbox)
            self.scrollLayout.addWidget(checkbox)
        
        self.scrollWidget.setLayout(self.scrollLayout)

        # 创建滚动区域，并将之前创建的widget设置为滚动区域的内容
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)  # 允许滚动区域内容的大小变化
        self.scrollArea.setWidget(self.scrollWidget)

        # 将滚动区域添加到主布局
        self.layout.addWidget(self.scrollArea)

        self.ok_button = QPushButton('确定')
        self.cancel_button = QPushButton('取消')

        self.ok_button.setFont(font)
        self.cancel_button.setFont(font)

        self.layout.addWidget(self.ok_button)
        self.layout.addWidget(self.cancel_button)

        self.ok_button.clicked.connect(self.apply_filter)
        self.cancel_button.clicked.connect(self.close)

        # 不再直接设置self.layout，因为在创建时已经设置
        # self.setLayout(self.layout)

    def apply_filter(self):
        selected_suppliers = [checkbox.text() for checkbox in self.supplier_checkboxes if checkbox.isChecked()]
        if selected_suppliers:
            self.filterApplied.emit(selected_suppliers)
        else:
            self.filterApplied.emit([])
        self.close()

