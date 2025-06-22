from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QMessageBox, QLabel
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import sys

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('添加新用户')
        if getattr(sys, 'frozen', False):
            self.setWindowIcon(QIcon(sys._MEIPASS + '/vivastock.ico'))
        else:
            self.setWindowIcon(QIcon('vivastock.ico'))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(400, 225)
        self.layout = QVBoxLayout()

        font = QFont()
        font.setPointSize(16)

        # 用户名
        self.username_label = QLabel("用户名:")
        self.username_input = QLineEdit()
        self.username_label.setFont(font)
        self.username_input.setFont(font)

        # 密码
        self.password_label = QLabel("密码:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_label.setFont(font)
        self.password_input.setFont(font)

        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)

        # 按钮
        self.add_button = QPushButton('添加')
        self.cancel_button = QPushButton('取消')
        self.add_button.setFont(font)
        self.cancel_button.setFont(font)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)

        # 连接按钮事件
        self.add_button.clicked.connect(self.on_add_clicked)
        self.cancel_button.clicked.connect(self.reject)

    def on_add_clicked(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "输入错误", "用户名和密码不能为空")
            return
        self.accept()

    def get_user_info(self):
        return self.username_input.text().strip(), self.password_input.text().strip()
