from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton, QComboBox,
    QLabel, QWidget, QScrollArea, QRadioButton, QButtonGroup, QMessageBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from AddUserDialog import AddUserDialog
import sys

class ManageDialog(QDialog):
    def __init__(self, parent=None, user=None, user_list=None, db_manager=None):
        super().__init__(parent)
        self.setWindowTitle('管理权限设置')

        if getattr(sys, 'frozen', False):
            self.setWindowIcon(QIcon(sys._MEIPASS + '/vivastock.ico'))
        else:
            self.setWindowIcon(QIcon('vivastock.ico'))

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.resize(700, 550)

        self.db_manager=db_manager
        self.user_list = user_list if user_list else []
        if user:
            self.user_list = [u for u in self.user_list if u['name'] != user and u['name'] != 'Admin']

        self.user_dict = {u['name']: str(u['status']) for u in self.user_list}  # status统一为字符串

        font = QFont()
        font.setPointSize(14)
        main_layout = QVBoxLayout(self)

        # 顶部添加按钮区域
        add_user_layout = QHBoxLayout()
        self.add_user_button = QPushButton("添加用户")
        self.add_user_button.setFont(font)
        self.add_user_button.clicked.connect(self.show_add_user_dialog)
        add_user_layout.addStretch()
        add_user_layout.addWidget(self.add_user_button)
        main_layout.addLayout(add_user_layout)


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
        self.active_radio.toggled.connect(self.toggle_permission_area)
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

        self.permission_mapping = {
            "edit_note": "修改备注",
            "edit_qty": "修改数量",
            "delete_record": "删除记录",
            "add_product": "添加新品",
            "edit_product": "修改产品",
            "manage_user": "管理用户"
        }

        # 构造复选框
        self.permission_checkboxes = {}
        for key, label in self.permission_mapping.items():
            checkbox = QCheckBox(label)
            checkbox.setFont(font)
            self.permission_checkboxes[key] = checkbox
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

    def show_add_user_dialog(self):
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            username, password = dialog.get_user_info()

            # 校验用户名和密码
            if not username or not password:
                QMessageBox.warning(self, "错误", "用户名和密码不能为空")
                return
            if username.lower() == "admin":
                QMessageBox.warning(self, "错误", "用户名不能为 admin")
                return
            if len(password) < 3:
                QMessageBox.warning(self, "错误", "密码不能少于 3 位")
                return

            # 插入用户（默认禁用）
            success_user = self.db_manager.insert_user(username, password, status="0")

            # 插入该用户的所有权限，stat=0
            all_perms = list(self.permission_mapping.keys())
            success_perm = self.db_manager.insert_user_permissions_default(username, all_perms)

            if success_user and success_perm:
                QMessageBox.information(self, "成功", f"用户 {username} 已添加（默认禁用）")
                # 添加到当前下拉框列表中
                self.user_list.append({"name": username, "status": "0"})
                self.user_dict[username] = "0"
                self.user_combo.addItem(username)
            else:
                QMessageBox.critical(self, "失败", "添加用户失败，请检查数据库")



    def toggle_permission_area(self, enabled):
        for checkbox in self.permission_checkboxes.values():
            checkbox.setEnabled(enabled)

    def on_user_changed(self, index):
        username = self.user_combo.itemText(index)
        self.update_user_status(username)

    def update_user_status(self, username):
        # 设置激活/禁用状态（仍使用 self.user_dict 或你传入的 user_list）
        status = self.user_dict.get(username, "1")
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

        self.toggle_permission_area(self.active_radio.isChecked())

        # 清除所有权限勾选
        for cb in self.permission_checkboxes.values():
            cb.setChecked(False)

        permission_status =self.db_manager.get_permissions_by_user(username)

        for key, checkbox in self.permission_checkboxes.items():
            if permission_status.get(key, 0) == 1:
                checkbox.setChecked(True)

    def save_permissions(self):
        selected_user = self.user_combo.currentText()
        status = "1" if self.active_radio.isChecked() else "0"

        if status == "1":
            selected_perms = {
                key: 1 if checkbox.isChecked() else 0
                for key, checkbox in self.permission_checkboxes.items()
            }
        else:
            # 如果禁用，所有权限设为0
            selected_perms = {key: 0 for key in self.permission_checkboxes}

        self.db_manager.update_user_permissions(selected_user, selected_perms)
        self.db_manager.update_user_status(selected_user, status)

        print(f"[保存] 用户: {selected_user}, 状态: {status}, 权限: {selected_perms}")
        self.close()




