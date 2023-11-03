from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView


class RecordDialog(QDialog):
    def __init__(self, parent=None, rug_id="", records=[]):
        super().__init__(parent)
        self.setWindowTitle('记录')
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        self.setMinimumSize(800, 600)

        self.layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # 假设有四列数据
        self.table.setHorizontalHeaderLabels(['型号', '日期', '修改人', '内容'])
        self.table.setRowCount(len(records))
        
        for i, record in enumerate(records):
            self.table.setItem(i, 0, QTableWidgetItem(record[0]))
            # 假设 record[1] 是一个 datetime.date 对象
            date_str = record[1].strftime('%Y-%m-%d')  # 将日期转换为字符串
            self.table.setItem(i, 1, QTableWidgetItem(date_str))
            self.table.setItem(i, 2, QTableWidgetItem(record[2]))
            self.table.setItem(i, 3, QTableWidgetItem(record[3]))
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # 自动调整列宽
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置表格内容不可编辑
        
        font = QFont()
        font.setPointSize(16)
        self.table.setFont(font)
        
        self.close_button = QPushButton('关闭')
        self.close_button.setFont(font)
        self.close_button.setFixedSize(100, 56)
        self.close_button.clicked.connect(self.reject)
        
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.close_button)

        self.setLayout(self.layout)
        self.rug_id = rug_id
