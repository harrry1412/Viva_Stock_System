from PyQt5.QtCore import QObject, QRunnable, pyqtSignal

class UserFetcherSignals(QObject):
    users_loaded = pyqtSignal(list)  # 返回完整的用户列表
    error = pyqtSignal(str)

class UserFetcher(QRunnable):
    def __init__(self, db_manager):
        super(UserFetcher, self).__init__()
        self.db_manager = db_manager
        self.signals = UserFetcherSignals()

    def run(self):
        try:
            users = self.db_manager.fetch_users()
            self.signals.users_loaded.emit(users)
        except Exception as e:
            self.signals.error.emit(str(e))
