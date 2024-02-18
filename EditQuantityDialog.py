from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLineEdit, QHBoxLayout, QMessageBox, QLabel, QDateEdit, QWidget
)
import sys
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QDate


class CustomDateEdit(QWidget):
    def __init__(self, parent=None):
        super(CustomDateEdit, self).__init__(parent)

        self.layout = QVBoxLayout(self)
        self.dateEdit = QDateEdit(self)
        self.lineEdit = QLineEdit(self)
        self.choseDate=0

        font = QFont()
        font.setPointSize(16)
        self.dateEdit.setFont(font)
        self.lineEdit.setFont(font)

        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setDisplayFormat("yyyy-MM-dd")
        self.dateEdit.hide()  # Initially hide the dateEdit

        self.layout.addWidget(self.lineEdit)
        self.layout.addWidget(self.dateEdit)

        self.lineEdit.setReadOnly(True)
        self.lineEdit.mousePressEvent = self.showCalendar
        self.dateEdit.dateChanged.connect(self.onDateChanged)

    def showCalendar(self, event):
        self.dateEdit.setDate(QDate.currentDate())
        self.dateEdit.show()
        self.dateEdit.setFocus()
        self.lineEdit.hide()
        self.choseDate=1

    def onDateChanged(self, date):
        self.lineEdit.setText(date.toString("yyyy-MM-dd"))
        self.dateEdit.hide()
        self.lineEdit.show()

    def date(self):
        return self.dateEdit.date()

    def setDate(self, date):
        self.dateEdit.setDate(date)
        self.lineEdit.setText(date.toString("yyyy-MM-dd"))

    def setCalendarPopup(self, enable):
        self.dateEdit.setCalendarPopup(enable)


class EditQuantityDialog(QDialog):
    def __init__(self, parent=None, current_quantity=''):
        super().__init__(parent)
        self.setWindowTitle('编辑数量')
        if getattr(sys, 'frozen', False):
            self.setWindowIcon(QIcon(sys._MEIPASS + '/vivastock.ico'))
        else:
            self.setWindowIcon(QIcon('vivastock.ico'))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(500, 400)
        self.layout = QVBoxLayout()

        input_layout = QHBoxLayout()

        self.title_label = QLabel('请在下方输入更新后的数量：')
        self.decrement_button = QPushButton('-')
        self.head_label = QLabel('当前数量：')
        self.new_quantity_input = QLineEdit()
        self.new_quantity_input.setText(current_quantity)
        self.increment_button = QPushButton('+')
        # 添加记录文本输入框
        self.record_label=QLabel('调货细节/原因：')
        self.record_input = QLineEdit()
        # 添加日期编辑器
        self.date_label = QLabel('进出货日期：')
        self.date_input = CustomDateEdit()

        font = QFont()
        font.setPointSize(16)
        self.title_label.setFont(font)
        self.new_quantity_input.setFont(font)
        self.decrement_button.setFont(font)
        self.head_label.setFont(font)
        self.increment_button.setFont(font)
        self.record_label.setFont(font)
        self.record_input.setFont(font)
        self.date_input.setCalendarPopup(True)
        self.date_label.setFont(font)
        self.date_input.setFont(font)
        

        button_size = 40  # 设置按钮的宽度和高度

        self.decrement_button.setFixedSize(button_size, button_size)
        self.increment_button.setFixedSize(button_size, button_size)

        #input_layout.addWidget(self.decrement_button)
        input_layout.addWidget(self.head_label)
        input_layout.addWidget(self.new_quantity_input)
        #input_layout.addWidget(self.increment_button)


        self.layout.addWidget(self.title_label)
        self.layout.addLayout(input_layout)
        # 将日期选择器添加到布局中
        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.date_input)
        self.layout.addWidget(self.record_label)
        self.layout.addWidget(self.record_input)


        self.ok_button = QPushButton('确认')
        self.cancel_button = QPushButton('取消')

        self.ok_button.setFont(font)
        self.cancel_button.setFont(font)

        self.layout.addWidget(self.ok_button)
        self.layout.addWidget(self.cancel_button)

        self.ok_button.clicked.connect(self.save_changes)
        self.cancel_button.clicked.connect(self.reject)
        self.increment_button.clicked.connect(self.increment_quantity)
        self.decrement_button.clicked.connect(self.decrement_quantity)

        # 连接回车键事件
        self.new_quantity_input.returnPressed.connect(self.save_changes)
        self.record_input.returnPressed.connect(self.save_changes)

        self.setLayout(self.layout)


    def get_new_quantity(self):
        return self.new_quantity_input.text()

    def get_record(self):
        return self.record_input.text()
    
    def get_selected_date(self):
        # 返回一个 QDate 对象，转换为字符串格式
        return self.date_input.date().toString(Qt.ISODate)

    def increment_quantity(self):
        current_quantity = int(self.new_quantity_input.text())
        new_quantity = current_quantity + 1
        self.new_quantity_input.setText(str(new_quantity))

    def decrement_quantity(self):
        current_quantity = int(self.new_quantity_input.text())
        new_quantity = current_quantity - 1
        self.new_quantity_input.setText(str(new_quantity))

    def save_changes(self):
        new_quantity_str = self.get_new_quantity()  # 假设这是从某个输入框获取的字符串
        record = self.get_record()
        selected_date = self.date_input.date().toString(Qt.ISODate)  # 获取日期字符串格式

        # 尝试将 new_quantity 转换为整数
        try:
            new_quantity = int(new_quantity_str)
        except ValueError:
            # 如果转换失败，显示警告
            QMessageBox.warning(self, '警告', '数量必须是整数')
            return  # 退出方法，不再执行后续代码

        # 确保记录不为空
        if record.strip():  # 检查 record 是否为空或只包含空白
            # 所有检查通过后保存更改或同步到数据库
            if(self.date_input.choseDate==1):
                self.accept()
            else:
                QMessageBox.warning(self, '警告', '请选择进出货日期')
        else:
            QMessageBox.warning(self, '警告', '记录不能为空')

