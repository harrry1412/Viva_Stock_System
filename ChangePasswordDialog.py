from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QMessageBox, QLabel
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import sys
import os

class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None, username=None, db_manager=None):
        super().__init__(parent)
        self.username = username
        self.db_manager = db_manager

        self.setWindowTitle('修改密码')
        if getattr(sys, 'frozen', False):
            self.setWindowIcon(QIcon(os.path.join(sys._MEIPASS, 'vivastock.ico')))
        else:
            self.setWindowIcon(QIcon('vivastock.ico'))

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(400, 300)
        self.layout = QVBoxLayout()

        font = QFont()
        font.setPointSize(16)

        # 原密码
        self.old_pwd_label = QLabel("原密码:")
        self.old_pwd_input = QLineEdit()
        self.old_pwd_input.setEchoMode(QLineEdit.Password)
        self.old_pwd_label.setFont(font)
        self.old_pwd_input.setFont(font)

        # 新密码
        self.new_pwd_label = QLabel("新密码:")
        self.new_pwd_input = QLineEdit()
        self.new_pwd_input.setEchoMode(QLineEdit.Password)
        self.new_pwd_label.setFont(font)
        self.new_pwd_input.setFont(font)

        # 确认密码
        self.confirm_pwd_label = QLabel("确认新密码:")
        self.confirm_pwd_input = QLineEdit()
        self.confirm_pwd_input.setEchoMode(QLineEdit.Password)
        self.confirm_pwd_label.setFont(font)
        self.confirm_pwd_input.setFont(font)

        self.layout.addWidget(self.old_pwd_label)
        self.layout.addWidget(self.old_pwd_input)
        self.layout.addWidget(self.new_pwd_label)
        self.layout.addWidget(self.new_pwd_input)
        self.layout.addWidget(self.confirm_pwd_label)
        self.layout.addWidget(self.confirm_pwd_input)

        self.submit_button = QPushButton('确认')
        self.cancel_button = QPushButton('取消')
        self.submit_button.setFont(font)
        self.cancel_button.setFont(font)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout)

        self.submit_button.clicked.connect(self.change_password)
        self.cancel_button.clicked.connect(self.reject)

        self.setLayout(self.layout)

    def change_password(self):
        old_pwd = self.old_pwd_input.text()
        new_pwd = self.new_pwd_input.text()
        confirm_pwd = self.confirm_pwd_input.text()

        if not old_pwd or not new_pwd or not confirm_pwd:
            QMessageBox.warning(self, "错误", "所有字段不能为空")
            return

        # === 1. 验证原密码是否正确 ===
        correct = self.db_manager.verify_password(self.username, old_pwd)
        if correct == -1:
            QMessageBox.critical(self, "错误", "数据库连接失败")
            return
        if not correct:
            QMessageBox.warning(self, "错误", "原密码错误")
            return

        # === 2. 判断新密码与确认密码是否一致 ===
        if new_pwd != confirm_pwd:
            QMessageBox.warning(self, "错误", "两次输入的新密码不一致")
            return

        # === 3. 判断新旧密码是否相同 ===
        if new_pwd == old_pwd:
            QMessageBox.warning(self, "错误", "新密码不能与原密码相同")
            return

        # === 4. 判断新密码长度是否符合要求 ===
        if len(new_pwd) < 3:
            QMessageBox.warning(self, "错误", "新密码长度必须至少为3个字符")
            return

        # === 5. 更新密码 ===
        success = self.db_manager.update_password(self.username, new_pwd)
        if success == -1:
            QMessageBox.critical(self, "错误", "数据库连接失败")
        elif success == 0:
            QMessageBox.warning(self, "错误", "密码修改失败")
        else:
            QMessageBox.information(self, "成功", "密码修改成功")
            self.accept()

