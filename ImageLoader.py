from PyQt5.QtCore import QThread, pyqtSignal, Qt, QObject
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
import os

class ImageLoader(QThread):
    # 创建一个信号，当图片加载完毕后发射
    image_loaded = pyqtSignal(int, QPixmap)

    def __init__(self, image_path, index):
        super().__init__()
        self.image_path = image_path
        self.index = index

    def run(self):
        if os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            thumbnail = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_loaded.emit(self.index, thumbnail)  # 发射信号，传递索引和缩略图
