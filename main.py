import sys
import yaml
from PyQt5 import QtWidgets
from engine.qt_window import QtWindow

if __name__ == '__main__':
    with open('settings.yaml', 'r') as f:
        settings = yaml.load(f.read(), Loader=yaml.FullLoader)

    DR = QtWidgets.QApplication(sys.argv)
    win = QtWindow(DR, settings)
    win.showMaximized()
    sys.exit(DR.exec_())
