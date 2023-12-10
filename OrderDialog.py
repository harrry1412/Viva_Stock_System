from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QRadioButton, QPushButton, QButtonGroup, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal


class OrderDialog(QDialog):
    # 定义一个信号，当排序应用时发出，发送排序字段和方向
    orderApplied = pyqtSignal(str, str)
    orderRestored = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('排序')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(300, 300)
        self.layout = QVBoxLayout()

        font = QFont()
        font.setPointSize(16)

        # 创建单选按钮并添加到按钮组，用于选择排序字段
        self.button_group = QButtonGroup(self)
        self.model_rbtn = QRadioButton('型号')
        self.supplier_rbtn = QRadioButton('供货商')
        self.quantity_rbtn = QRadioButton('数量')
        self.model_rbtn.setFont(font)
        self.supplier_rbtn.setFont(font)
        self.quantity_rbtn.setFont(font)

        self.button_group.addButton(self.model_rbtn)
        self.button_group.addButton(self.supplier_rbtn)
        self.button_group.addButton(self.quantity_rbtn)

        # 将单选按钮添加到布局中
        self.layout.addWidget(self.model_rbtn)
        self.layout.addWidget(self.supplier_rbtn)
        self.layout.addWidget(self.quantity_rbtn)

        # 创建单选按钮用于选择排序方向
        self.order_direction_group = QButtonGroup(self)
        self.asc_rbtn = QRadioButton('升序')
        self.desc_rbtn = QRadioButton('降序')
        self.quantity_rbtn.setChecked(True) # 默认设置为数量排序
        self.desc_rbtn.setChecked(True)  # 默认设置为升序

        self.asc_rbtn.setFont(font)
        self.desc_rbtn.setFont(font)
        self.order_direction_group.addButton(self.asc_rbtn)
        self.order_direction_group.addButton(self.desc_rbtn)

        # 创建一个水平布局用于包含排序方向单选按钮
        direction_layout = QHBoxLayout()
        direction_layout.addWidget(self.asc_rbtn)
        direction_layout.addWidget(self.desc_rbtn)

        # 将排序方向布局添加到主布局
        self.layout.addLayout(direction_layout)

        # 确定和取消按钮
        self.ok_button = QPushButton('确定')
        self.cancel_button = QPushButton('取消')
        self.restore_button = QPushButton('恢复')

        font = QFont()
        font.setPointSize(16)
        self.ok_button.setFont(font)
        self.cancel_button.setFont(font)
        self.restore_button.setFont(font)

        # 将按钮添加到布局中
        self.layout.addWidget(self.ok_button)
        self.layout.addWidget(self.cancel_button)
        self.layout.addWidget(self.restore_button)

        # 连接信号和槽
        self.ok_button.clicked.connect(self.apply_order)
        self.cancel_button.clicked.connect(self.close)
        self.restore_button.clicked.connect(self.restore)

        self.setLayout(self.layout)

    def restore(self):
        self.orderRestored.emit()
        self.close()

    def apply_order(self):
        # 获取选中的排序字段
        order_field = None
        if self.model_rbtn.isChecked():
            order_field = 'id'
        elif self.supplier_rbtn.isChecked():
            order_field = 'supplier'
        elif self.quantity_rbtn.isChecked():
            order_field = 'qty'

        # 获取选中的排序方向
        order_direction = 'ASC' if self.asc_rbtn.isChecked() else 'DESC'

        # 如果选择了排序字段，则发出信号
        if order_field:
            self.orderApplied.emit(order_field, order_direction)
        else:
            self.orderApplied.emit('none', 'ASC')

        self.close()
