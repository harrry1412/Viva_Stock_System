import sys
import os
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QApplication
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("关于")
        self.setWindowIcon(QIcon(self.getIconPath()))
        self.resize(800, 600)

        about_text = (
            "软件名称: 你的软件\n"
            "版本: 1.0.0\n"
            "作者: 你的名字\n"
            "版权: © 2023 你的名字\n"
            "描述: 这是我的软件，用于......"
        )

        label = QLabel(about_text, self)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("SansSerif", 12))

        layout = QVBoxLayout(self)
        layout.addWidget(label)

    def getIconPath(self):
        if getattr(sys, 'frozen', False):
            # 打包后的情况
            application_path = sys._MEIPASS
        else:
            # 从源代码运行的情况
            application_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(application_path, 'vivastock.ico')

# 测试代码
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AboutDialog()
    ex.show()
    sys.exit(app.exec_())
