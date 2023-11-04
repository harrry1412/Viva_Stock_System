import os
import shutil
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QPlainTextEdit, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt



class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('新增产品')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(600, 600)  # 设置对话框的大小
        self.layout = QVBoxLayout()

        # 创建字体对象
        font = QFont()
        font.setPointSize(16)

        self.model_label = QLabel('型号:')
        self.quantity_label = QLabel('数量:')
        self.supplier_label = QLabel('供货商:')
        self.note_label = QLabel('备注:')
        self.image_label = QLabel('图片:')

        self.model_input = QLineEdit()
        self.quantity_input = QLineEdit()
        self.supplier_input = QLineEdit()
        self.note_input = QPlainTextEdit()
        self.add_image_button = QPushButton('选择图片')

        self.model_label.setFont(font)
        self.quantity_label.setFont(font)
        self.supplier_label.setFont(font)
        self.note_label.setFont(font)
        self.image_label.setFont(font)

        self.model_input.setFont(font)
        self.quantity_input.setFont(font)
        self.supplier_input.setFont(font)
        self.note_input.setFont(font)
        self.add_image_button.setFont(font)

        self.layout.addWidget(self.model_label)
        self.layout.addWidget(self.model_input)
        self.layout.addWidget(self.quantity_label)
        self.layout.addWidget(self.quantity_input)
        self.layout.addWidget(self.supplier_label)
        self.layout.addWidget(self.supplier_input)
        self.layout.addWidget(self.note_label)
        self.layout.addWidget(self.note_input)
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.add_image_button)

        self.add_image_button.clicked.connect(self.select_image)

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

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.setLayout(self.layout)

        self.selected_image_path = ''
        self.new_image_path = ''
    '''
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
            self.selected_image_path = self.copy_images_to_folder(file_paths)
    '''
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
            model = self.model_input.text().strip()
            self.new_image_path = f"//VIVA303-WORK/Viva店面共享/StockImg/{model}{ext}"
            

    def copy_images_to_folder(self):
        # 如果任一路径为None，方法不执行任何操作
        if self.selected_image_path != '' and self.new_image_path != '':
            shutil.copy(self.selected_image_path, self.new_image_path)

    def get_product_data(self):
        model = self.model_input.text().strip()  # 获取型号输入框的文本内容
        quantity = self.quantity_input.text().strip()  # 获取数量输入框的文本内容
        supplier = self.supplier_input.text().strip()  # 获取供货商输入框的文本内容
        note = self.note_input.toPlainText().strip()  # 获取备注输入框的文本内容

        # 检查型号和数量是否为空
        if not model or not quantity:
            QMessageBox.warning(self, '警告', '型号和数量不能为空')
            return None

        # 检查型号是否已存在
        if self.parent().db_manager.id_exists(model):
            QMessageBox.warning(self, '警告', '型号已经存在')
            return None

        image_path = self.new_image_path  # 获取新的图片路径

        return (model, quantity, supplier, note, image_path)
    
