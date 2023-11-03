from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout, QMessageBox, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class EditQuantityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('编辑数量')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(400, 225)
        self.layout = QVBoxLayout()

        input_layout = QHBoxLayout()

        self.decrement_button = QPushButton('-')
        self.new_quantity_input = QLineEdit()
        self.increment_button = QPushButton('+')
        # 添加记录文本输入框
        self.record_label=QLabel('调货细节/原因：')
        self.record_input = QLineEdit()

        font = QFont()
        font.setPointSize(16)
        self.new_quantity_input.setFont(font)
        self.decrement_button.setFont(font)
        self.increment_button.setFont(font)
        self.record_label.setFont(font)
        self.record_input.setFont(font)
        

        button_size = 40  # 设置按钮的宽度和高度

        self.decrement_button.setFixedSize(button_size, button_size)
        self.increment_button.setFixedSize(button_size, button_size)

        input_layout.addWidget(self.decrement_button)
        input_layout.addWidget(self.new_quantity_input)
        input_layout.addWidget(self.increment_button)

        self.layout.addLayout(input_layout)
        self.layout.addWidget(self.record_label)
        self.layout.addWidget(self.record_input)

        self.ok_button = QPushButton('确认')
        self.cancel_button = QPushButton('取消')

        self.ok_button.setFont(font)
        self.cancel_button.setFont(font)

        self.layout.addWidget(self.ok_button)
        self.layout.addWidget(self.cancel_button)

        self.ok_button.clicked.connect(self.save_changes)
        self.cancel_button.clicked.connect(self.reject)
        self.increment_button.clicked.connect(self.increment_quantity)
        self.decrement_button.clicked.connect(self.decrement_quantity)

        # 连接回车键事件
        self.new_quantity_input.returnPressed.connect(self.save_changes)
        self.record_input.returnPressed.connect(self.save_changes)

        self.setLayout(self.layout)

    def get_new_quantity(self):
        return self.new_quantity_input.text()

    def get_record(self):
        return self.record_input.text()

    def increment_quantity(self):
        current_quantity = int(self.new_quantity_input.text())
        new_quantity = current_quantity + 1
        self.new_quantity_input.setText(str(new_quantity))

    def decrement_quantity(self):
        current_quantity = int(self.new_quantity_input.text())
        new_quantity = current_quantity - 1
        self.new_quantity_input.setText(str(new_quantity))

    def save_changes(self):
        new_quantity = self.get_new_quantity()
        record = self.get_record()

        if record:
            # 在这里保存更改或同步到数据库
            print(f"保存数量更改: {new_quantity}")
            print(f"记录: {record}")
            self.accept()
        else:
            QMessageBox.warning(self, '警告', '记录不能为空')