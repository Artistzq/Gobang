from ui_mainwindow import *
import sys
sys.path.append("../Scripts/")
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *  # QApplication, QWidget, QPushButton
from PyQt5.QtGui import *  # QPainter, QPixmap, QBrush
from PyQt5.QtCore import *  # Qt, QPoint, QRect
from config import VACANT, BLACK, WHITE
import threading
from game import Game, Board
from player import PlayerBase, ConsolePlayer

BOARD_COLOR = QColor(249, 214, 91)  # 棋盘颜色


class UIPlayer(PlayerBase):
    def __init__(self, player=1):
        super(UIPlayer, self).__init__(player)

    def set_player(self, player):
        self.player = player

    def get_action(self, board):
        pass


class Button(QToolButton):
    def __init__(self, parent=None):
        super(Button, self).__init__(parent)
        self.setFont(QFont("Microsoft YaHei", 18))
        self.setFixedSize(QSize(100, 60))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(True)
            self.parent().mousePressEvent(event)


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
        self.black = True
        self.finish = False
        self.sequence = []

        self.table = [[VACANT for j in range(self.n)] for i in range(self.n)]
        for i, j in self.sequence:
            self.table[i][j] = BLACK if self.black else WHITE
            self.black = not self.black
        self.withdraw_point = None
        self.winner = VACANT

        self.show_step = True

        self.setWindowTitle("五子棋")
        self.setFixedSize(self.size * self.n, self.size * self.n + self.margin)
        self.pix = QPixmap(self.size * self.n, self.size * self.n + self.margin)
        self.point = None

        self.game = Game(Board(length, length))

        # 人人对战，始终黑棋先下
        thread = threading.Thread(target=self.new_thread_start)
        thread.start()

    def new_thread_start(self):
        entity1, entity2 = ConsolePlayer(), ConsolePlayer()
        # entity1, entity2 = ConsolePlayer(random_move=True), ConsolePlayer(random_move=True)
        self.game.start_play(entity1, entity2, start_player=1, is_shown=1)

    def input(self):
        pass

    def paint(self):
        painter = QPainter(self)
        p = QPainter(self.pix)

        pack = self.game.board.pack_board()
        # self.sequence = [(self.n-i-1, j) for (i, j) in  pack["pos"]]
        print(self.sequence)

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

        # 画已落子位置
        # for i, j in self.sequence:
        for move, player in pack["states"].items():
            i, j = self.game.board.move_to_location(move)
            i = self.n - i - 1
            # if self.table[i][j] == VACANT:
            #     continue
            # color = Qt.black if self.table[i][j] == BLACK else Qt.white
            color = Qt.black if player == pack["start"] else Qt.white
            p.setPen(color)
            p.setBrush(QBrush(color))
            self.count += 1
            # 画椭圆
            p.drawEllipse(j * self.size + (self.size - self.dia) // 2, i * self.size + (self.size - self.dia) // 2,
                          self.dia, self.dia)

            # 在圆上写字
            if self.show_step:
                # color = Qt.white if self.table[i][j] == BLACK else Qt.black
                color = Qt.black if player == pack["start"] else Qt.white
                p.setPen(color)
                p.setFont(QFont("Bold", 16))
                p.drawText(j * self.size + (self.size - self.dia) // 2, i * self.size + (self.size - self.dia) // 2,
                           self.dia, self.dia, Qt.AlignCenter, str(self.count))

        painter.drawPixmap(0, 0, self.pix)
        QApplication.processEvents()

    def paintEvent(self, event):
        # return
        painter = QPainter(self)
        p = QPainter(self.pix)

        pack = self.game.board.pack_board()
        # self.sequence = [(self.n-i-1, j) for (i, j) in  pack["pos"]]

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

        # 画已落子位置
        # for i, j in self.sequence:
        for move, player in pack["states"].items():
            i, j = self.game.board.move_to_location(move)
            i = self.n-i-1
            # if self.table[i][j] == VACANT:
            #     continue
            # color = Qt.black if self.table[i][j] == BLACK else Qt.white
            color = Qt.black if player == pack["start"] else Qt.white
            p.setPen(color)
            p.setBrush(QBrush(color))
            self.count += 1
            # 画椭圆
            p.drawEllipse(j * self.size + (self.size - self.dia) // 2, i * self.size + (self.size - self.dia) // 2,
                          self.dia, self.dia)

            # 在圆上写字
            if self.show_step:
                # color = Qt.white if self.table[i][j] == BLACK else Qt.black
                color = Qt.black if player == pack["start"] else Qt.white
                p.setPen(color)
                p.setFont(QFont("Bold", 16))
                p.drawText(j * self.size + (self.size - self.dia) // 2, i * self.size + (self.size - self.dia) // 2,
                           self.dia, self.dia, Qt.AlignCenter, str(self.count))

        painter.drawPixmap(0, 0, self.pix)
        self.update()

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
                print(self.n - i - 1, j)
                self.sequence.append((i, j))
            self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    n = 10 if len(sys.argv)==1 else int(sys.argv[1])

    myWin = MyWindow(n)
    myWin.show()
    sys.exit(app.exec_())
