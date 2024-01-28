import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QComboBox, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class EditProductDialog(QDialog):
    def __init__(self, parent=None, old_info=None):
        if old_info==None:
            old_info={}
        self.old_info=old_info
        print(self.old_info)
        super().__init__(parent)
        self.setWindowTitle('编辑产品')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(600, 600)
        self.layout = QVBoxLayout()

        font = QFont()
        font.setPointSize(16)

        # 界面组件初始化
        self.model_label = QLabel('型号:')
        self.supplier_label = QLabel('供货商:')
        self.category_label = QLabel('产品类别:')
        self.image_label = QLabel('图片:')

        self.model_input = QLineEdit()
        self.supplier_input = QComboBox()
        self.category_input = QComboBox()
        self.add_image_button = QPushButton('选择图片')

        self.supplier_input.setEditable(True)
        self.category_input.setEditable(True)
        self.supplier_input.addItem("")
        self.category_input.addItem("")

        # 设置字体
        for widget in [self.model_label, self.supplier_label, self.category_label, self.image_label,
                       self.model_input, self.supplier_input, self.category_input, self.add_image_button]:
            widget.setFont(font)

        # 布局
        for widget in [self.model_label, self.model_input, self.supplier_label, self.supplier_input,
                       self.category_label, self.category_input, self.image_label, self.add_image_button]:
            self.layout.addWidget(widget)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton('保存')
        self.cancel_button = QPushButton('取消')
        for button in [self.save_button, self.cancel_button]:
            button.setFont(font)
            button.setFixedSize(100, 56)
            button_layout.addWidget(button)
        self.layout.addLayout(button_layout)

        # 按钮事件
        self.add_image_button.clicked.connect(self.select_image)
        self.save_button.clicked.connect(self.save_changes)
        self.cancel_button.clicked.connect(self.reject)

        self.setLayout(self.layout)

        # 图片相关
        self.selected_image_path = ''
        self.new_image_path = ''
        self.image_name = ''

        # 加载产品信息
        self.load_product_info()

    def load_product_info(self):
        if self.old_info:
            self.model_input.setText(self.old_info['id'])
            self.supplier_input.setCurrentText(self.old_info['supplier'])
            self.category_input.setCurrentText(self.old_info['category'])

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
            self.selected_image_path = file_paths[0] # 假设我们只处理第一个选中的文件
            # 生成新文件名
            _, ext = os.path.splitext(self.selected_image_path)
            model = self.model_input.text().strip().replace('/', '-')
            self.new_image_path = f"//VIVA303-WORK/Viva店面共享/StockImg/{model}{ext}"
            self.image_name = os.path.basename(self.new_image_path)


    def get_product_data(self):
        # 获取并验证输入数据
        model = self.model_input.text().strip()
        supplier = self.supplier_input.currentText().strip()
        category = self.category_input.currentText().strip()
        image = model+'.png'

        if not model:
            QMessageBox.warning(self, '警告', '型号不能为空')
            return None

        return {
            'model': model,
            'supplier': supplier,
            'category': category,
            'image': image
        }
    
    def save_changes(self):
        # 获取输入值
        model = self.model_input.text().strip()
        supplier = self.supplier_input.currentText().strip()
        category = self.category_input.currentText().strip()

        # 单独检查每个字段
        if not model:
            QMessageBox.warning(self, '警告', '型号不能为空。')
            return

        if not supplier:
            QMessageBox.warning(self, '警告', '供货商不能为空。')
            return

        if not category:
            QMessageBox.warning(self, '警告', '产品类别不能为空。')
            return

        # 检查model（id）是否重复
        if self.parent().db_manager.id_exists(model):
            QMessageBox.warning(self, '警告', '该型号已存在，请使用不同的型号。')
            return

        # 如果所有检查都通过，接受对话框并关闭
        self.accept()
