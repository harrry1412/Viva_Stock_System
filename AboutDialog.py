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
            "Viva Stock Management System / Viva大仓库库存管理系统\n"
            "版本: 2.6.4\n"
            "作者: Harry\n"
            "版权: © 2023 Haochu Chen\n"
            "描述: Viva库存管理系统，旨在管理并规范化所有增减库存的活动，使得记录清晰易读可追踪。"
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
