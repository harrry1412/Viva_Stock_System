from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QRadioButton, QComboBox, QLabel, QButtonGroup
import sys

class TestDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("状态切换测试")
        self.resize(300, 150)

        self.user_dict = {"Alice": "1", "Bob": "0", "Charlie": "1"}

        layout = QVBoxLayout()

        self.combo = QComboBox()
        self.combo.addItems(list(self.user_dict.keys()))
        self.combo.currentTextChanged.connect(self.update_status)
        layout.addWidget(QLabel("选择用户:"))
        layout.addWidget(self.combo)

        self.radio_active = QRadioButton("激活")
        self.radio_disabled = QRadioButton("禁用")
        self.group = QButtonGroup()
        self.group.addButton(self.radio_active)
        self.group.addButton(self.radio_disabled)

        layout.addWidget(self.radio_active)
        layout.addWidget(self.radio_disabled)

        self.setLayout(layout)
        self.update_status(self.combo.currentText())

    def update_status(self, username):
        status = self.user_dict.get(username, "1")
        print(f"更新状态: {username} => {status}")
        if status == "1":
            self.radio_active.setChecked(True)
        else:
            self.radio_disabled.setChecked(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = TestDialog()
    dlg.exec_()
