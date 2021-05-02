import json
import socket
import sys
import threading

from PyQt5.QtCore import *  # Qt, QPoint, QRect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *  # QPainter, QPixmap, QBrush
from PyQt5.QtWidgets import *  # QApplication, QWidget, QPushButton

from gobang.backend.board import Board
from gobang.backend.game import Game
from gobang.backend.player import SocketPlayer, ConsolePlayer
from ui_mainwindow import Ui_MainWindow

BOARD_COLOR = QColor(249, 214, 91)  # 棋盘颜色

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog


class MainCode(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    md = MainCode()
    md.show()
    sys.exit(app.exec_())