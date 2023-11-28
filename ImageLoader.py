from PyQt5.QtCore import QRunnable, pyqtSignal, QObject, Qt
from PyQt5.QtGui import QPixmap
import os

'''
# 为了发射信号，我们需要一个QObject，因为QRunnable不是QObject
class ImageLoaderSignals(QObject):
    image_loaded = pyqtSignal(int, QPixmap)

class ImageLoader(QRunnable):

    def __init__(self, image_path, index):
        super().__init__()
        path='\\\\VIVA303-WORK\\Viva店面共享\\StockImg\\'
        if(image_path is None):
            self.image_path=''
        else:
            self.image_path = path+image_path
        self.index = index
        self.signals = ImageLoaderSignals()

    def run(self):
        if os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            thumbnail = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.signals.image_loaded.emit(self.index, thumbnail)  # 发射信号，传递索引和缩略图
'''
class ImageLoaderSignals(QObject):
    image_loaded = pyqtSignal(int, QPixmap)


class ImageLoader(QRunnable):
    def __init__(self, image_path, index, thumbnail=True):
        super().__init__()
        self.image_path = image_path  # 图片路径直接从外部传入
        self.index = index
        self.thumbnail = thumbnail
        self.signals = ImageLoaderSignals()

    def run(self):
        if os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            if self.thumbnail:
                pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.signals.image_loaded.emit(self.index, pixmap)


