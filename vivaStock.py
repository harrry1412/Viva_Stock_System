import sys
from PyQt5.QtWidgets import QApplication

from App import App


def main():
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()