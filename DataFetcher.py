from PyQt5.QtCore import QRunnable, pyqtSignal, QObject

class DataFetcherSignals(QObject):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

class DataFetcher(QRunnable):
    def __init__(self, db_manager, order_key, order_direction, filtered_suppliers):
        super(DataFetcher, self).__init__()
        self.db_manager = db_manager
        self.order_key = order_key
        self.order_direction = order_direction
        self.filtered_suppliers = filtered_suppliers
        self.signals = DataFetcherSignals()

    def run(self):
        try:
            if self.order_key == 'none':
                rows = self.db_manager.fetch_rugs()
            else:
                rows = self.db_manager.fetch_ordered_rugs(self.order_key, self.order_direction)

            filtered_rows_with_records = []
            for row in rows:
                id, qty, supplier, note, image_path = row
                if not self.filtered_suppliers or supplier in self.filtered_suppliers:
                    # 获取与该产品相关的记录
                    records = self.db_manager.fetch_records_for_rug(id)  # 假设这个方法返回了所需的记录数据
                    record_str = "; ".join([f"{dat}: {content}" for dat, content in records])
                    extended_row = row + (record_str,)  # 将记录数据作为字符串附加到行数据中
                    filtered_rows_with_records.append(extended_row)

            self.signals.finished.emit(filtered_rows_with_records)

        except Exception as e:
            self.signals.error.emit(str(e))
