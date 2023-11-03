import os
import openpyxl
import mysql.connector
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel,
    QHeaderView, QPushButton, QDialog, QLineEdit, QHBoxLayout, QMainWindow, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

from DatabaseManager import DatabaseManager
from EditQuantityDialog import EditQuantityDialog
from FilterDialog import FilterDialog
from NoteDialog import NoteDialog
from RecordDialog import RecordDialog
from AddProductDialog import AddProductDialog
from LoginDialog import LoginDialog
from OrderDialog import OrderDialog
from ImageLoader import ImageLoader


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.supplier_list = None
        self.filtered_suppliers = []
        self.order_key='none'
        self.order_direction='ASC'
        self.db_manager = DatabaseManager()
        self.title = 'Viva仓库库存 - Designed by Harry'
        self.initUI()
        self.undo_stack = []
        self.redo_stack = []
        self.search_results = []
        self.current_result_index = 0
        self.logged=0
        self.user='Guest'

    def initUI(self):
        self.setWindowTitle(self.title)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_label = QLabel('搜索型号:')
        self.search_input = QLineEdit()
        self.search_button = QPushButton('搜索')
        self.prev_result_button = QPushButton('上一个')
        self.next_result_button = QPushButton('下一个')
        self.filter_button = QPushButton('筛选')  # 添加筛选按钮
        self.order_button = QPushButton('排序')
        self.add_button = QPushButton('添加')
        self.export_button = QPushButton('导出')
        self.login_button = QPushButton('登录')

        
        font = QFont()
        font.setPointSize(16)
        
        # 设置各个组件的字体
        self.search_label.setFont(font)
        self.search_input.setFont(font)
        self.search_button.setFont(font)
        self.prev_result_button.setFont(font)
        self.next_result_button.setFont(font)
        self.filter_button.setFont(font)  # 筛选按钮
        self.order_button.setFont(font)  # 排序按钮
        self.add_button.setFont(font)
        self.export_button.setFont(font)
        self.login_button.setFont(font)

        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.prev_result_button)
        search_layout.addWidget(self.next_result_button)
        search_layout.addWidget(self.filter_button)  # 将筛选按钮添加到布局中
        search_layout.addWidget(self.order_button)
        search_layout.addWidget(self.add_button)
        search_layout.addWidget(self.export_button)
        search_layout.addWidget(self.login_button)
        search_layout.addStretch(1)
        search_layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addLayout(search_layout)

        # 创建一个水平布局用于显示欢迎信息
        self.welcome_layout = QHBoxLayout()
        self.welcome_label = QLabel('Welcome Guest')  # 将其设置为类的属性
        self.welcome_label.setFont(font)  # 使用之前设置的字体
        self.welcome_layout.addStretch(1)  # 先添加伸缩项，占据所有额外空间
        self.welcome_layout.addWidget(self.welcome_label)  # 然后添加标签，它将被推向最右侧
        self.layout.addLayout(self.welcome_layout)


        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)  # 增加1，以包括备注列
        self.table_widget.setHorizontalHeaderLabels(["图片", "型号", "供货商", "数量", "备注", "操作"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.populate_table()
        self.layout.addWidget(self.table_widget)
        self.central_widget.setLayout(self.layout)
        self.setGeometry(100, 100, 800, 600)

        self.search_button.clicked.connect(self.search_item)
        self.search_input.returnPressed.connect(self.search_item)
        self.prev_result_button.clicked.connect(self.show_previous_result)
        self.next_result_button.clicked.connect(self.show_next_result)
        self.filter_button.clicked.connect(self.show_filter_dialog)  # 连接筛选按钮的点击事件
        self.add_button.clicked.connect(self.show_add_product_dialog)
        self.export_button.clicked.connect(self.export_to_excel)
        self.login_button.clicked.connect(self.clickLogin)
        self.order_button.clicked.connect(self.show_order_dialog)

        self.showMaximized()  # 最大化窗口

        self.show()

    def get_suppliers(self):
        if self.supplier_list is None:
            self.supplier_list = self.db_manager.fetch_supplier()
        return self.supplier_list


    def populate_table(self):
        try:
            # 获取所有数据行
            if(self.order_key=='none'):
                rows = self.db_manager.fetch_rugs()
            else:
                rows=self.db_manager.fetch_ordered_rugs(self.order_key, self.order_direction)
        

            # 根据筛选条件过滤数据
            filtered_rows = []
            for id, qty, supplier, note, image_path in rows:
                if not self.filtered_suppliers or supplier in self.filtered_suppliers:
                    filtered_rows.append((id, qty, supplier, note, image_path))

            # 设置表格行数
            self.table_widget.setRowCount(len(filtered_rows))
            self.table_widget.verticalHeader().setVisible(False)

            # 填充表格数据
            for i, (id, qty, supplier, note, image_path) in enumerate(filtered_rows):
                # Image column
                image_label = QLabel()
                image_label.setAlignment(Qt.AlignCenter)
                self.table_widget.setCellWidget(i, 0, image_label)

                loader = ImageLoader(image_path, i)
                loader.image_loaded.connect(self.set_thumbnail)  # 将信号连接到槽函数
                loader.start()  # 启动线程

                # ID column
                self.table_widget.setItem(i, 1, QTableWidgetItem(str(id)))
                font = self.table_widget.item(i, 1).font()
                font.setPointSize(14)
                self.table_widget.item(i, 1).setFont(font)
                self.table_widget.item(i, 1).setTextAlignment(Qt.AlignCenter)
                item = self.table_widget.item(i, 1)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                # Supplier column
                supplier_item = QTableWidgetItem(supplier)
                supplier_item.setFont(font)
                supplier_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(i, 2, supplier_item)

                # Quantity column
                qty_item = QTableWidgetItem(str(qty))
                qty_item.setFlags(qty_item.flags() & ~Qt.ItemIsEditable)
                qty_item.setFont(font)
                qty_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(i, 3, qty_item)

                # Remark column
                note_item = QTableWidgetItem(note)
                note_item.setFont(font)
                note_item.setTextAlignment(Qt.AlignCenter)
                self.table_widget.setItem(i, 4, note_item)

                # Operation buttons column (5th column)
                edit_button = QPushButton('修改')
                undo_button = QPushButton('撤销')
                redo_button = QPushButton('重做')
                note_button = QPushButton('备注')
                record_button = QPushButton('记录')

                redo_button.clicked.connect(self.redo_quantity)
                edit_button.clicked.connect(lambda _, row=i: self.edit_quantity(row))
                undo_button.clicked.connect(self.undo_quantity)
                note_button.clicked.connect(lambda _, row=i: self.show_note_dialog(row))
                record_button.clicked.connect(lambda _, row=i: self.show_record_dialog(row))

                button_container = QWidget()
                button_layout = QHBoxLayout(button_container)
                redo_button.setFixedSize(56, 56)
                edit_button.setFixedSize(56, 56)
                undo_button.setFixedSize(56, 56)
                note_button.setFixedSize(56, 56)
                record_button.setFixedSize(56, 56)
                button_layout.addWidget(edit_button)
                #button_layout.addWidget(undo_button)
                #button_layout.addWidget(redo_button)
                button_layout.addWidget(note_button)
                button_layout.addWidget(record_button)
                button_layout.setContentsMargins(0, 0, 0, 0)
                button_container.setLayout(button_layout)
                self.table_widget.setCellWidget(i, 5, button_container)  # 设置为第5列

                self.table_widget.setRowHeight(i, 110)

        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def set_thumbnail(self, index, thumbnail):
        image_label = self.table_widget.cellWidget(index, 0)
        if image_label:
            image_label.setPixmap(thumbnail)



    def edit_quantity(self, row):
        # 首先检测全局变量logged是否为1
        if self.logged != 1:
            QMessageBox.warning(self, '警告', '您未登录，无法修改数量！')
            return

        # 查找“数量”列的索引
        quantity_col = None
        for col in range(self.table_widget.columnCount()):
            if self.table_widget.horizontalHeaderItem(col).text() == "数量":
                quantity_col = col
                break

        # 查找“型号”列的索引
        id_col = None
        for col in range(self.table_widget.columnCount()):
            if self.table_widget.horizontalHeaderItem(col).text() == "型号":
                id_col = col
                break

        # 如果没有找到“数量”或“型号”列，返回或抛出一个错误
        if quantity_col is None:
            print("Error: '数量' column not found!")
            return
        if id_col is None:
            print("Error: '型号' column not found!")
            return

        item = self.table_widget.item(row, quantity_col)
        current_quantity = item.text()

        # 将数据压入previous_quantities堆栈
        self.undo_stack.append((row, current_quantity))

        # 清空redo_quantities堆栈
        self.redo_stack.clear()

        dialog = EditQuantityDialog(self)
        dialog.new_quantity_input.setText(current_quantity)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            new_quantity = dialog.get_new_quantity()
            record=dialog.get_record()
            record=current_quantity+"->"+new_quantity+": "+record
            rug_id = self.table_widget.item(row, id_col).text()
            user=self.user
            self.update_quantity(row, rug_id, new_quantity)
            self.db_manager.insert_record(rug_id, user, record)

    def update_quantity(self, row, rug_id, new_quantity):
        # 查找“数量”列的索引
        quantity_col = None
        for col in range(self.table_widget.columnCount()):
            if self.table_widget.horizontalHeaderItem(col).text() == "数量":
                quantity_col = col
                break

        # 如果没有找到“数量”列，返回或抛出一个错误
        if quantity_col is None:
            print("Error: '数量' column not found!")
            return

        try:
            self.db_manager.update_rug_quantity(rug_id, new_quantity)
            item = self.table_widget.item(row, quantity_col)
            item.setText(str(new_quantity))
            # self.previous_quantities[row] = self.table_widget.item(row, quantity_col).text()
        except mysql.connector.Error as err:
            print(f"Error: {err}")


    def undo_quantity(self):
        if self.undo_stack:
            # 查找“数量”列的索引
            quantity_col = None
            for col in range(self.table_widget.columnCount()):
                if self.table_widget.horizontalHeaderItem(col).text() == "数量":
                    quantity_col = col
                    break

            # 查找“型号”列的索引
            id_col = None
            for col in range(self.table_widget.columnCount()):
                if self.table_widget.horizontalHeaderItem(col).text() == "型号":
                    id_col = col
                    break

            # 从undo_stack中弹出数据
            row, quantity_to_undo = self.undo_stack.pop()

            # 获取当前表格中的数量
            current_quantity = self.table_widget.item(row, quantity_col).text()

            # 将当前数量放入redo_stack以便我们可以后续重做这个操作
            self.redo_stack.append((row, current_quantity))

            # 使用之前的数量来更新表格
            rug_id = self.table_widget.item(row, id_col).text()
            self.update_quantity(row, rug_id, quantity_to_undo)


    def redo_quantity(self):
        if self.redo_stack:
            # 查找“数量”列的索引
            quantity_col = None
            for col in range(self.table_widget.columnCount()):
                if self.table_widget.horizontalHeaderItem(col).text() == "数量":
                    quantity_col = col
                    break

            # 查找“型号”列的索引
            id_col = None
            for col in range(self.table_widget.columnCount()):
                if self.table_widget.horizontalHeaderItem(col).text() == "型号":
                    id_col = col
                    break

            row, quantity_to_redo = self.redo_stack.pop()  # 从重做栈中弹出数据
            current_quantity = self.table_widget.item(row, quantity_col).text()  # 获取当前数量

            # 将当前数量放回到undo_stack，以便我们可以再次撤销这个操作
            self.undo_stack.append((row, current_quantity))

            rug_id = self.table_widget.item(row, id_col).text()
            self.update_quantity(row, rug_id, quantity_to_redo)

    def show_note_dialog(self, row):
        id_col = None
        for col in range(self.table_widget.columnCount()):
            if self.table_widget.horizontalHeaderItem(col).text() == "型号":
                id_col = col
                break

        if id_col is None:
            print("Error: '型号' column not found!")
            return

        rug_id = self.table_widget.item(row, id_col).text()
        note = self.table_widget.item(row, 4).text()
        logged=self.logged

        note_dialog = NoteDialog(self, rug_id, note, logged)
        result = note_dialog.exec_()

        if result == QDialog.Accepted:
            new_note = note_dialog.get_new_note()
            self.update_note(row, rug_id, new_note)

    def show_record_dialog(self, row):
        id_col = None
        for col in range(self.table_widget.columnCount()):
            if self.table_widget.horizontalHeaderItem(col).text() == "型号":
                id_col = col
                break

        if id_col is None:
            print("Error: '型号' column not found!")
            return

        rug_id = self.table_widget.item(row, id_col).text()
        records = self.db_manager.fetch_records(rug_id)

        formatted_records = ["型号: {}, 日期: {}, 修改人：{}, 内容: {}".format(record[0], record[1], record[2], record[3]) for record in records]
        records_str = "\n\n".join(formatted_records)

        record_dialog = RecordDialog(self, rug_id, records_str)
        record_dialog.exec_()

    def update_note(self, row, rug_id, new_note):
        try:
            # 更新数据库中的备注信息
            conn = self.db_manager.connect()
            cursor = conn.cursor()
            update_query = "UPDATE rug SET note = %s WHERE id = %s"
            cursor.execute(update_query, (new_note, rug_id))
            conn.commit()
            conn.close()

            # 更新表格中的备注信息
            note_item = QTableWidgetItem(new_note)
            note_item.setFont(self.table_widget.item(row, 4).font())
            note_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, 4, note_item)
        except mysql.connector.Error as err:
            print(f"Error updating note: {err}")


    def search_item(self):
        search_text = self.search_input.text().strip().lower()
        if not search_text:
            return

        matched_rows = []
        for row in range(self.table_widget.rowCount()):
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                if item and search_text in item.text().lower():
                    matched_rows.append(row)
                    break

        if matched_rows:
            self.search_results = matched_rows
            self.current_result_index = 0
            self.show_current_result()
        else:
            print("No results found.")


    def show_current_result(self):
        if not self.search_results:
            return
        row = self.search_results[self.current_result_index]
        self.table_widget.scrollToItem(self.table_widget.item(row, 0))
        self.table_widget.clearSelection()
        self.table_widget.selectRow(row)

    def show_previous_result(self):
        if not self.search_results:
            return
        if self.current_result_index > 0:
            self.current_result_index -= 1
            self.show_current_result()

    def show_next_result(self):
        if not self.search_results:
            return
        if self.current_result_index < len(self.search_results) - 1:
            self.current_result_index += 1
            self.show_current_result()

    def show_filter_dialog(self):
        filter_dialog = FilterDialog(self)
        filter_dialog.filterApplied.connect(self.apply_supplier_filter)
        filter_dialog.exec_()

    def apply_supplier_filter(self, selected_suppliers):
        self.filtered_suppliers = selected_suppliers
        self.populate_table()


    def show_order_dialog(self):
        order_dialog=OrderDialog(self)
        order_dialog.orderApplied.connect(self.apply_order)
        order_dialog.exec_()

    def apply_order(self, selected_order_key, order_direction):
        self.order_key=selected_order_key
        self.order_direction=order_direction
        self.populate_table()


    def clickLogin(self):
        print(self.logged)
        if (self.logged==1):
            self.logout()
        else:
            self.show_login_dialog()

    def logout(self):
        self.logged = 0
        self.login_button.setText('登录')
        self.welcome_label.setText('Welcome Guest')
        self.user = 'Guest'
        
        # 创建一个消息框
        logout_message_box = QMessageBox()
        logout_message_box.setIcon(QMessageBox.Information)
        logout_message_box.setText("Logout Successful")
        logout_message_box.setWindowTitle("Logout")
        logout_message_box.setStandardButtons(QMessageBox.Ok)
        
        # 显示消息框
        logout_message_box.exec_()

    def show_login_dialog(self):
        print('Login Dialog')
        login_dialog = LoginDialog(self)
        result = login_dialog.exec_()
        if result == QDialog.Accepted:
            username = login_dialog.get_username()
            password = login_dialog.get_password()
            if username and password:
                if self.verify_login(username, password):
                    self.login_successful(username)
                else:
                    self.show_error_message('登录失败', '用户名或密码错误!')

    def verify_login(self, username, password):
        # 在这里添加验证用户名和密码的逻辑
        database_password = self.db_manager.fetch_userPwd(username)
        if database_password and password == database_password:
            return True
        else:
            return False

    def login_successful(self, username):
        # 在这里添加登录成功后的操作
        print("登录成功!")
        self.user=username
        self.welcome_label.setText('Welcome '+username)
        self.login_button.setText('登出')
        self.logged=1

        # 创建一个消息框
        logout_message_box = QMessageBox()
        logout_message_box.setIcon(QMessageBox.Information)
        logout_message_box.setText("Login Successful \nWelcome "+username)
        logout_message_box.setWindowTitle("Login")
        logout_message_box.setStandardButtons(QMessageBox.Ok)
        
        # 显示消息框
        logout_message_box.exec_()

    def show_error_message(self, title, message):
        QMessageBox.warning(self, title, message)



    def show_add_product_dialog(self):
        add_product_dialog = AddProductDialog(self)
        result = add_product_dialog.exec_()
        if result == QDialog.Accepted:
            product_data = add_product_dialog.get_product_data()
            if product_data:
                self.add_product_to_database(product_data)
                self.populate_table()

    def add_product_to_database(self, product_data):
        try:
            conn = self.db_manager.connect()
            cursor = conn.cursor()
            insert_query = "INSERT INTO rug (qty, supplier, note, image, id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_query, product_data)
            conn.commit()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Error inserting product: {err}")

    def export_to_excel(self):
        export_dialog = QFileDialog(self)
        export_dialog.setDefaultSuffix('xlsx')
        export_dialog.setAcceptMode(QFileDialog.AcceptSave)
        export_dialog.setNameFilter('Excel Files (*.xlsx)')

        if export_dialog.exec_():
            selected_file = export_dialog.selectedFiles()[0]
            if selected_file:
                try:
                    # 获取要导出的数据（从数据库中获得）
                    db_manager = self.db_manager
                    selected_suppliers = self.filtered_suppliers
                    rows_to_export = db_manager.fetch_rugs()

                    # 指定自定义的列顺序
                    column_order = ['图片', '型号', '数量', '供货商', '备注']

                    # 对数据进行排序以符合要求
                    rows_to_export.sort(key=lambda x: (x[2], x[1], x[0]))

                    # 创建一个新的 Excel 工作簿
                    workbook = openpyxl.Workbook()

                    # 创建一个默认的工作表
                    default_sheet = workbook.active
                    default_sheet.title = '所有供货商'

                    # 添加列标题
                    default_sheet.append(column_order)

                    # 将数据填充到默认工作表
                    for row in rows_to_export:
                        # 提取按照自定义顺序的列数据
                        row_data = [row[4], row[0], row[1], row[2], row[3]]
                        default_sheet.append(row_data)

                    # 获取不同供货商的数据
                    suppliers = set(row[2] for row in rows_to_export)

                    # 创建一个工作表来存储每个供货商的数据
                    for supplier in suppliers:
                        sheet = workbook.create_sheet(title=supplier)

                        # 添加列标题
                        sheet.append(column_order)

                        supplier_data = [row for row in rows_to_export if row[2] == supplier]
                        for row in supplier_data:
                            # 按照指定顺序提取数据列
                            data_columns = [row[4], row[0], row[1], row[2], row[3]]
                            sheet.append(data_columns)


                    # 保存 Excel 文件
                    workbook.save(selected_file)

                    QMessageBox.information(self, '导出完成', f'已导出数据到 {selected_file}')
                except Exception as e:
                    QMessageBox.warning(self, '导出失败', f'导出时出现错误: {str(e)}')