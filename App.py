from PyQt5.QtCore import QThreadPool
import json
import sys
import os
import mysql.connector
from PyQt5 import QtGui
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel,
    QHeaderView, QPushButton, QDialog, QHBoxLayout, QMainWindow, QFileDialog, QMessageBox, QApplication, QAbstractItemView, QHeaderView, QProgressDialog
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QTimer
from pypinyin import lazy_pinyin
from openpyxl.drawing.image import Image
from PIL import Image as PilImage
from openpyxl.styles import Alignment

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
from LoadingDialog import LoadingDialog
from ManageDialog import ManageDialog
from ChangePasswordDialog import ChangePasswordDialog
from TestDialog import TestDialog
from ClickableLineEdit import ClickableLineEdit
import datetime
from EditProductDialog import EditProductDialog
from ExcelExporter import ExcelExporter
import time


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version = 'V10.0.0'
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
        self.order_key = 'none'
        self.order_direction = 'ASC'

        # load config file
        self.config=self.load_config()

        self.office_wifi = self.config['network_settings']['office_wifi']
        self.downstair_wifi = self.config['network_settings']['downstair_wifi']
        self.supply_position = self.config['network_settings']['supply_position']

        self.base_path = self.config['network_settings']['base_path']
        if not os.path.exists(self.base_path):
            # 使用配置文件中的消息模板
            message_template = self.config['error_messages']['network_failure']
            # 准备用于填充模板的字典，包括所有可能的键
            replacements = {
                "office_wifi": self.office_wifi,
                "downstair_wifi": self.downstair_wifi,
                "supply_position": self.supply_position
            }
            
            # 使用字典推导来格式化字符串，对每个键调用.get()以提供默认值
            # 为所有可能的字段提供默认值
            message = message_template.format(**{key: replacements.get(key, '未指定') for key in replacements})
            
            self.show_message('warn', '警告', message)
            sys.exit(1)

        self.db_manager = None
        self.init_database_connection()
        self.title = f'Viva大仓库及地毯库存 {self.version} - Designed by Harry'
        self.check_version()

        self.logged = 0
        self.initUI()
    
        self.undo_stack = []
        self.redo_stack = []
        self.search_results = []
        self.current_result_index = 0
        self.user = 'Guest'
        self.table_widget.cellDoubleClicked.connect(self.handle_cell_clicked)
        self.image_paths = {}  # 添加字典来存储图片路径
        self.last_search = ''
        self.image_loaders = []  # 用于存储 ImageLoader 实例
        self.sorting_states = {}  # 添加属性来保存默认行顺序
        self.sorting_states = {1: 'default', 2: 'default', 3: 'default'}  # 初始化排序状态为默认
        self.image_index = 0
        self.id_index = 0
        self.category_index = 0
        self.supplier_index = 0
        self.qty_index = 0
        self.note_index = 0
        self.record_index = 0
        self.action_index = 0
        self.refresh_time = datetime.datetime.now()


    def load_config(self):
        print("当前工作目录:", os.getcwd())
        # 检测是否运行在一个打包后的环境
        if getattr(sys, 'frozen', False):
            # 打包后的情况，配置文件路径是exe文件旁边
            base_path = sys._MEIPASS
        else:
            # 从源代码运行的情况，配置文件在当前文件的同级目录
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        config_path = os.path.join(base_path, 'vivaStock_config.json')
        with open(config_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def init_database_connection(self):
        self.loading_dialog = LoadingDialog()
        self.loading_dialog.show()
        QApplication.processEvents()  # 刷新窗口以显示对话框

        import time
        start_time = time.time()

        while time.time() - start_time < 5:  # 模拟数据库连接的耗时操作
            QApplication.processEvents()  # 处理事件循环，保持 UI 响应

        self.db_manager = DatabaseManager()

        if not self.db_manager.initialized:
            # 使用配置文件中的消息模板
            message_template = self.config['error_messages']['database_failure']
            # 准备用于填充模板的字典，包括所有可能的键
            replacements = {
                "office_wifi": self.office_wifi,
                "downstair_wifi": self.downstair_wifi,
                "supply_position": self.supply_position
            }
            message = message_template.format(**{key: replacements.get(key, '未指定') for key in replacements})

            self.show_message('warn', '错误', message)
            sys.exit(1)  # 终止程序

        self.loading_dialog.close()

    def check_version(self):
        version=self.version[1:]
        parts=version.split('.')
        v1, v2, v3=int(parts[0]), int(parts[1]), int(parts[2])

        dict=self.db_manager.fetch_version()
        version_now_str=dict['user']
        version_now=version_now_str[1:]
        parts=version_now.split('.')
        vn1, vn2, vn3=int(parts[0]), int(parts[1]), int(parts[2])
        if (v1, v2, v3) < (vn1, vn2, vn3):
            if vn1 > v1:
                # 大版本落后
                self.show_message('warn', '警告: 版本落后',
                    f'当前版本: {v1}.{v2}.{v3}, 最新版本包含重要更新，请联系开发者更新后继续使用，或暂时使用其它设备上已更新的本应用。')
                sys.exit(1)
            elif vn2 > v2:
                # 小版本落后
                self.show_message('warn', '警告: 版本落后',
                    f'当前版本: {v1}.{v2}.{v3}, 最新版本包含轻量级更新，建议尽快联系开发者更新后继续使用，或暂时使用其它设备上已更新的本应用。')
            elif vn3 > v3:
                # 修订版本落后
                self.show_message('warn', '警告: 版本落后',
                    f'当前版本: {v1}.{v2}.{v3}, 最新版本包含小规模修复，建议联系开发者更新后继续使用，或暂时使用其它设备上已更新的本应用。')


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
        self.manage_button = QPushButton('管理')
        self.about_button = QPushButton('关于')
        self.change_password_button = QPushButton('修改密码')
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
        self.manage_button.setFont(font)
        self.about_button.setFont(font)
        self.change_password_button.setFont(font)
        self.login_button.setFont(font)

        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.prev_result_button)
        search_layout.addWidget(self.next_result_button)
        search_layout.addWidget(self.filter_button)
        search_layout.addWidget(self.order_button)
        search_layout.addWidget(self.refresh_button)
        search_layout.addWidget(self.add_button)
        search_layout.addWidget(self.export_button)
        search_layout.addWidget(self.manage_button)
        if self.show_about_bool():
            search_layout.addWidget(self.about_button)
        search_layout.addWidget(self.change_password_button)
        search_layout.addWidget(self.login_button)
        search_layout.addStretch(1)
        search_layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addLayout(search_layout)

        # 创建一个水平布局用于显示欢迎信息
        self.welcome_layout = QHBoxLayout()
        self.welcome_label = QLabel('Welcome Guest')
        self.welcome_label.setFont(font)
        self.welcome_layout.addStretch(1)  # 先添加伸缩项，占据所有额外空间
        self.welcome_layout.addWidget(self.welcome_label)  # 然后添加标签，它将被推向最右侧
        self.layout.addLayout(self.welcome_layout)


        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(7)  #总列数
        self.table_widget.setHorizontalHeaderLabels(["图片", "型号", "类型", "供货商", "数量", "备注", "记录"])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.verticalHeader().setVisible(False)
        self.populate_table()
        self.layout.addWidget(self.table_widget)
        self.central_widget.setLayout(self.layout)
        self.setGeometry(100, 100, 800, 600)

        self.search_button.clicked.connect(self.search_item)
        self.search_input.returnPressed.connect(self.search_item)
        self.search_input.clicked.connect(self.on_search_input_clicked)  # 连接信号到槽函数
        self.prev_result_button.clicked.connect(self.show_previous_result)
        self.next_result_button.clicked.connect(self.show_next_result)
        self.filter_button.clicked.connect(self.show_filter_dialog)
        self.add_button.clicked.connect(self.show_add_product_dialog)
        self.export_button.clicked.connect(self.export_to_excel)
        self.about_button.clicked.connect(self.show_about_dialog)
        self.login_button.clicked.connect(self.click_login)
        self.order_button.clicked.connect(self.show_order_dialog)
        self.refresh_button.clicked.connect(self.refresh_window)
        self.manage_button.clicked.connect(self.show_manage_dialog)
        self.change_password_button.clicked.connect(self.show_change_password_dialog)

        self.change_password_button.setVisible(False)
        self.manage_button.setVisible(False)


        # 获取表的水平表头
        header = self.table_widget.horizontalHeader()

        # 设置所有列为可伸缩模式
        header.setSectionResizeMode(QHeaderView.Stretch)

        # 设置所有列号
        self.set_all_column_index()
        
        header.setSectionResizeMode(self.image_index, QHeaderView.Interactive)
        header.setSectionResizeMode(self.id_index, QHeaderView.Interactive)
        header.setSectionResizeMode(self.category_index, QHeaderView.Interactive)
        header.setSectionResizeMode(self.supplier_index, QHeaderView.Interactive)
        header.setSectionResizeMode(self.qty_index, QHeaderView.Interactive)
        header.setSectionResizeMode(self.note_index, QHeaderView.Interactive)


        # 启用表格排序
        self.table_widget.horizontalHeader().sectionClicked.connect(self.on_header_clicked)

        self.showMaximized()
        time.sleep(1)

        self.show()

    
    def adjustColumnWidths(self):
        header = self.table_widget.horizontalHeader()
        totalWidth=self.width()

        header.resizeSection(self.image_index, totalWidth * 0.1)
        header.resizeSection(self.id_index, totalWidth * 0.25)
        header.resizeSection(self.category_index, totalWidth * 0.07)
        header.resizeSection(self.supplier_index, totalWidth * 0.07)
        header.resizeSection(self.qty_index, totalWidth * 0.07)
        header.resizeSection(self.note_index, totalWidth * 0.24)
        header.resizeSection(self.record_index, totalWidth * 0.2)

    # Overwrite resizeEvent method
    def resizeEvent(self, event):
        self.adjustColumnWidths()
        super().resizeEvent(event)

    def on_search_input_clicked(self):
        self.search_input.selectAll()

    def on_header_clicked(self, logicalIndex):
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
                self.restore_order()
                self.sorting_states[logicalIndex] = 'default'
            else:
                # 如果当前是默认顺序或未设置，切换到降序
                self.apply_order(order_key, 'DESC')
                self.sorting_states[logicalIndex] = 'DESC'
    
    def make_full_image_path(self, image_file_name):
        return self.base_path + image_file_name if image_file_name else None

    def update_suppliers(self):
        self.supplier_list = self.db_manager.fetch_supplier()
        self.supplier_list.sort(key=lambda x: lazy_pinyin(x))
        #return self.supplier_list

    def update_categories(self):
        self.category_list = self.db_manager.fetch_category()
        self.category_list.sort(key=lambda x: lazy_pinyin(x))

    def update_user_list(self):
        self.user_list = self.db_manager.fetch_users()
        self.user_list.sort(key=lambda x: x["name"].lower())

    def get_suppliers(self):
        return self.supplier_list
    
    def get_categories(self):
        return self.category_list
    
    def get_user_list(self):
        return self.user_list

    def handle_cell_clicked(self, row, column):
        self.set_all_column_index
        if column==self.image_index:
            self.show_full_size_image(row)
            if not os.path.exists(self.base_path):
                # 使用配置文件中的消息模板
                message_template = self.config['error_messages']['image_failure']
                # 准备用于填充模板的字典，包括所有可能的键
                replacements = {
                    "office_wifi": self.office_wifi,
                    "downstair_wifi": self.downstair_wifi,
                    "supply_position": self.supply_position
                }
                message = message_template.format(**{key: replacements.get(key, '未指定') for key in replacements})

                self.show_message('warn', '错误', message)
        elif column==self.qty_index:
            self.show_edit_quantity_dialog(row)
        elif column==self.note_index:
            self.show_note_dialog(row)
        elif column==self.record_index:
            self.show_record_dialog(row)
        elif column==self.id_index:
            self.show_editProduct_dialog(row)


    def show_full_size_image(self, row):
        image_path = self.get_full_image_path_from_row(row)
        if image_path:
            loader = ImageLoader(image_path, row, thumbnail=False)
            loader.signals.image_loaded.connect(self.display_full_size_image)
            self.full_size_image_thread_pool.start(loader)  # 使用新的线程池


    def display_full_size_image(self, row, pixmap):
        if not pixmap.isNull():
            self.image_window = QDialog(self)
            self.image_window.setWindowTitle("图片预览")

            # get screen size
            screen = QApplication.primaryScreen().size()

            # check pixmap size, scale to fit screen size
            max_width = screen.width() * 0.8
            max_height = screen.height() * 0.8
            if pixmap.width() > max_width or pixmap.height() > max_height:
                pixmap = pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            layout = QVBoxLayout(self.image_window)
            label = ImageLabel()
            label.setPixmap(pixmap)
            layout.addWidget(label)

            # resize image window size
            self.image_window.resize(pixmap.size())
            self.image_window.exec_()

    def get_full_image_path_from_row(self, row):
        if row in self.image_paths:
            return self.image_paths[row]
        return None
    
    def show_about_bool(self):
        dict=self.db_manager.fetch_show_about()
        show=dict['user']
        if show == 'yes':
            return True
        else:
            return False
        
    def show_manage_bool(self):
        dict=self.db_manager.fetch_show_manage()
        show=dict['user']
        if show == 'yes':
            return True
        else:
            return False


    def populate_table(self):
        # 更新Suppliers category列表
        self.update_suppliers()
        self.update_categories()
        self.update_user_list()
        # 将滚动条移动到最上面
        self.table_widget.verticalScrollBar().setValue(0)

        # 创建并启动 DataFetcher，现在传递两个筛选列表
        fetcher = DataFetcher(self.db_manager, self.order_key, self.order_direction, self.filtered_suppliers, self.filtered_categories)
        fetcher.signals.finished.connect(self.on_data_fetched)
        fetcher.signals.error.connect(self.on_data_fetch_error)
        self.thread_pool.start(fetcher)

    def on_data_fetched(self, filtered_rows):
        self.set_all_column_index()

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

    def show_edit_quantity_dialog(self, row):
        if self.logged != 1:
            self.show_message('warn', '警告', '您未登录，无法修改数量。')
            return
        permission=self.db_manager.check_user_permission(self.user, 'edit_qty')
        if permission==-1:
            self.exit_with_conn_error()
        if not permission:
            self.show_message('warn', '警告', '账户权限不足，无法修改数量。')
            return
        if not self.is_latest():
            self.show_message('warn', '警告', '其他用户已更新数据，请刷新或重启应用以应用更新。')
            return

        item = self.table_widget.item(row, self.qty_index)
        current_quantity = item.text()

        dialog = EditQuantityDialog(self, current_quantity)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            new_quantity = dialog.get_new_quantity()
            record = dialog.get_record()
            bef=current_quantity
            aft=new_quantity
            selected_date = dialog.get_selected_date()  # 获取选择的日期
            rug_id = self.table_widget.item(row, self.id_index).text()
            user = self.user
            
            edit_date=datetime.datetime.now()
            if user!='admin':
                success=self.db_manager.insert_record(rug_id, user, record, bef, aft, selected_date, edit_date)
                if not success:
                    self.exit_with_conn_error()
            self.update_quantity(row, rug_id, new_quantity)

    def update_quantity(self, row, rug_id, new_quantity):
        try:
            success=self.db_manager.update_rug_quantity(rug_id, new_quantity)
            if not success:
                self.exit_with_conn_error()
            item = self.table_widget.item(row, self.qty_index)
            item.setText(str(int(new_quantity)))
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        try:
            records = self.db_manager.fetch_records_for_rug(rug_id)
            record_str = "\n".join([f"{date}: {'+' if aft > bef else ''}{aft - bef}" for date, content, bef, aft in records])
            item = self.table_widget.item(row, self.record_index)
            item.setText(str(record_str))
        except Exception as e:
            pass


    def show_note_dialog(self, row):
        permission_level=0
        if self.logged == 1:
            permission_level=1            
        permission=self.db_manager.check_user_permission(self.user, 'edit_note')
        if permission==-1:
            self.exit_with_conn_error()
        if permission:
            permission_level=2

        rug_id = self.table_widget.item(row, self.id_index).text()
        old_note = self.table_widget.item(row, self.note_index).text()
        note_dialog = NoteDialog(self, rug_id, old_note, permission_level)
        result = note_dialog.exec_()
        if result == QDialog.Accepted:
            new_note = note_dialog.get_new_note()
            self.update_note(row, rug_id, new_note, old_note)

    def update_note(self, row, rug_id, new_note, old_note):
        try:
            # 更新数据库中的备注信息
            success=self.db_manager.update_note(new_note, rug_id)
            if not success:
                self.exit_with_conn_error()

            #Update note_record in database
            date=datetime.datetime.now()
            user=self.user
            if user!='admin' and new_note!=old_note:
                success=self.db_manager.insert_note_record(rug_id, user, old_note, new_note, date)
                if not success:
                    self.exit_with_conn_error()

            # 更新表格中的备注信息
            item = self.table_widget.item(row, self.note_index)
            item.setText(new_note)
        except mysql.connector.Error as err:
            print(f"Error updating note: {err}")

    def show_editProduct_dialog(self, row):
        if self.logged != 1:
            self.show_message('warn', '警告', '您未登录，无法修改产品数据。')
            return
        permission = self.db_manager.check_user_permission(self.user, 'edit_product')
        if permission==-1:
            self.exit_with_conn_error()
        if not permission:
            self.show_message('warn', '警告', '账户权限不足，无法修改产品数据。')
            return
        if not self.is_latest():
            self.show_message('warn', '警告', '其他用户已更新数据，请刷新或重启应用以应用更新。')
            return

        rug_id = self.table_widget.item(row, self.id_index).text()
        old_info = self.db_manager.fetch_rug_by_id(rug_id)
        edit_product_dialog = EditProductDialog(self, old_info, self.user, self.db_manager)
        edit_product_dialog.delete_signal.connect(self.refresh_window)  # 连接信号到刷新窗口的处理函数

        result = edit_product_dialog.exec_()
        if result == QDialog.Accepted:
            new_info = edit_product_dialog.get_product_data()
            if new_info:
                success = self.update_product_to_database(rug_id, new_info)
                if not success:
                    self.exit_with_conn_error()
                if success and self.user != 'admin':
                    # insert into database success, edit record id and copy image now
                    self.db_manager.update_record_ids(rug_id, new_info['model'])
                    edit_product_dialog.copy_images_to_folder()
                    date = datetime.datetime.now()
                    self.db_manager.insert_edit_product_record(self.user, str(old_info), str(new_info), date)
                self.refresh_window()

    def update_product_to_database(self, old_rug_id, new_info):
        success = self.db_manager.update_rug_info(old_rug_id, new_info)
        return success

    def show_add_product_dialog(self):
        if self.logged != 1:
            self.show_message('warn', '警告', '您未登录，无法添加新品。')
            return
        permission=self.db_manager.check_user_permission(self.user, 'add_product')
        if permission==-1:
            self.exit_with_conn_error()
        if not permission:
            self.show_message('warn', '警告', '账户权限不足，无法添加新品。')
            return
        if not self.is_latest():
            self.show_message('warn', '警告', '其他用户已更新数据，请刷新或重启应用以应用更新。')
            return

        add_product_dialog = AddProductDialog(self)
        result = add_product_dialog.exec_()
        if result == QDialog.Accepted:
            product_data = add_product_dialog.get_product_data(self)
            if product_data:
                success = self.add_product_to_database(product_data)
                if success:
                    # insert into database success, copy image now
                    add_product_dialog.copy_images_to_folder()
                    self.db_manager.insert_record(product_data[0], product_data[7], '新增产品', 0, product_data[1], product_data[6], datetime.datetime.now())
                else:
                    self.exit_with_conn_error()
                self.refresh_window()
    
    def add_product_to_database(self, product_data):
        success=self.db_manager.insert_product(product_data)
        return success

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

        record_dialog = RecordDialog(self, rug_id, records, row)
        record_dialog.exec_()

    def delete_record(self, rug_id, editdate, rug_row, isCreateRecord):
        if self.logged != 1:
            self.show_message('warn', '警告', '您未登录，无法删除记录。')
            return
        permission=self.db_manager.check_user_permission(self.user, 'delete_record')
        if permission==-1:
            self.exit_with_conn_error()
        if not permission:
            self.show_message('warn', '警告', '账户权限不足，无法删除记录。')
            return
        if not self.is_latest():
            self.show_message('warn', '警告', '其他用户已更新数据，请刷新或重启应用以应用更新。')
            return
        if (isCreateRecord == 1):
            self.show_message('warn', '警告', '此记录为产品创始记录，无法删除。')
            return
        reply = QMessageBox.question(self, '确认删除', '你确定要删除这条记录吗？',
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            date_now=datetime.datetime.now()
            success=self.db_manager.delete_record(rug_id, self.user, editdate, date_now)
            if not success:
                self.exit_with_conn_error()
            old_qty=self.db_manager.fetch_record_bef(rug_id, editdate)
            success=success and self.db_manager.update_rug_quantity(rug_id, old_qty)
            if not success:
                self.exit_with_conn_error()
            return success
        else:
            return False
    
    def update_quantity_no_record(self, rug_id, row):
        qty=self.db_manager.fetch_qty(rug_id)
        qty_item = self.table_widget.item(row, self.qty_index)
        qty_item.setText(str(qty))
        records = self.db_manager.fetch_records_for_rug(rug_id)
        record_str = "\n".join([f"{date}: {'+' if aft > bef else ''}{aft - bef}" for date, content, bef, aft in records])
        record_item = self.table_widget.item(row, self.record_index)
        record_item.setText(record_str)


    def search_item(self):
        search_text = self.search_input.text().strip().lower()
        if not search_text:
            return

        if search_text == self.last_search:
            # if search key word same, show next search result
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

                self.show_message('info', '错误', '搜索失败\n\n找不到结果。')

                


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

    def show_manage_dialog(self):
        if self.logged != 1:
            self.show_message('warn', '警告', '您未登录，无法管理用户。')
            return
        permission=self.db_manager.check_user_permission(self.user, 'manage_user')
        if permission==-1:
            self.exit_with_conn_error()
        if not permission:
            self.show_message('warn', '警告', '账户权限不足，无法管理用户。')
            return
        if not self.is_latest():
            self.show_message('warn', '警告', '其他用户已更新数据，请刷新或重启应用以应用更新。')
            return
        dialog = ManageDialog(self, self.get_user_list(), self.db_manager)
        dialog.exec_()
        self.refresh_window()

    def show_change_password_dialog(self):
        if self.logged != 1:
            self.show_message('warn', '警告', '您未登录，无法修改密码。')
            return
        dialog = ChangePasswordDialog(self, self.user, self.db_manager)
        dialog.exec_()
        self.refresh_window()
        self.logout_after_change_password()

    def show_filter_dialog(self):
        filter_dialog = FilterDialog(self)
        filter_dialog.filterApplied.connect(self.apply_filters)  # 修改方法名称以反映其功能
        filter_dialog.exec_()

    def apply_filters(self, selected_suppliers, selected_categories):
        if not selected_suppliers and not selected_categories:
            self.filtered_suppliers = []
            self.filtered_categories = []
            self.reset_application()
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
        order_dialog.orderRestored.connect(self.restore_order)
        order_dialog.exec_()

    def restore_order(self):
        self.reset_application()

    def apply_order(self, selected_order_key, order_direction):
        # 取消所有正在进行的图片加载
        for loader in self.image_loaders:
            loader.cancel()

        # 清空现有的 ImageLoader 实例列表
        self.image_loaders.clear()

        self.order_key=selected_order_key
        self.order_direction=order_direction
        self.populate_table()


    def click_login(self):
        if (self.logged==1):
            self.logout()
        else:
            self.show_login_dialog()

    def logout(self):
        self.logged = 0
        self.update_login_dependent_ui()
        self.disable_permission_dependent_ui()
        self.login_button.setText('登录')
        self.welcome_label.setText('Welcome Guest')
        self.user = 'Guest'
        
        self.show_message('info', 'Logout', 'Logout Successful')


    def logout_after_change_password(self):
        self.logged = 0
        self.update_login_dependent_ui()
        self.login_button.setText('登录')
        self.welcome_label.setText('Welcome Guest')
        self.user = 'Guest'
        
        self.show_message('info', 'Logout', '请使用新密码重新登录')


    def show_login_dialog(self):
        login_dialog = LoginDialog(self)
        result = login_dialog.exec_()
        if result == QDialog.Accepted:
            username = login_dialog.get_username()
            password = login_dialog.get_password()
            if username and password:
                login_verify_code=self.verify_login(username, password)
                if login_verify_code==2:
                    # Login successfully
                    self.login_successful(username)
                elif login_verify_code==0:
                    self.show_message('warn', '错误', '登录失败\n\n用户名或密码错误，请重试。')
                else:
                    self.show_message('warn', '错误', '登录失败\n\n账号暂时不可用，请联系系统管理员。')
            else:
                self.show_message('warn', '错误', '登录失败\n\n用户名或密码错误，请重试。')


    def verify_login(self, username, password):
        user_info = self.db_manager.fetch_userPwd_status(username)
        if (user_info==-1):
            self.exit_with_conn_error()
        if user_info:
            # 检查密码是否匹配
            if password == user_info['password']:
                # 密码正确，进一步检查状态
                if user_info['status']:
                    return 2  # 密码正确且状态为true
                else:
                    return 1  # 密码正确但状态为false
        # 密码不匹配或没有找到用户信息，返回0
        return 0

    def login_successful(self, username):
        # 在这里添加登录成功后的操作
        self.user = username.strip().capitalize()
        self.welcome_label.setText('Welcome, ' + self.user)
        self.login_button.setText('登出')
        self.logged = 1
        self.update_login_dependent_ui()
        self.enable_permission_dependent_ui()


    def is_latest(self):
        dict=self.db_manager.fetch_last_modified()
        last_time=dict['time']
        last_user=dict['user']
        if (self.refresh_time < last_time) and self.user != last_user:
            return False
        else:
            return True

    def show_message(self, type, title, message, temporary=False):
        # 创建一个消息框
        message_box = QMessageBox()
        if type == 'info':
            message_box.setIcon(QMessageBox.Information)
        elif type == 'warn':
            message_box.setIcon(QMessageBox.Warning)

        # 设置消息框的窗口图标
        if getattr(sys, 'frozen', False):
            # 打包后的情况
            application_path = sys._MEIPASS
        else:
            # 从源代码运行的情况
            application_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(application_path, 'vivastock.ico')
        message_box.setWindowIcon(QIcon(icon_path))

        message_box.setText(message)
        message_box.setWindowTitle(title)
        message_box.setStandardButtons(QMessageBox.Ok)

        # 设置消息框始终在最上层显示
        message_box.setWindowFlags(message_box.windowFlags() | Qt.WindowStaysOnTopHint)
        
        if temporary:
            message_box.setWindowModality(Qt.ApplicationModal)
            message_box.show()
            return message_box
        else:
            # 显示消息框
            message_box.exec_()

        
    def exit_with_conn_error(self):
        # 使用配置文件中的消息模板
        message_template = self.config['error_messages']['dataFetch_failure']
        # 准备用于填充模板的字典，包括所有可能的键
        replacements = {
            "office_wifi": self.office_wifi,
            "downstair_wifi": self.downstair_wifi,
            "supply_position": self.supply_position
        }
        message = message_template.format(**{key: replacements.get(key, '未指定') for key in replacements})

        self.show_message('warn', '错误', message)
        sys.exit(1)  # 终止程序
    
    def show_about_dialog(self):
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
                # 询问用户是否要导出带图版本
                reply = QMessageBox.question(self, '导出选项', '是否要导出带图片版本？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                include_images = reply == QMessageBox.Yes

                # 创建并启动导出任务
                export_runnable = ExcelExporter(self.db_manager, self.filtered_suppliers, selected_file, include_images)
                export_runnable.signals.finished.connect(lambda: self.on_export_complete(success=True, selected_file=selected_file))
                export_runnable.signals.error.connect(lambda error_message: self.on_export_complete(success=False, error_message=error_message))
                self.thread_pool.start(export_runnable)

                # 显示加载提示框
                self.loading_dialog = QProgressDialog("正在导出...", None, 0, 0, self)
                self.loading_dialog.setWindowTitle("请稍候")
                self.loading_dialog.setWindowModality(Qt.WindowModal)
                self.loading_dialog.setWindowFlag(Qt.WindowCloseButtonHint, False)
                self.loading_dialog.setCancelButton(None)
                self.loading_dialog.show()

    def on_export_complete(self, success, selected_file=None, error_message=None):
        # 关闭加载提示框
        self.loading_dialog.close()
        if success:
            self.show_message('info', '导出完成', f'已导出数据到 {selected_file}')
        else:
            self.show_message('warn', '导出失败', f'导出失败\n\n导出时出现错误: {error_message}')

    def set_all_column_index(self):
        self.image_index=self.get_column_index_by_name('图片')
        self.id_index=self.get_column_index_by_name('型号')
        self.category_index=self.get_column_index_by_name('类型')
        self.supplier_index=self.get_column_index_by_name('供货商')
        self.qty_index=self.get_column_index_by_name('数量')
        self.note_index=self.get_column_index_by_name('备注')
        self.record_index=self.get_column_index_by_name('记录')
        self.action_index=self.get_column_index_by_name('操作')

    def update_login_dependent_ui(self):
        is_logged_in = self.logged == 1
        self.change_password_button.setVisible(is_logged_in)

    def enable_permission_dependent_ui(self):
        permission=self.db_manager.check_user_permission(self.user, 'manage_user')
        if permission==-1:
            self.exit_with_conn_error()
        if not permission:
            return
        self.manage_button.setVisible(True)

    def disable_permission_dependent_ui(self):
        self.manage_button.setVisible(False)
    
    def refresh_window(self):
        self.refresh_time=datetime.datetime.now()
        self.filtered_suppliers=[]
        self.filtered_categories=[]
        self.reset_application()

    def reset_application(self):
        # 停止所有后台线程
        self.cancel_background_tasks()

        # 清除并重置界面元素
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
        self.search_input.clear()

        # 重置滚动条位置和其他界面状态
        self.table_widget.verticalScrollBar().setValue(0)

        # 重新加载数据
        self.order_key='none'
        self.last_search=''
        self.populate_table()

    def cancel_background_tasks(self):
        # 停止图片加载器
        for loader in self.image_loaders:
            loader.cancel()
        self.image_loaders.clear()

        # 清除未完成的线程池任务
        self.thread_pool.clear()
        self.full_size_image_thread_pool.clear()
        self.record_thread_pool.clear()

    # overwrite build in closeEvent method
    def closeEvent(self, event):
        # 隐藏窗口而不是关闭
        self.hide()
        event.ignore()

        # 启动一个定时器，定期检查线程池是否空闲，如果是，则退出应用程序
        self.shutdown_timer = QTimer(self)  # 创建一个新的定时器
        self.shutdown_timer.start(1000)  # 设置定时器每秒触发一次
        self.shutdown_timer.timeout.connect(self.check_thread_pool)

    def check_thread_pool(self):
        if self.thread_pool.activeThreadCount() == 0:
            # 线程完成了，可以安全退出了
            QApplication.quit()
        # 否则定时器会再次触发并检查线程