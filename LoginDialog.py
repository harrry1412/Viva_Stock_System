from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QMessageBox, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('登录')
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

        self.login_button = QPushButton('登录')
        self.cancel_button = QPushButton('取消')

        self.login_button.setFont(font)
        self.cancel_button.setFont(font)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout)

        # 将登录按钮的点击事件连接到 accept 方法，这样点击后会关闭对话框并返回 QDialog.Accepted
        self.login_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.setLayout(self.layout)

    def get_username(self):
        return self.username_input.text()

    def get_password(self):
        return self.password_input.text()
