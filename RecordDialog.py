from PyQt5.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QTextEdit, QPushButton
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class RecordDialog(QDialog):
    def __init__(self, parent=None, rug_id="", records=""):
        super().__init__(parent)
        self.setWindowTitle('记录')
        # 移除帮助按钮，并添加最大化/最小化按钮
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        
        # 设置一个合适的最小尺寸
        self.setMinimumSize(800, 600)

        self.layout = QVBoxLayout()

        self.record_label = QLabel('记录:')
        self.record_display = QTextEdit()
        self.record_display.setMinimumHeight(200)
        self.record_display.setReadOnly(True)  # 设置为只读，因为这只是用来显示记录的

        font = QFont()
        font.setPointSize(16)
        self.record_label.setFont(font)
        self.record_display.setFont(font)

        self.close_button = QPushButton('关闭')
        self.close_button.setFont(font)
        self.close_button.setFixedSize(100, 56)
        self.close_button.clicked.connect(self.reject)  # 直接关闭对话框，无需保存

        self.layout.addWidget(self.record_label)
        self.layout.addWidget(self.record_display)
        self.layout.addWidget(self.close_button)

        self.setLayout(self.layout)

        self.record_display.setPlainText(records)  # 显示记录
        self.rug_id = rug_id