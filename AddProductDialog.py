import os
import sys
import shutil
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QPlainTextEdit, QFileDialog, QMessageBox, QComboBox
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
import datetime


class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('新增产品')
        if getattr(sys, 'frozen', False):
            self.setWindowIcon(QIcon(sys._MEIPASS + '/vivastock.ico'))
        else:
            self.setWindowIcon(QIcon('vivastock.ico'))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(600, 600)  # 设置对话框的大小
        self.layout = QVBoxLayout()

        # 创建字体对象
        font = QFont()
        font.setPointSize(16)

        # 初始化各个标签和输入框
        self.model_label = QLabel('型号:')
        self.quantity_label = QLabel('数量:')
        self.supplier_label = QLabel('供货商:')
        self.category_label = QLabel('产品类别:')
        self.wlevel_label = QLabel('所在仓库层:')
        self.note_label = QLabel('备注:')
        self.image_label = QLabel('图片:')

        self.model_input = QLineEdit()
        self.quantity_input = QLineEdit()
        # 创建供货商输入框
        self.supplier_input = QComboBox()
        self.supplier_input.setEditable(True)
        
        self.category_input = QComboBox()
        self.category_input.setEditable(True)

        self.wlevel_input = QComboBox()
        self.wlevel_input.setEditable(True)

        # 添加一个空的选项作为默认选项
        self.supplier_input.addItem('')
        self.category_input.addItem('')
        self.wlevel_input.setCurrentText('0')

        # 填充供货商组合框选项
        suppliers = self.parent().supplier_list
        for supplier in suppliers:
            self.supplier_input.addItem(supplier)

        # 填充类别组合框选项
        categories = self.parent().category_list
        for category in categories:
            self.category_input.addItem(category)

        # 填充所在层组合框选项
        wlevels = self.parent().wlevel_list
        for wlevel in wlevels:
            self.wlevel_input.addItem(str(wlevel))

        self.note_input = QPlainTextEdit()
        self.add_image_button = QPushButton('选择图片')

        # 设置字体
        self.model_label.setFont(font)
        self.quantity_label.setFont(font)
        self.supplier_label.setFont(font)
        self.category_label.setFont(font)
        self.note_label.setFont(font)
        self.image_label.setFont(font)
        self.wlevel_label.setFont(font)

        self.model_input.setFont(font)
        self.quantity_input.setFont(font)
        self.supplier_input.setFont(font)
        self.category_input.setFont(font)
        self.note_input.setFont(font)
        self.add_image_button.setFont(font)
        self.wlevel_input.setFont(font)

        # 添加到布局
        self.layout.addWidget(self.model_label)
        self.layout.addWidget(self.model_input)
        self.layout.addWidget(self.quantity_label)
        self.layout.addWidget(self.quantity_input)
        self.layout.addWidget(self.supplier_label)
        self.layout.addWidget(self.supplier_input)
        self.layout.addWidget(self.category_label)
        self.layout.addWidget(self.category_input)
        self.layout.addWidget(self.wlevel_label)
        self.layout.addWidget(self.wlevel_input)
        self.layout.addWidget(self.note_label)
        self.layout.addWidget(self.note_input)
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.add_image_button)

        # 按钮布局
        button_layout = QHBoxLayout()
        self.save_button = QPushButton('保存')
        self.cancel_button = QPushButton('取消')
        self.save_button.setFont(font)
        self.cancel_button.setFont(font)
        self.save_button.setFixedSize(100, 56)
        self.cancel_button.setFixedSize(100, 56)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        self.layout.addLayout(button_layout)

        # 按钮连接
        self.add_image_button.clicked.connect(self.select_image)
        self.save_button.clicked.connect(self.save_change)
        self.cancel_button.clicked.connect(self.reject)

        self.setLayout(self.layout)

        # 图片相关
        self.selected_image_path = ''
        self.new_image_path = ''
        self.image_name = ''

    def select_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_paths, _ = file_dialog.getOpenFileNames(self, '选择图片', '', 'Images (*.png *.jpg *.jpeg *.bmp *.gif)')

        if file_paths:
            # 我们只保存第一张图片的路径，您可以根据需求来调整
            self.selected_image_path = file_paths[0]  # 假设我们只处理第一个选中的文件
            # 生成新文件名
            _, ext = os.path.splitext(self.selected_image_path)
            # 对model进行处理：替换/为-，去除(之后的内容（如果有），并去除非法字符
            model_raw = self.model_input.text().strip()
            model_processed = model_raw.split('(')[0].replace('/', '-').replace('\n', '').strip()
            self.new_image_path = f"//VIVA303-WORK/Viva店面共享/StockImg/{model_processed}{ext}"
            self.image_name = os.path.basename(self.new_image_path)

            self.image_label.setText('图片: 图片已上传')

            

    def copy_images_to_folder(self):
        # 如果任一路径为None，方法不执行任何操作
        if self.selected_image_path != '' and self.new_image_path != '':
            print(self.selected_image_path)
            print(self.new_image_path)
            shutil.copy(self.selected_image_path, self.new_image_path)

    def get_product_data(self, parent=None):
        model = self.model_input.text().strip()  # 获取型号输入框的文本内容
        quantity = self.quantity_input.text().strip()  # 获取数量输入框的文本内容
        supplier = self.supplier_input.currentText().strip()  # 获取供货商输入框的文本内容
        category = self.category_input.currentText().strip()  # 获取产品类别输入框的文本内容
        note = self.note_input.toPlainText().strip()  # 获取备注输入框的文本内容
        wlevel = self.wlevel_input.currentText().strip()  # 获取所在层输入框的文本内容

        image = self.image_name
        if image == '':
            image = model + '.png'

        # 返回产品数据
        date = datetime.datetime.now()
        user = parent.user
        # return (model, int(quantity), category, supplier, note, image, date, user, wlevel)

        return {
            'model': model,
            'quantity': int(quantity),
            'category': category,
            'supplier': supplier,
            'note': note,
            'image': image,
            'date': date,
            'user': user,
            'wlevel': wlevel
    }
    
    def save_change(self):
        model = self.model_input.text().strip()  # 获取型号输入框的文本内容
        quantity = self.quantity_input.text().strip()  # 获取数量输入框的文本内容
        supplier = self.supplier_input.currentText().strip()  # 获取供货商输入框的文本内容
        category = self.category_input.currentText().strip()  # 获取产品类别输入框的文本内容
        wlevel = self.wlevel_input.currentText().strip()  # 获取所在层输入框的文本内容

        # 检查型号和数量是否为空
        if not model or not quantity:
            QMessageBox.warning(self, '警告', '型号和数量不能为空')
            return None

        # 检查供货商是否为空
        if not supplier:
            QMessageBox.warning(self, '警告', '供货商不能为空')
            return None
        
        # 检查供货商是否已存在，若存在，将大小写统一
        supplier_database = self.parent().db_manager.supplier_exists(supplier)
        if isinstance(supplier_database, str):
            supplier = supplier_database
            QMessageBox.warning(self, '警告', f'该供货商已存在，已统一大小写为 "{supplier}"')
            print(f'该供货商已存在，已统一大小写为 "{supplier}"')

        # 检查所在层是否为空
        if not wlevel:
            QMessageBox.warning(self, '警告', '所在仓库层不能为空')
            return None
        
        # 检查所在层是否为整数
        try:
            int(wlevel)
        except ValueError:
            QMessageBox.warning(self, '警告', '所在仓库层必须为整数')
            return

        # 检查类别是否为空
        if not category:
            QMessageBox.warning(self, '警告', '产品类别不能为空')
            return None

        # 检查数量是否为整数
        try:
            int(quantity)
        except ValueError:
            QMessageBox.warning(self, '警告', '数量必须为整数')
            return

        # 检查型号是否已存在
        if self.parent().db_manager.id_exists(model):
            QMessageBox.warning(self, '警告', '型号已经存在')
            return None
        
        self.accept()

    
