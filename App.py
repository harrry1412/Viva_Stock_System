from PyQt5.QtCore import QThreadPool
import sys
import os
import openpyxl
import mysql.connector
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel,
    QHeaderView, QPushButton, QDialog, QLineEdit, QHBoxLayout, QMainWindow, QFileDialog, QMessageBox, QApplication, QAbstractItemView
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QTimer, QSize

from DatabaseManager import DatabaseManager
from EditQuantityDialog import EditQuantityDialog
from FilterDialog import FilterDialog
from NoteDialog import NoteDialog
from RecordDialog import RecordDialog
from AddProductDialog import AddProductDialog
from LoginDialog import LoginDialog
from OrderDialog import OrderDialog
from ImageLoader import ImageLoader
from DataFetcher import DataFetcher
from RecordLoader import RecordLoader
from ImageLable import ImageLabel
from AboutDialog import AboutDialog
from ClickableLineEdit import ClickableLineEdit
import datetime


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version='V4.0.0'
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(1)
        self.full_size_image_thread_pool = QThreadPool()
        self.full_size_image_thread_pool.setMaxThreadCount(1) 
        self.record_thread_pool = QThreadPool()
        self.record_thread_pool.setMaxThreadCount(1)
        print("Multithreading with maximum %d threads" % self.thread_pool.maxThreadCount())
        self.supplier_list = None
        self.category_list = None
        self.filtered_suppliers = []
        self.filtered_categories = []
        self.image_loaders = []
        self.order_key='none'
        self.order_direction='ASC'
        self.db_manager = DatabaseManager()
        self.title = f'Viva仓库库存 {self.version} - Designed by Harry'
        self.initUI()
        self.undo_stack = []
        self.redo_stack = []
        self.search_results = []
        self.current_result_index = 0
        self.logged=0
        self.user='Guest'
        self.table_widget.cellDoubleClicked.connect(self.show_full_size_image)
        self.image_paths = {}  # 添加字典来存储图片路径
        self.last_search = ""
        self.image_loaders = []  # 用于存储 ImageLoader 实例
        self.sorting_states = {}  # 添加属性来保存默认行顺序
        self.sorting_states = {1: 'default', 2: 'default', 3: 'default'} # 初始化排序状态为默认
        self.image_index=0
        self.id_index=0
        self.category_index=0
        self.supplier_index=0
        self.qty_index=0
        self.note_index=0
        self.record_index=0
        self.action_index=0

    def initUI(self):
        self.setWindowTitle(self.title)

        if getattr(sys, 'frozen', False):
            # 打包后的情况
            application_path = sys._MEIPASS
        else:
            # 从源代码运行的情况
            application_path = os.path.dirname(os.path.abspath(__file__))

        icon_path = os.path.join(application_path, 'vivastock.ico')

        # 设置窗口图标
        self.setWindowIcon(QtGui.QIcon(icon_path))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_label = QLabel('搜索:')
        self.search_input = ClickableLineEdit()  # 使用自定义的 ClickableLineEdit
        self.search_button = QPushButton('搜索')
        self.prev_result_button = QPushButton('上一个')
        self.next_result_button = QPushButton('下一个')
        self.filter_button = QPushButton('筛选')
        self.order_button = QPushButton('排序')
        self.refresh_button = QPushButton('刷新')
        self.add_button = QPushButton('添加')
        self.export_button = QPushButton('导出')
        self.about_button = QPushButton('关于')
        self.login_button = QPushButton('登录')

        
        font = QFont()
        font.setPointSize(16)
        
        # 设置各个组件的字体
        self.search_label.setFont(font)
        self.search_input.setFont(font)
        self.search_button.setFont(font)
        self.prev_result_button.setFont(font)
        self.next_result_button.setFont(font)
        self.filter_button.setFont(font)
        self.order_button.setFont(font)
        self.refresh_button.setFont(font)
        self.add_button.setFont(font)
        self.export_button.setFont(font)
        self.about_button.setFont(font)
        self.login_button.setFont(font)

        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.prev_result_button)
        search_layout.addWidget(self.next_result_button)
        search_layout.addWidget(self.filter_button)  # 将筛选按钮添加到布局中
        search_layout.addWidget(self.order_button)
        search_layout.addWidget(self.refresh_button)
        search_layout.addWidget(self.add_button)
        search_layout.addWidget(self.export_button)
        #search_layout.addWidget(self.about_button)
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
        self.table_widget.setColumnCount(8)  #总列数
        self.table_widget.setHorizontalHeaderLabels(["图片", "型号", "类型", "供货商", "数量", "备注", "记录", "操作"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.populate_table()
        self.layout.addWidget(self.table_widget)
        self.central_widget.setLayout(self.layout)
        self.setGeometry(100, 100, 800, 600)

        self.search_button.clicked.connect(self.search_item)
        self.search_input.returnPressed.connect(self.search_item)
        self.search_input.clicked.connect(self.on_search_input_clicked)  # 连接信号到槽函数
        self.prev_result_button.clicked.connect(self.show_previous_result)
        self.next_result_button.clicked.connect(self.show_next_result)
        self.filter_button.clicked.connect(self.show_filter_dialog)  # 连接筛选按钮的点击事件
        self.add_button.clicked.connect(self.show_add_product_dialog)
        self.export_button.clicked.connect(self.export_to_excel)
        self.about_button.clicked.connect(self.showAboutDialog)
        self.login_button.clicked.connect(self.clickLogin)
        self.order_button.clicked.connect(self.show_order_dialog)
        self.refresh_button.clicked.connect(self.refreshWindow)

        # 获取表的水平表头
        header = self.table_widget.horizontalHeader()

        # 设置所有列为可伸缩模式
        header.setSectionResizeMode(QHeaderView.Stretch)

        # 设置所有列号
        self.setAllColumnIndex()

        
        header.setSectionResizeMode(self.image_index, QHeaderView.Interactive)
        header.resizeSection(self.image_index, 200)
        header.setSectionResizeMode(self.id_index, QHeaderView.Interactive)
        header.resizeSection(self.id_index, 300)
        header.setSectionResizeMode(self.category_index, QHeaderView.Interactive)
        header.resizeSection(self.category_index, 150)
        header.setSectionResizeMode(self.supplier_index, QHeaderView.Interactive)
        header.resizeSection(self.supplier_index, 100)
        header.setSectionResizeMode(self.qty_index, QHeaderView.Interactive)
        header.resizeSection(self.qty_index, 100)

        # 启用表格排序
        self.table_widget.horizontalHeader().sectionClicked.connect(self.onHeaderClicked)

        self.showMaximized()  # 最大化窗口

        self.show()

    

    def on_search_input_clicked(self):
        self.search_input.selectAll()  # 选中所有文本

    def onHeaderClicked(self, logicalIndex):
        # 检查被点击的列是否是可排序的列
        if logicalIndex in [self.id_index, self.category_index, self.supplier_index, self.qty_index]: 
            # '型号', '供货商', '数量' 列的排序键
            order_keys = {self.id_index: 'id', self.category_index: 'category', self.supplier_index: 'supplier', self.qty_index: 'qty'}

            # 获取当前列的排序键
            order_key = order_keys[logicalIndex]

            # 检查当前列的排序状态，并切换到下一个状态
            if self.sorting_states.get(logicalIndex) == 'DESC':
                # 如果当前是降序，切换到升序
                self.apply_order(order_key, 'ASC')
                self.sorting_states[logicalIndex] = 'ASC'
            elif self.sorting_states.get(logicalIndex) == 'ASC':
                # 如果当前是升序，恢复默认顺序
                self.restoreOrder()
                self.sorting_states[logicalIndex] = 'default'
            else:
                # 如果当前是默认顺序或未设置，切换到降序
                self.apply_order(order_key, 'DESC')
                self.sorting_states[logicalIndex] = 'DESC'


    def make_full_image_path(self, image_file_name):
        base_path = '\\\\VIVA303-WORK\\Viva店面共享\\StockImg\\'
        return base_path + image_file_name if image_file_name else None

    def get_suppliers(self):
        if self.supplier_list is None:
            self.supplier_list = self.db_manager.fetch_supplier()
        return self.supplier_list
    
    def get_categories(self):
        if self.category_list is None:
            self.category_list = self.db_manager.fetch_category()
        return self.category_list

    def show_full_size_image(self, row, column):
        if column == self.image_index:
            image_path = self.get_full_image_path_from_row(row)
            if image_path:
                loader = ImageLoader(image_path, row, thumbnail=False)
                loader.signals.image_loaded.connect(self.display_full_size_image)
                self.full_size_image_thread_pool.start(loader)  # 使用新的线程池


    def display_full_size_image(self, row, pixmap):
        if not pixmap.isNull():
            self.image_window = QDialog(self)
            self.image_window.setWindowTitle("图片预览")

            layout = QVBoxLayout(self.image_window)
            label = ImageLabel()
            label.setPixmap(pixmap)
            layout.addWidget(label)

            self.image_window.resize(pixmap.size())
            self.image_window.exec_()

    def get_full_image_path_from_row(self, row):
        if row in self.image_paths:
            return self.image_paths[row]
        return None


    def populate_table(self):
        # 将滚动条移动到最上面
        self.table_widget.verticalScrollBar().setValue(0)

        # 创建并启动 DataFetcher，现在传递两个筛选列表
        fetcher = DataFetcher(self.db_manager, self.order_key, self.order_direction, self.filtered_suppliers, self.filtered_categories)
        fetcher.signals.finished.connect(self.on_data_fetched)
        fetcher.signals.error.connect(self.on_data_fetch_error)
        self.thread_pool.start(fetcher)

    def on_data_fetched(self, filtered_rows):
        self.setAllColumnIndex()

        self.image_paths = {}
        self.table_widget.setRowCount(len(filtered_rows))

        for i, (id, qty, supplier, category, note, image_path) in enumerate(filtered_rows):
            full_image_path = self.make_full_image_path(image_path)
            self.image_paths[i] = full_image_path

            # Image column
            image_label = QLabel()
            image_label.setAlignment(Qt.AlignCenter)
            self.table_widget.setCellWidget(i, self.image_index, image_label)

            if full_image_path:
                loader = ImageLoader(full_image_path, i)
                loader.signals.image_loaded.connect(self.set_thumbnail)
                self.thread_pool.start(loader)
                self.image_loaders.append(loader)  # 将实例添加到列表中


            # ID column
            self.table_widget.setItem(i, 1, QTableWidgetItem(str(id)))
            font = self.table_widget.item(i, 1).font()
            font.setPointSize(14)
            self.table_widget.item(i, 1).setFont(font)
            self.table_widget.item(i, 1).setTextAlignment(Qt.AlignCenter)
            item = self.table_widget.item(i, 1)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)

            # Category column
            category_item = QTableWidgetItem(category)
            category_item.setFlags(category_item.flags() & ~Qt.ItemIsEditable)
            category_item.setFont(font)
            category_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(i, self.category_index, category_item)

            # Supplier column
            supplier_item = QTableWidgetItem(supplier)
            supplier_item.setFlags(supplier_item.flags() & ~Qt.ItemIsEditable)
            supplier_item.setFont(font)
            supplier_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(i, self.supplier_index, supplier_item)

            # Quantity column
            qty_item = QTableWidgetItem(str(qty))
            qty_item.setFlags(qty_item.flags() & ~Qt.ItemIsEditable)
            qty_item.setFont(font)
            qty_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(i, self.qty_index, qty_item)

            # Note column
            note_item = QTableWidgetItem(note)
            note_item.setFlags(note_item.flags() & ~Qt.ItemIsEditable)
            note_item.setFont(font)
            note_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(i, self.note_index, note_item)

            # Record column
            record_item = QTableWidgetItem("加载中...")
            record_item.setFlags(record_item.flags() & ~Qt.ItemIsEditable)
            self.table_widget.setItem(i, self.record_index, record_item)

            # 启动记录加载
            record_loader = RecordLoader(self.db_manager, id, i)
            record_loader.signals.records_loaded.connect(self.set_record_data)
            self.record_thread_pool.start(record_loader)

            # Operation buttons column
            edit_button = QPushButton('修改')
            note_button = QPushButton('备注')
            record_button = QPushButton('记录')

            edit_button.clicked.connect(lambda _, row=i: self.edit_quantity(row))
            note_button.clicked.connect(lambda _, row=i: self.show_note_dialog(row))
            record_button.clicked.connect(lambda _, row=i: self.show_record_dialog(row))

            button_container = QWidget()
            button_layout = QHBoxLayout(button_container)
            edit_button.setFixedSize(56, 56)
            note_button.setFixedSize(56, 56)
            record_button.setFixedSize(56, 56)
            button_layout.addWidget(edit_button)
            button_layout.addWidget(note_button)
            button_layout.addWidget(record_button)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_container.setLayout(button_layout)
            self.table_widget.setCellWidget(i, self.action_index, button_container)

            self.table_widget.setRowHeight(i, 110)

    def on_data_fetch_error(self, error_message):
        print(f"Data fetch error: {error_message}")

    def set_record_data(self, row_number, record_data):
        # 创建新的表格项
        record_item = QTableWidgetItem(record_data)
        record_item.setFlags(record_item.flags() & ~Qt.ItemIsEditable)

        # 设置字体
        font = record_item.font()  # 获取当前的字体设置
        font.setPointSize(14)      # 设置字体大小
        record_item.setFont(font)  # 应用新的字体设置

        # 设置文本对齐方式
        record_item.setTextAlignment(Qt.AlignCenter)

        # 将表格项添加到表格的相应行和列
        record_index=self.get_column_index_by_name('记录')
        self.table_widget.setItem(row_number, record_index, record_item)


    def set_thumbnail(self, index, thumbnail):
        image_label = self.table_widget.cellWidget(index, self.image_index)
        if image_label:
            image_label.setPixmap(thumbnail)
        sender = self.sender()
        if sender:
            sender.deleteLater()

    def get_column_index_by_name(self, column_name):
        for col in range(self.table_widget.columnCount()):
            if self.table_widget.horizontalHeaderItem(col).text() == column_name:
                return col
        return -1



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

        dialog = EditQuantityDialog(self, current_quantity)
        #dialog.new_quantity_input.setText(str(current_quantity))
        result = dialog.exec_()
        if result == QDialog.Accepted:
            new_quantity = dialog.get_new_quantity()
            record = dialog.get_record()
            bef=current_quantity
            aft=new_quantity
            selected_date = dialog.get_selected_date()  # 获取选择的日期
            # 构造新的记录字符串，包括日期
            # record = f"{current_quantity} -> {new_quantity}: {record}"
            rug_id = self.table_widget.item(row, id_col).text()
            user = self.user
            
            edit_date=datetime.datetime.now()
            self.db_manager.insert_record(rug_id, user, record, bef, aft, selected_date, edit_date)
            self.update_quantity(row, rug_id, new_quantity)

    def update_quantity(self, row, rug_id, new_quantity):
        # 查找“数量”列的索引
        quantity_col = None
        record_col = None
        for col in range(self.table_widget.columnCount()):
            if self.table_widget.horizontalHeaderItem(col).text() == "数量":
                quantity_col = col
                break
        for col in range(self.table_widget.columnCount()):
            if self.table_widget.horizontalHeaderItem(col).text() == "记录":
                record_col = col
                break

        # 如果没有找到“数量”列，返回或抛出一个错误
        if quantity_col is None:
            print("Error: '数量' column not found!")
            return

        try:
            self.db_manager.update_rug_quantity(rug_id, new_quantity)
            item = self.table_widget.item(row, quantity_col)
            item.setText(str(int(new_quantity)))
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        try:
            records = self.db_manager.fetch_records_for_rug(rug_id)
            record_str = "\n".join([f"{date}: {'+' if aft > bef else ''}{aft - bef}" for date, content, bef, aft in records])
            item = self.table_widget.item(row, record_col)
            item.setText(str(record_str))
        except Exception as e:
            # 可以添加错误处理逻辑
            pass


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
        old_note = self.table_widget.item(row, self.note_index).text()
        logged=self.logged

        note_dialog = NoteDialog(self, rug_id, old_note, logged)
        result = note_dialog.exec_()

        if result == QDialog.Accepted:
            new_note = note_dialog.get_new_note()
            self.update_note(row, rug_id, new_note, old_note)

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

        # 此处不再需要将记录转换为字符串，直接将列表传递给RecordDialog
        # records 已经是一个列表，每个元素代表一条记录，每条记录也是一个列表

        record_dialog = RecordDialog(self, rug_id, records)
        record_dialog.exec_()


    def update_note(self, row, rug_id, new_note, old_note):
        try:
            # 更新数据库中的备注信息
            conn = self.db_manager.connect()
            cursor = conn.cursor()
            update_query = "UPDATE rug SET note = %s WHERE id = %s"
            cursor.execute(update_query, (new_note, rug_id))
            conn.commit()
            conn.close()

            #Update note_record in database
            date=datetime.datetime.now()
            self.db_manager.insert_note_record(rug_id, self.user, old_note, new_note, date)

            # 更新表格中的备注信息
            note_item = QTableWidgetItem(new_note)
            note_item.setFont(self.table_widget.item(row, self.note_index).font())
            note_item.setTextAlignment(Qt.AlignCenter)
            self.table_widget.setItem(row, self.note_index, note_item)
        except mysql.connector.Error as err:
            print(f"Error updating note: {err}")


    def search_item(self):
        search_text = self.search_input.text().strip().lower()
        if not search_text:
            return

        # 检查当前搜索关键词是否与上一次搜索的关键词相同
        if search_text == self.last_search:
            # 如果有搜索结果，并且当前关键词未变，则跳转到下一个搜索结果
            if self.search_results:
                self.show_next_result()
                return
        else:
            # 如果当前关键词与上次不同，则执行新的搜索
            self.last_search = search_text
            matched_rows = []
            for row in range(self.table_widget.rowCount()):
                for col in range(self.table_widget.columnCount()):
                    # 跳过“记录”列的搜索
                    if col == self.record_index:  
                        continue
                    
                    item = self.table_widget.item(row, col)
                    if item and search_text in item.text().lower():
                        matched_rows.append(row)
                        break

            if matched_rows:
                self.search_results = matched_rows
                self.current_result_index = 0
                self.show_current_result()
            else:
                #print("No results found.")
                self.search_input.setText('')
                search_text=''
                self.search_results=[]
                self.table_widget.scrollToTop()

                # 创建一个消息框
                logout_message_box = QMessageBox()
                logout_message_box.setIcon(QMessageBox.Information)

                # 设置消息框的窗口图标
                if getattr(sys, 'frozen', False):
                    # 打包后的情况
                    application_path = sys._MEIPASS
                else:
                    # 从源代码运行的情况
                    application_path = os.path.dirname(os.path.abspath(__file__))
                icon_path = os.path.join(application_path, 'vivastock.ico')
                logout_message_box.setWindowIcon(QIcon(icon_path))

                logout_message_box.setText("找不到结果")
                logout_message_box.setWindowTitle("搜索失败")
                logout_message_box.setStandardButtons(QMessageBox.Ok)
                
                # 显示消息框
                logout_message_box.exec_()


    def show_current_result(self):
        if not self.search_results:
            return
        row = self.search_results[self.current_result_index]
        self.table_widget.scrollTo(self.table_widget.model().index(row, 0), QAbstractItemView.PositionAtCenter)
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

        # 检查是否已经是最后一个搜索结果
        if self.current_result_index < len(self.search_results) - 1:
            # 如果不是，移动到下一个结果
            self.current_result_index += 1
        else:
            # 如果是，回到第一个结果
            self.current_result_index = 0
        
        # 显示当前结果
        self.show_current_result()


    def show_filter_dialog(self):
        filter_dialog = FilterDialog(self)
        filter_dialog.filterApplied.connect(self.apply_filters)  # 修改方法名称以反映其功能
        filter_dialog.exec_()

    def apply_filters(self, selected_suppliers, selected_categories):
        if not selected_suppliers and not selected_categories:
            self.filtered_suppliers = []
            self.filtered_categories = []
            self.resetApplication()
        else:
            # 取消所有正在进行的图片加载
            for loader in self.image_loaders:
                loader.cancel()

            # 清空现有的 ImageLoader 实例列表
            self.image_loaders.clear()

            # 应用筛选并重新填充表格
            self.filtered_suppliers = selected_suppliers
            self.filtered_categories = selected_categories
            self.populate_table()

    def show_order_dialog(self):
        order_dialog=OrderDialog(self)
        order_dialog.orderApplied.connect(self.apply_order)
        order_dialog.orderRestored.connect(self.restoreOrder)
        order_dialog.exec_()

    def restoreOrder(self):
        self.resetApplication()

    def apply_order(self, selected_order_key, order_direction):
        # 取消所有正在进行的图片加载
        for loader in self.image_loaders:
            loader.cancel()

        # 清空现有的 ImageLoader 实例列表
        self.image_loaders.clear()

        self.order_key=selected_order_key
        self.order_direction=order_direction
        self.populate_table()


    def clickLogin(self):
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

        # 设置消息框的窗口图标
        if getattr(sys, 'frozen', False):
            # 打包后的情况
            application_path = sys._MEIPASS
        else:
            # 从源代码运行的情况
            application_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(application_path, 'vivastock.ico')
        logout_message_box.setWindowIcon(QIcon(icon_path))

        logout_message_box.setText("Logout Successful")
        logout_message_box.setWindowTitle("Logout")
        logout_message_box.setStandardButtons(QMessageBox.Ok)
        
        # 显示消息框
        logout_message_box.exec_()


    def show_login_dialog(self):
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

    def show_error_message(self, title, message):
        QMessageBox.warning(self, title, message)


    def show_add_product_dialog(self):
        # 首先检测全局变量logged是否为1
        if self.logged != 1:
            QMessageBox.warning(self, '警告', '您未登录，无法添加新品！')
            return

        add_product_dialog = AddProductDialog(self)
        result = add_product_dialog.exec_()
        if result == QDialog.Accepted:
            product_data = add_product_dialog.get_product_data()
            if product_data:
                # 注意，此处我们不再直接复制图片，而是传递图片路径给数据库添加函数
                success = self.add_product_to_database(product_data)
                if success:
                    # 数据库添加成功，现在可以复制图片
                    add_product_dialog.copy_images_to_folder()
                self.populate_table()
    
    def add_product_to_database(self, product_data):
        success=self.db_manager.insert_product(product_data)
        return success
    
    def showAboutDialog(self):
        about_dialog = AboutDialog(self, self.version)
        about_dialog.exec_()



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

    def setAllColumnIndex(self):
        self.image_index=self.get_column_index_by_name('图片')
        self.id_index=self.get_column_index_by_name('型号')
        self.category_index=self.get_column_index_by_name('类型')
        self.supplier_index=self.get_column_index_by_name('供货商')
        self.qty_index=self.get_column_index_by_name('数量')
        self.note_index=self.get_column_index_by_name('备注')
        self.record_index=self.get_column_index_by_name('记录')
        self.action_index=self.get_column_index_by_name('操作')
    
    def refreshWindow(self):
        self.filtered_suppliers=[]
        self.filtered_categories=[]
        self.resetApplication()

    def resetApplication(self):
        # 停止所有后台线程
        self.cancelBackgroundTasks()

        # 清除并重置界面元素
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
        self.search_input.clear()

        # 重置滚动条位置和其他界面状态
        self.table_widget.verticalScrollBar().setValue(0)

        # 重新加载数据
        self.order_key='none'
        self.populate_table()

    def cancelBackgroundTasks(self):
        # 停止图片加载器
        for loader in self.image_loaders:
            loader.cancel()
        self.image_loaders.clear()

        # 清除未完成的线程池任务
        self.thread_pool.clear()
        self.full_size_image_thread_pool.clear()
        self.record_thread_pool.clear()

    def closeEvent(self, event):
        # 隐藏窗口而不是关闭
        self.hide()
        # 你可以选择在此处通知用户程序将继续运行
        # 直到所有线程完成
        # ...

        # 不要在这里等待线程完成
        # 改为让应用程序在退出前自动处理线程完成

        # 让事件继续传播，以便窗口关闭操作继续
        event.ignore()

        # 启动一个定时器，定期检查线程池是否空闲，如果是，则退出应用程序
        self.shutdown_timer = QTimer(self)  # 创建一个新的定时器
        self.shutdown_timer.start(1000)  # 设置定时器每秒触发一次
        self.shutdown_timer.timeout.connect(self.checkThreadPool)

    def checkThreadPool(self):
        if self.thread_pool.activeThreadCount() == 0:
            # 线程完成了，可以安全退出了
            QApplication.quit()
        # 否则定时器会再次触发并检查线程
