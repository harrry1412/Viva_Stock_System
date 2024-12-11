from PyQt5.QtCore import Qt
import sys
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu, QMessageBox)

class RecordDialog(QDialog):
    def __init__(self, parent=None, rug_id="", records=[], row=0):
        super().__init__(parent)
        self.setWindowTitle('记录')
        if getattr(sys, 'frozen', False):
            self.setWindowIcon(QIcon(sys._MEIPASS + '/vivastock.ico'))
        else:
            self.setWindowIcon(QIcon('vivastock.ico'))
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinMaxButtonsHint)
        self.setMinimumSize(800, 600)

        self.layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(5)  
        self.table.setHorizontalHeaderLabels(['型号', '进出货日期', '修改人', '内容', 'Edittime'])
        self.table.setRowCount(len(records))

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.showContextMenu)

        self.table.setSelectionMode(QAbstractItemView.SingleSelection)

        self.rug_row=row
        self.rug_id=rug_id

        # 添加记录到表格中
        for i, record in enumerate(records):
            item = QTableWidgetItem(record[0])
            item.setTextAlignment(Qt.AlignTop)  # 设置文本顶部对齐
            item.setFlags(item.flags() | Qt.TextWrapAnywhere)  # 允许在任何地方换行
            self.table.setItem(i, 0, item)
            date_str = record[1].strftime('%Y-%m-%d')  # 将日期转换为字符串
            self.table.setItem(i, 1, QTableWidgetItem(date_str))
            self.table.setItem(i, 2, QTableWidgetItem(record[2]))
            self.table.setItem(i, 3, QTableWidgetItem(f"{record[4]} -> {record[5]}: {record[3]}"))
            self.table.setItem(i, 4, QTableWidgetItem(str(record[6])))
            self.table.setColumnHidden(4, True)
            self.table.resizeRowToContents(i)

        # 设置前三列的宽度和最后一列的伸缩策略
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        # 设置表格内容不可编辑
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

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

    def showContextMenu(self, pos):
        index = self.table.indexAt(pos)
        # 确保点击位置有效，且为第一行的第3列
        if index.isValid() and index.row() == 0 and index.column() == 3:
            contextMenu = QMenu(self)
            deleteAction = contextMenu.addAction("删除记录")
            action = contextMenu.exec_(self.table.viewport().mapToGlobal(pos))
            if action == deleteAction:
                self.delete_record(index.row())
        else:
            pass

    
    def delete_record(self, record_row):
        editdate = self.table.item(record_row, 4).text()
        isCreateRecord=0
        print(self.table.item(record_row, 3).text())
        if ('新增产品' in self.table.item(record_row, 3).text()):
            isCreateRecord=1
        success = self.parent().delete_record(self.rug_id, editdate, self.rug_row, isCreateRecord)
        
        if success:
            self.table.removeRow(record_row)
            self.parent().update_quantity_no_record(self.rug_id, self.rug_row)
