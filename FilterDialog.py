from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QScrollArea, QWidget
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, pyqtSignal
import sys

class FilterDialog(QDialog):
    filterApplied = pyqtSignal(list, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('筛选供货商与产品类型')
        if getattr(sys, 'frozen', False):
            self.setWindowIcon(QIcon(sys._MEIPASS + '/vivastock.ico'))
        else:
            self.setWindowIcon(QIcon('vivastock.ico'))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.resize(600, 400)  # 修改初始大小以适应两列
        self.layout = QVBoxLayout(self)

        self.supplier_checkboxes = []
        self.category_checkboxes = []

        font = QFont()
        font.setPointSize(14)

        # 水平布局用于放置两个滚动区域
        self.hLayout = QHBoxLayout()

        # 创建供货商滚动区域
        self.supplierScrollWidget = QWidget()
        self.supplierScrollLayout = QVBoxLayout(self.supplierScrollWidget)
        suppliers = self.parent().get_suppliers()
        for supplier in suppliers:
            display_text = "空白" if supplier is None or not supplier.strip() else supplier
            checkbox = QCheckBox(display_text)
            checkbox.setFont(font)
            self.supplier_checkboxes.append(checkbox)
            self.supplierScrollLayout.addWidget(checkbox)
        self.supplierScrollWidget.setLayout(self.supplierScrollLayout)
        self.supplierScrollArea = QScrollArea()
        self.supplierScrollArea.setWidgetResizable(True)
        self.supplierScrollArea.setWidget(self.supplierScrollWidget)

        # 创建产品类型滚动区域
        self.categoryScrollWidget = QWidget()
        self.categoryScrollLayout = QVBoxLayout(self.categoryScrollWidget)
        categories=self.parent().get_categories()
        #categories=['Sofa', 'Lamp', 'Rugs', 'Chair']
        for category in categories:
            display_text = "空白" if category is None or not category.strip() else category
            checkbox = QCheckBox(display_text)
            checkbox.setFont(font)
            self.category_checkboxes.append(checkbox)
            self.categoryScrollLayout.addWidget(checkbox)
        self.categoryScrollWidget.setLayout(self.categoryScrollLayout)
        self.categoryScrollArea = QScrollArea()
        self.categoryScrollArea.setWidgetResizable(True)
        self.categoryScrollArea.setWidget(self.categoryScrollWidget)

        # 将两个滚动区域添加到水平布局
        self.hLayout.addWidget(self.supplierScrollArea)
        self.hLayout.addWidget(self.categoryScrollArea)

        # 将水平布局添加到主布局
        self.layout.addLayout(self.hLayout)

        self.ok_button = QPushButton('确定')
        self.cancel_button = QPushButton('取消')
        self.ok_button.setFont(font)
        self.cancel_button.setFont(font)
        self.layout.addWidget(self.ok_button)
        self.layout.addWidget(self.cancel_button)

        self.ok_button.clicked.connect(self.apply_filter)
        self.cancel_button.clicked.connect(self.close)

    def apply_filter(self):
        selected_suppliers = [checkbox.text() for checkbox in self.supplier_checkboxes if checkbox.isChecked()]
        selected_categories = [checkbox.text() for checkbox in self.category_checkboxes if checkbox.isChecked()]
        self.filterApplied.emit(selected_suppliers, selected_categories)
        self.close()
