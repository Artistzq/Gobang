import sys

import socket
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *  # QApplication, QWidget, QPushButton
from PyQt5.QtGui import *  # QPainter, QPixmap, QBrush
from PyQt5.QtCore import *  # Qt, QPoint, QRect

import threading
from ui_mainwindow import Ui_MainWindow

BOARD_COLOR = QColor(249, 214, 91)  # 棋盘颜色


class MyWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, length=19, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.n = length

        self.host = "127.0.0.1"
        self.port = 20223
        self.n, self.pack = self.init_from_para(self.host, self.port)
        print("已初始化参数")

        self.ui_host = ("127.0.0.1", 20226)

        self.width = 800
        self.margin = 80
        self.size = self.width // self.n
        self.dia = self.size * 9 // 10

        self.count = 0
        self.finish = False

        self.show_step = True

        self.setFixedSize(self.size * self.n, self.size * self.n + self.margin)
        self.pix = QPixmap(self.size * self.n, self.size * self.n + self.margin)

    def init_from_para(self, host, port):
        main_socket = socket.socket()
        main_socket.connect((host, port))
        msg = main_socket.recv(2048).decode("utf-8")
        print(msg)
        width, pack = json.loads(msg)
        main_socket.close()
        return width, pack

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

        if self.pack:
            pack = self.pack
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

                # 发送
                s = socket.socket()
                host, port = "127.0.0.1", 0
                if self.pack["current_player"] == 1:
                    host, port = ("127.0.0.1", 20224)
                else:
                    host, port = ("127.0.0.1", 20225)
                s.connect((host, port))
                data = {"row": row, "col": col}
                j_str = json.dumps(data)
                s.sendall((j_str + "#").encode("utf-8"))
                s.close()
                # print("发送", data)

                # 接收
                # print("接收")
                # s = socket.socket()
                # s.connect()
                # # pack_str = ""
                # # while True:
                # #     pack_str += pack_skt.recv(1024).decode("utf-8")
                # #     if pack_str[-1] == "@":
                # #         pack_str = pack_str[:-1]
                # #         break
                # # print(pack_str)
                # pack_str = pack_skt.recv(1024).decode("utf-8")
                # self.pack = json.loads(pack_str)
                # pack_skt.close()
                # s.close()
                # print("接受完")


            self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    n = 19 if len(sys.argv) == 1 else int(sys.argv[1])

    myWin = MyWindow(n)
    myWin.show()
    sys.exit(app.exec_())
