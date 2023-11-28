from PyQt5.QtWidgets import QLabel, QMenu, QAction, QApplication
from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import Qt

class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

    def showContextMenu(self, position):
        contextMenu = QMenu(self)
        copyAction = QAction("复制", self)
        copyAction.triggered.connect(self.copyImage)
        contextMenu.addAction(copyAction)
        contextMenu.exec_(self.mapToGlobal(position))

    def copyImage(self):
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(self.pixmap())