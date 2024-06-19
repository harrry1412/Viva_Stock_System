from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QBrush, QLinearGradient, QColor, QFontMetrics
import sys
import os

class LoadingDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.main_message = 'Viva大仓库库存系统加载中，请稍候...'
        self.messages = [
            '正在初始化...',
            '正在连接数据库...',
            '正在验证用户...',
            '加载配置...',
            '准备界面...'
        ]
        self.current_message_index = 0

        # 获取DPI缩放比例
        screen = QApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch()
        scale_factor = dpi / 96.0  # 96是标准DPI

        # 设置无边框窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # 设置对话框的窗口图标
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(application_path, 'vivastock.ico')
        self.setWindowIcon(QIcon(icon_path))

        # 添加所有子组件和布局
        layout = QVBoxLayout()

        # Main message
        self.main_label = QLabel(self.main_message)
        main_font = QFont("Arial", int(16 * scale_factor))
        self.main_label.setFont(main_font)
        self.main_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.main_label)

        # 图标
        self.icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        self.icon_label.setPixmap(pixmap.scaled(int(64 * scale_factor), int(64 * scale_factor), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)

        # Secondary message
        self.secondary_label = QLabel(self.messages[self.current_message_index])
        secondary_font = QFont("Arial", int(10 * scale_factor))
        self.secondary_label.setFont(secondary_font)
        self.secondary_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.secondary_label)

        # 设计者信息
        self.designer_label = QLabel("Designed by Harry")
        designer_font = QFont("Arial", int(8 * scale_factor))
        self.designer_label.setFont(designer_font)
        self.designer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.designer_label)

        self.setLayout(layout)

        # 使用 QFontMetrics 计算所需窗口大小
        font_metrics = QFontMetrics(main_font)
        width = font_metrics.horizontalAdvance(self.main_message) + 40
        height = font_metrics.height() * 5 + int(64 * scale_factor) + 80

        # 设置窗口大小策略和大小
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(width, height)

        # 设置背景样式
        self.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: black;
            }
        """)

        # 创建定时器定期更新消息
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_message)
        self.timer.start(1000)  # 每1秒更新一次

    def update_message(self):
        if self.current_message_index < len(self.messages) - 1:
            self.current_message_index += 1
            self.secondary_label.setText(self.messages[self.current_message_index])
        else:
            self.timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, Qt.white)
        gradient.setColorAt(1, QColor(135, 206, 250))  # 调整后的浅蓝色
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.transparent)
        painter.drawRect(self.rect())  # 使用 drawRect 而不是 drawRoundedRect 以保持方角
