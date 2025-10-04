import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QComboBox, QFileDialog, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import shutil
import datetime
from PyQt5.QtCore import pyqtSignal


class EditProductDialog(QDialog):
    delete_signal = pyqtSignal()  # 定义一个自定义信号
    def __init__(self, parent=None, old_info=None, user='', db_manager=None):
        self.user=user
        self.db_manager=db_manager
        if old_info is None:
            old_info = {}
        self.old_info = old_info
        super().__init__(parent)
        self.setWindowTitle('编辑产品')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(400, 500)  # 增加窗口高度
        self.layout = QVBoxLayout()

        font = QFont()
        font.setPointSize(16)

        # 界面组件初始化
        self.model_label = QLabel('型号:')
        self.supplier_label = QLabel('供货商:')
        self.category_label = QLabel('产品类别:')
        self.wlevel_label = QLabel('所在仓库层:')
        self.image_label = QLabel('图片:')

        self.model_input = QLineEdit()
        self.supplier_input = QComboBox()
        self.category_input = QComboBox()
        self.wlevel_input = QComboBox()
        self.add_image_button = QPushButton('选择图片')

        self.supplier_input.setEditable(True)
        self.category_input.setEditable(True)
        self.wlevel_input.setEditable(True)
        self.supplier_input.addItem("")
        self.category_input.addItem("")

        # 填充供货商组合框选项
        suppliers = self.parent().get_suppliers() 
        for supplier in suppliers:
            self.supplier_input.addItem(supplier)

        # 填充类别组合框选项
        categories = self.parent().get_categories()
        for category in categories:
            self.category_input.addItem(category)

        # 填充所在层组合框选项
        wlevels = self.parent().get_wlevels()
        for wlevel in wlevels:
            self.wlevel_input.addItem(str(wlevel))

        # 设置字体
        self.model_label.setFont(font)
        self.supplier_label.setFont(font)
        self.category_label.setFont(font)
        self.wlevel_label.setFont(font)
        self.image_label.setFont(font)
        self.model_input.setFont(font)
        self.supplier_input.setFont(font)
        self.category_input.setFont(font)
        self.wlevel_input.setFont(font)
        self.add_image_button.setFont(font)

        # 布局
        self.layout.addWidget(self.model_label)
        self.layout.addWidget(self.model_input)
        self.layout.addWidget(self.supplier_label)
        self.layout.addWidget(self.supplier_input)
        self.layout.addWidget(self.category_label)
        self.layout.addWidget(self.category_input)
        self.layout.addWidget(self.wlevel_label)
        self.layout.addWidget(self.wlevel_input)
        self.layout.addWidget(self.image_label)
        
        # 将选择图片按钮和删除产品按钮放在同一个水平布局中
        button_layout = QVBoxLayout()
        
        self.add_image_button.setFont(font)
        self.add_image_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout.addWidget(self.add_image_button)

        # 添加固定高度的空白区域
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        button_layout.addItem(spacer)

        self.delete_button = QPushButton('删除产品')
        self.delete_button.setFont(font)
        self.delete_button.setStyleSheet('background-color: red; color: white; border: 1px solid black;')
        self.delete_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button_layout.addWidget(self.delete_button)

        self.layout.addLayout(button_layout)

        # 再次添加固定高度的空白区域
        spacer_bottom = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.layout.addItem(spacer_bottom)

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
        self.delete_button.clicked.connect(self.delete_product)
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
            self.wlevel_input.setCurrentText(str(self.old_info['wlevel']))

    def select_image(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setFileMode(QFileDialog.ExistingFile)  # 设置为只能选择一个文件
        file_path, _ = file_dialog.getOpenFileName(self, '选择图片', '', 'Images (*.png *.jpg *.jpeg *.bmp *.gif)')

        if file_path:
            # 我们只保存所选图片的路径
            self.selected_image_path = file_path
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

    def get_product_data(self):
        # 获取并验证输入数据
        model_raw = self.model_input.text().strip()
        # 对model进行处理：替换/为-，去除(之后的内容（如果有），并去除非法字符
        model_processed = model_raw.split('(')[0].replace('/', '-').replace('\n', '').strip()
        supplier = self.supplier_input.currentText().strip()
        category = self.category_input.currentText().strip()
        wlevel = self.wlevel_input.currentText().strip()

        image = self.image_name
        if image == '':
            image = model_processed + '.png'


        return {
            'model': model_raw,
            'supplier': supplier,
            'category': category,
            'wlevel': wlevel,
            'image': image
        }

    def save_changes(self):
        # 获取输入值
        model = self.model_input.text().strip()
        supplier = self.supplier_input.currentText().strip()
        category = self.category_input.currentText().strip()
        wlevel = self.wlevel_input.currentText().strip()

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
        
        try:
            int(wlevel)
        except ValueError:
            QMessageBox.warning(self, '警告', '所在层必须是整数。')
            return

        # 检查model（id）是否重复
        old_model = self.old_info['id']
        if model != old_model:
            if self.parent().db_manager.id_exists(model):
                QMessageBox.warning(self, '警告', '该型号已存在，请使用不同的型号。')
                return

        # 如果没有选择新图片，重命名原图片
        if self.selected_image_path == '':
            base_path = "//VIVA303-WORK/Viva店面共享/StockImg"
            # 处理旧图片名：替换斜杠为横杠，去除括号之后的内容，删除换行符和首尾空格
            old_image_name = self.old_info['image'].split('(')[0].replace('/', '-').replace('\n', '').strip()
            old_image_path = os.path.join(base_path, old_image_name)
            # 确保model已经处理过：替换斜杠为横杠，去除括号之后的内容，删除换行符和首尾空格
            model_processed = self.model_input.text().split('(')[0].replace('/', '-').replace('\n', '').strip()
            new_image_name = f"{model_processed}.png"
            new_image_path = os.path.join(base_path, new_image_name)
            
            if os.path.exists(old_image_path):
                try:
                    os.rename(old_image_path, new_image_path)
                except OSError as e:
                    print(f"Error renaming file: {e}")

        # 如果所有检查都通过，接受对话框并关闭
        self.accept()

    def delete_product(self):
        reply = QMessageBox.warning(self, '警告', '您确定要删除该产品吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            date_now = datetime.datetime.now()
            success = self.db_manager.delete_product(self.old_info['id'], self.user, date_now)
            if success:
                self.delete_signal.emit()  # 发出信号
                self.close()
            else:
                self.parent.exitWithConnError()

