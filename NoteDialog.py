from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPlainTextEdit, QPushButton, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt



class NoteDialog(QDialog):
    def __init__(self, parent=None, rug_id="", note="", logged=0):
        super().__init__(parent)
        if (logged==1):
            self.setWindowTitle('备注')
        else:
            self.setWindowTitle('备注（未登录，无法编辑）')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(600, 400)  # 调整对话框的大小
        self.layout = QVBoxLayout()

        self.note_label = QLabel('备注:')
        self.note_input = QPlainTextEdit()  # 使用 QPlainTextEdit
        self.note_input.setMinimumHeight(200)  # 增加文本输入框的最小高度
        # 设置文本框的只读属性，取决于logged的值
        self.note_input.setReadOnly(logged != 1)
        self.save_button = QPushButton('保存')
        self.cancel_button = QPushButton('取消')

        font = QFont()
        font.setPointSize(16)
        self.note_label.setFont(font)
        self.note_input.setFont(font)
        self.save_button.setFont(font)
        self.cancel_button.setFont(font)

        self.layout.addWidget(self.note_label)
        self.layout.addWidget(self.note_input)
        button_layout = QHBoxLayout()
        self.save_button.setFixedSize(100, 56)
        self.cancel_button.setFixedSize(100, 56)
        if (logged==1):
            button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.setLayout(self.layout)

        self.note_input.setPlainText(note)  # 使用 setPlainText 设置多行文本
        self.rug_id = rug_id

    def get_new_note(self):
        return self.note_input.toPlainText()  # 使用 toPlainText 获取多行文本