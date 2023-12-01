from PyQt5.QtCore import QObject, QRunnable, pyqtSignal

class RecordLoaderSignals(QObject):
    records_loaded = pyqtSignal(int, str)  # 参数：行号和记录数据

class RecordLoader(QRunnable):
    def __init__(self, db_manager, rug_id, row_number):
        super(RecordLoader, self).__init__()
        self.db_manager = db_manager
        self.rug_id = rug_id
        self.row_number = row_number
        self.signals = RecordLoaderSignals()

    def run(self):
        try:
            records = self.db_manager.fetch_records_for_rug(self.rug_id)
            record_str = "\n".join([f"{date}: {content}" for date, content in records])
            self.signals.records_loaded.emit(self.row_number, record_str)
        except Exception as e:
            # 可以添加错误处理逻辑
            pass
