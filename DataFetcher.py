
from PyQt5.QtCore import QRunnable, pyqtSignal, QObject
from PyQt5.QtCore import QObject, QRunnable, pyqtSignal

class DataFetcherSignals(QObject):
    finished = pyqtSignal(list)  # 发送完成时的数据
    error = pyqtSignal(str)  # 发送错误信息

class DataFetcher(QRunnable):
    def __init__(self, db_manager, order_key, order_direction, filtered_suppliers, filtered_categories):
        super(DataFetcher, self).__init__()
        self.db_manager = db_manager
        self.order_key = order_key
        self.order_direction = order_direction
        self.filtered_suppliers = filtered_suppliers
        self.filtered_categories = filtered_categories  # 新增参数
        self.signals = DataFetcherSignals()

    def run(self):
        try:
            # 根据 order_key 获取数据
            if self.order_key == 'none':
                rows = self.db_manager.fetch_rugs()
            else:
                rows = self.db_manager.fetch_ordered_rugs(self.order_key, self.order_direction)

            filtered_rows = []
            for row in rows:
                id, qty, supplier, category, note, image_path = row 

                # 检查是否符合筛选条件
                if ((not self.filtered_suppliers or supplier in self.filtered_suppliers) and 
                    (not self.filtered_categories or category in self.filtered_categories)):
                    filtered_rows.append(row)

            self.signals.finished.emit(filtered_rows)
        except Exception as e:
            self.signals.error.emit(str(e))


