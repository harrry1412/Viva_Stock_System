from PyQt5.QtCore import QRunnable, pyqtSignal, QObject, Qt
from PyQt5.QtGui import QPixmap
import os

class ImageLoaderSignals(QObject):
    image_loaded = pyqtSignal(int, QPixmap)

class ImageLoader(QRunnable):
    def __init__(self, image_path, index, thumbnail=True):
        super().__init__()
        self.image_path = image_path  # 图片路径直接从外部传入
        self.index = index
        self.thumbnail = thumbnail
        self.signals = ImageLoaderSignals()
        self.is_cancelled = False  # 添加取消标志

    def run(self):
        if self.is_cancelled:
            return  # 如果已经被取消，则直接返回

        if os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            if self.thumbnail:
                pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.signals.image_loaded.emit(self.index, pixmap)

    def cancel(self):
        self.is_cancelled = True  # 提供一个方法来设置取消标志
