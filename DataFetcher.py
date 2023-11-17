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
            
            filtered_rows = []
            for row in rows:
                id, qty, supplier, note, image_path = row
                if not self.filtered_suppliers or supplier in self.filtered_suppliers:
                    filtered_rows.append(row)

            self.signals.finished.emit(filtered_rows)

        except Exception as e:
            self.signals.error.emit(str(e))
