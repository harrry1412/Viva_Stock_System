from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import pyqtSignal, QTimer

class ClickableLineEdit(QLineEdit):
    clicked = pyqtSignal()  # 自定义信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_selected = False  # 跟踪文本是否被全选

    def mousePressEvent(self, event):
        if self.is_selected:
            # 如果文本已经被全选，则取消选择并将光标移动到点击位置
            super().mousePressEvent(event)
            self.is_selected = False
        else:
            # 如果文本未全选，则先执行默认操作，然后全选文本
            super().mousePressEvent(event)
            QTimer.singleShot(0, self.select_all_text)

    def select_all_text(self):
        self.selectAll()
        self.is_selected = True  # 更新状态表示文本已被全选