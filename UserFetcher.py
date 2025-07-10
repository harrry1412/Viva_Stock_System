from PyQt5.QtCore import QRunnable, pyqtSignal, QObject

class UserFetcherSignals(QObject):
    finished = pyqtSignal(list)  # 成功返回用户列表
    error = pyqtSignal(str)      # 发生错误时发送错误信息

class UserFetcher(QRunnable):
    def __init__(self, db_manager):
        super(UserFetcher, self).__init__()
        self.db_manager = db_manager
        self.signals = UserFetcherSignals()

    def run(self):
        try:
            users = self.db_manager.fetch_users()
            users.sort(key=lambda x: x["name"].lower())
            self.signals.finished.emit(users)
        except Exception as e:
            self.signals.error.emit(str(e))
