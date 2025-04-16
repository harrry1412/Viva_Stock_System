from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QComboBox,
    QLabel, QWidget, QScrollArea, QRadioButton, QButtonGroup
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import sys

class ManageDialog(QDialog):
    def __init__(self, parent=None, user_list=None):
        super().__init__(parent)
        self.setWindowTitle('管理权限设置')

        if getattr(sys, 'frozen', False):
            self.setWindowIcon(QIcon(sys._MEIPASS + '/vivastock.ico'))
        else:
            self.setWindowIcon(QIcon('vivastock.ico'))

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.resize(700, 550)

        # ✅ 确保用上传入的 user_list
        self.user_list = user_list if user_list else []
        self.user_dict = {u['name']: str(u['status']) for u in self.user_list}  # status统一为字符串

        font = QFont()
        font.setPointSize(14)
        main_layout = QVBoxLayout(self)

        # 下拉框选择用户
        top_layout = QHBoxLayout()
        user_label = QLabel("选择用户:")
        user_label.setFont(font)
        self.user_combo = QComboBox()
        self.user_combo.setFont(font)
        self.user_combo.addItems([u['name'] for u in self.user_list])
        self.user_combo.currentIndexChanged.connect(self.on_user_changed)
        top_layout.addWidget(user_label)
        top_layout.addWidget(self.user_combo)
        main_layout.addLayout(top_layout)

        # 用户状态（单选框）
        status_layout = QHBoxLayout()
        status_label = QLabel("用户状态:")
        status_label.setFont(font)
        self.active_radio = QRadioButton("激活")
        self.disabled_radio = QRadioButton("禁用")
        self.active_radio.setFont(font)
        self.disabled_radio.setFont(font)

        self.status_group = QButtonGroup()
        self.status_group.addButton(self.active_radio)
        self.status_group.addButton(self.disabled_radio)

        status_layout.addWidget(status_label)
        status_layout.addWidget(self.active_radio)
        status_layout.addWidget(self.disabled_radio)
        status_layout.addStretch(1)
        main_layout.addLayout(status_layout)

        # 权限列表（复选框）
        permission_layout = QHBoxLayout()
        permission_label = QLabel("修改权限:")
        permission_label.setFont(font)
        permission_layout.addWidget(permission_label)

        self.permission_scroll_widget = QWidget()
        self.permission_scroll_layout = QVBoxLayout(self.permission_scroll_widget)

        self.permissions = [
            "修改产品", "添加产品", "删除产品", "导出数据", "查看日志",
            "管理用户", "上传图片", "库存调整", "价格管理"
        ]

        self.permission_checkboxes = []
        for perm in self.permissions:
            checkbox = QCheckBox(perm)
            checkbox.setFont(font)
            self.permission_checkboxes.append(checkbox)
            self.permission_scroll_layout.addWidget(checkbox)

        self.permission_scroll_area = QScrollArea()
        self.permission_scroll_area.setWidgetResizable(True)
        self.permission_scroll_area.setWidget(self.permission_scroll_widget)
        permission_layout.addWidget(self.permission_scroll_area)
        main_layout.addLayout(permission_layout)

        # 底部按钮
        bottom_layout = QHBoxLayout()
        self.save_button = QPushButton('保存')
        self.cancel_button = QPushButton('取消')
        self.save_button.setFont(font)
        self.cancel_button.setFont(font)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.save_button)
        bottom_layout.addWidget(self.cancel_button)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

        # 连接按钮
        self.save_button.clicked.connect(self.save_permissions)
        self.cancel_button.clicked.connect(self.close)

        # 初始化第一项
        if self.user_list:
            self.update_user_status(self.user_list[0]['name'])

    def on_user_changed(self, index):
        username = self.user_combo.itemText(index)
        self.update_user_status(username)

    def update_user_status(self, username):
        status = self.user_dict.get(username, "1")
        print(f"[Debug] 当前选中用户: {username}, 状态: {status}")

        # 先清除状态再设定，确保 UI 正确刷新
        self.active_radio.setAutoExclusive(False)
        self.disabled_radio.setAutoExclusive(False)
        self.active_radio.setChecked(False)
        self.disabled_radio.setChecked(False)
        self.active_radio.setAutoExclusive(True)
        self.disabled_radio.setAutoExclusive(True)

        if status == "1":
            self.active_radio.setChecked(True)
        else:
            self.disabled_radio.setChecked(True)

    def save_permissions(self):
        selected_user = self.user_combo.currentText()
        selected_perms = [cb.text() for cb in self.permission_checkboxes if cb.isChecked()]
        status = "1" if self.active_radio.isChecked() else "0"
        print(f"[保存] 用户: {selected_user}, 状态: {status}, 权限: {selected_perms}")
        self.close()
