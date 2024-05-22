from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPlainTextEdit, QPushButton, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor



class NoteDialog(QDialog):
    def __init__(self, parent=None, rug_id="", note="", permission_level=0):
        super().__init__(parent)
        if permission_level == 2:
            self.setWindowTitle('备注')
        elif permission_level == 1:
            self.setWindowTitle('备注（账户权限不足，无法编辑）')
        else:
            self.setWindowTitle('备注（未登录，无法编辑）')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(600, 400) 
        self.layout = QVBoxLayout()

        self.note_label = QLabel('备注:')
        self.note_input = QPlainTextEdit() 
        self.note_input.setMinimumHeight(200)
        # set read only, depends on permission level
        if permission_level !=2:
            self.note_input.setReadOnly(True)
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
        if (permission_level==2):
            button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.setLayout(self.layout)

        self.note_input.setPlainText(note)  # 使用 setPlainText 设置多行文本
        self.note_input.moveCursor(QTextCursor.End)
        self.rug_id = rug_id

    def get_new_note(self):
        return self.note_input.toPlainText()  # 使用 toPlainText 获取多行文本