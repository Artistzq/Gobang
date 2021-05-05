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


class MyWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, length=19, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.n = length
        self.width = 800
        self.margin = 80
        self.size = self.width // self.n
        self.dia = self.size * 9 // 10

        self.start = False
        self.count = 0
        self.finish = False
        self.pack = None


        self.show_step = True

        self.setWindowTitle("五子棋")
        self.setFixedSize(self.size * self.n, self.size * self.n + self.margin)
        self.pix = QPixmap(self.size * self.n, self.size * self.n + self.margin)
        self.point = None

        self.game = Game(Board(length, length))
        self.entity1, self.entity2 = SocketPlayer("127.0.0.1", 30606), SocketPlayer("127.0.0.1", port=30607)

        self.entity3 = ConsolePlayer(random_move=True, sleep=0.2)
        self.entity4 = ConsolePlayer(random_move=True, sleep=0.2)
        # 人人对战，始终黑棋先下
        thread = threading.Thread(target=self.new_thread_start, args=(self.entity1, self.entity2, 1))
        thread.start()

    def new_thread_start(self, entity1, entity2, start_player):
        self.game.start_play(entity1, entity2, start_player=start_player)

    def paintEvent(self, event):
        painter = QPainter(self)
        p = QPainter(self.pix)

        # 画棋盘
        p.setPen(BOARD_COLOR)
        p.setBrush(QBrush(BOARD_COLOR))
        p.drawRect(0, 0, self.size * self.n, self.size * self.n + self.margin)
        # 画网格线
        p.setPen(Qt.black)
        for i in range(self.n):
            p.drawLine(self.size * i + self.size // 2, self.size // 2,
                       self.size * i + self.size // 2, self.size * self.n - self.size // 2)
            p.drawLine(self.size // 2, self.size * i + self.size // 2,
                       self.size * self.n - self.size // 2, self.size * i + self.size // 2)

        pack = self.game.board.pack_board()
        for i, j, player in pack["pos_player"]:
            i = self.n - i - 1
            color = Qt.black if player == pack["start_player"] else Qt.white
            p.setPen(color)
            p.setBrush(QBrush(color))
            self.count += 1
            # 画椭圆
            p.drawEllipse(j * self.size + (self.size - self.dia) // 2, i * self.size + (self.size - self.dia) // 2,
                          self.dia, self.dia)

            # 在圆上写字
            if self.show_step:
                color = Qt.black if player == pack["start_player"] else Qt.white
                p.setPen(color)
                p.setFont(QFont("Bold", 16))
                p.drawText(j * self.size + (self.size - self.dia) // 2, i * self.size + (self.size - self.dia) // 2,
                           self.dia, self.dia, Qt.AlignCenter, str(self.count))

        painter.drawPixmap(0, 0, self.pix)
        self.update()
        # QApplication.processEvents()

    def mouseReleaseEvent(self, event):
        """
        鼠标点击
        :param event:
        :return:
        """
        if event.button() == Qt.LeftButton:
            if not self.finish:
                x, y = event.pos().x(), event.pos().y()
                j, i = x // self.size, y // self.size
                row, col = self.n - i - 1, j  # 棋盘参考系
            self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    n = 19 if len(sys.argv) == 1 else int(sys.argv[1])

    myWin = MyWindow(n)
    myWin.show()
    sys.exit(app.exec_())
