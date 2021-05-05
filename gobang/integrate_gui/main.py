import sys
import threading

from PyQt5.QtCore import *  # Qt, QPoint, QRect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *  # QPainter, QPixmap, QBrush
from PyQt5.QtWidgets import *  # QApplication, QWidget, QPushButton

from gobang.backend.board import Board
from gobang.backend.game import Game
from gobang.backend.game import Game
from gobang.backend.player import PlayerBase
from ui_mainwindow import Ui_MainWindow

BOARD_COLOR = QColor(249, 214, 91)


class PaintArea(QWidget):

    def __init__(self, length=19, parent=None):
        super(PaintArea, self).__init__(parent=parent)
        self.n = length
        self.width = self.frameGeometry().width()
        self.width = 1000
        self.margin = 0
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
        self.game: Game = None

    def paintEvent(self, QPaintEvent):
        print("draw the board again")
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

        if self.game:
            pack = self.game.board.pack_board()
            print(pack)
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
                print(row, col)
            self.update()
        # p = QPainter(self)
        # p.setPen(self.pen)
        # p.setBrush(self.brush)
        #
        # rect = QRect(50, 100, 300, 200)
        # points = [QPoint(150, 100), QPoint(300, 150), QPoint(350, 250), QPoint(100, 300)]
        # startAngle = 30 * 16
        # spanAngle = 120 * 16
        #
        # path = QPainterPath()
        # path.addRect(150, 150, 100, 100)
        # path.moveTo(100, 100)
        # path.cubicTo(300, 100, 200, 200, 300, 300)
        # path.cubicTo(100, 300, 200, 200, 100, 100)
        #
        # print(self.shape)
        #
        # if self.shape == "Line":
        #     p.drawLine(rect.topLeft(), rect.bottomRight())
        # elif self.shape == "Rectangle":
        #     p.drawRect(rect)
        # elif self.shape == 'Rounded Rectangle':
        #     p.drawRoundedRect(rect, 25, 25, Qt.RelativeSize)
        # elif self.shape == "Ellipse":
        #     p.drawEllipse(rect)
        # elif self.shape == "Polygon":
        #     p.drawPolygon(QPolygon(points), Qt.WindingFill)
        # elif self.shape == "Polyline":
        #     p.drawPolyline(QPolygon(points))
        # elif self.shape == "Points":
        #     p.drawPoints(QPolygon(points))
        # elif self.shape == "Pie":
        #     p.drawPie(rect, startAngle, spanAngle)
        # elif self.shape == "Arc":
        #     p.drawArc(rect, startAngle, spanAngle)
        # elif self.shape == "Chord":
        #     p.drawChord(rect, startAngle, spanAngle)
        # elif self.shape == "Path":
        #     p.drawPath(path)
        # elif self.shape == "Text":
        #     p.drawText(rect, Qt.AlignCenter, "Hello Qt!")
        # elif self.shape == "Pixmap":
        #     p.drawPixmap(150, 150, QPixmap("images/qt-logo.png"))

    def bind_game(self, game: Game):
        self.game = game


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.game = Game(Board(19))
        self.area = PaintArea(19)
        self.area.bind_game(self.game)
        self.init_components()

    def init_components(self):
        self.showFullScreen()

        self.widget_pve_para.setVisible(False)
        self.widget_pvp_para.setVisible(False)
        self.widget_watch_para.setVisible(False)
        self.widget_game.setVisible(False)

        # menu panel
        self.pBtn_pve.clicked.connect(self.start_new_pve)
        self.pBtn_pve_confirm.clicked.connect(self.confirm_new_pve)
        self.pBtn_watch.clicked.connect(self.watch_a_game)
        self.pBtn_watch_confirm.clicked.connect(self.confirm_watch)
        self.pBtn_pvp.clicked.connect(self.start_new_pvp)
        self.pBtn_pvp_confirm.clicked.connect(self.confirm_new_pvp)
        self.pBtn_quit.clicked.connect(QCoreApplication.quit)

        # game panel
        self.pBtn_back.clicked.connect(self.back_to_menu)

        self.horizontalLayout.removeWidget(self.widget_board)
        self.widget_board.deleteLater()
        self.widget_board = None

        # area = PaintArea(parent=self.widget_game)
        self.horizontalLayout.addWidget(self.area)

        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 8)

        # self.widget_game.setVisible(True)

    def start_new_pve(self):
        if self.widget_pve_para.isVisible():
            self.widget_pve_para.setVisible(False)
        else:
            self.widget_pve_para.setVisible(True)

    def confirm_new_pve(self):
        self.get_into_ui("pve")
        size = self.get_from_cmb(self.cb_pve_size)
        level = self.get_from_cmb(self.cb_pve_level)
        # do something to backend

    def watch_a_game(self):
        if self.widget_watch_para.isVisible():
            self.widget_watch_para.setVisible(False)
        else:
            self.widget_watch_para.setVisible(True)

    def confirm_watch(self):
        self.get_into_ui("watch")
        size = self.get_from_cmb(self.cb_watch_size)
        level_black = self.get_from_cmb(self.cb_watch_level_b)
        level_white = self.get_from_cmb(self.cb_watch_level_w)
        # do something to backend

    def start_new_pvp(self):
        if self.widget_pvp_para.isVisible():
            self.widget_pvp_para.setVisible(False)
        else:
            self.widget_pvp_para.setVisible(True)

    def confirm_new_pvp(self):
        size = self.get_from_cmb(self.cb_pvp_size)
        self.widget_pvp_para.setVisible(False)
        # do something

    def get_into_ui(self, option):
        if option == "pve":
            self.pBtn_pre.setVisible(False)
            self.pBtn_next.setVisible(False)
            self.pBtn_undo.setVisible(True)
            self.pBtn_tip.setVisible(True)
            self.pBtn_surrender.setVisible(True)
            self.widget_pve_para.setVisible(False)
        elif option == "watch":
            self.pBtn_pre.setVisible(False)
            self.pBtn_next.setVisible(True)
            self.pBtn_undo.setVisible(False)
            self.pBtn_tip.setVisible(False)
            self.pBtn_surrender.setVisible(False)
            self.widget_watch_para.setVisible(False)

        self.widget_game.setVisible(True)
        self.widget_menu.setVisible(False)

    def undo_for_pve(self):
        pass

    def next_for_watch(self):
        pass

    def pre_for_watch(self):
        pass

    def get_from_cmb(self, cb: QComboBox, ret_str=False):
        if ret_str:
            return cb.currentIndex(), cb.currentText()
        else:
            return cb.currentIndex()

    def tip(self):
        pass

    def surrender(self):
        pass

    def back_to_menu(self):
        # do something
        self.widget_menu.setVisible(True)
        self.widget_game.setVisible(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    md = MainWindow()
    md.show()
    sys.exit(app.exec_())
