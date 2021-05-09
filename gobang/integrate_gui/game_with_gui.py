import sys
import threading
import time

from PyQt5 import QtGui
from PyQt5.QtCore import *  # Qt, QPoint, QRect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *  # QPainter, QPixmap, QBrush
from PyQt5.QtWidgets import *  # QApplication, QWidget, QPushButton

from gobang.backend.board import Board
from gobang.backend.game import Game
from gobang.backend.player import PlayerBase, RandomTestPlayer
from gobang.utils.stoppable_thread import StoppableThread
from gobang.backend.mcts_alphaZero import MCTSPlayer
from gobang.backend.policy_value_net_pytorch import PolicyValueNet
from ui_mainwindow import Ui_MainWindow

human_player_event = threading.Event()


class QtGame(Game, QWidget):
    BOARD_COLOR = QColor(249, 214, 91)

    def __init__(self, board: Board, event: threading.Event, parent=None):
        Game.__init__(self, board)
        QWidget.__init__(self, parent, flags=Qt.WindowFlags())
        self.click_pos = (0, 0)
        self.human_player_event = event

        # self.n = board.width
        # self.width = self.frameGeometry().width()
        # self.width = 1000
        # self.margin = 0
        # self.size = self.width // self.n
        # self.dia = self.size * 9 // 10
        #
        # self.start = False
        # self.count = 0
        # self.finish = False
        # self.pack = None
        #
        # self.show_step = True
        #
        # self.setFixedSize(self.size * self.n, self.size * self.n + self.margin)
        # self.pix = QPixmap(self.size * self.n, self.size * self.n + self.margin)
        # self.point = None
        # self.game_thread: StoppableThread = StoppableThread()

        self.init_canvas()

    def new_thread_player(self, entity1, entity2, sp):
        self.game_thread = StoppableThread(target=self.start_play, args=(entity1, entity2, sp, True))
        self.game_thread.start()

    def set_board(self, board: Board):
        self.board = board
        self.init_canvas()

    def gui(self):
        self.update()

    def init_canvas(self):
        self.click_pos = (0, 0)
        self.n = self.board.width
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

        self.setFixedSize(self.size * self.n, self.size * self.n + self.margin)
        self.pix = QPixmap(self.size * self.n, self.size * self.n + self.margin)
        self.point = None
        self.game_thread: StoppableThread = StoppableThread()

        self.informate = False

    def start_play(self, entity1: PlayerBase, entity2: PlayerBase, start_player=1, is_shown=0):
        print("进入新线程，开始一场棋局")
        self.board.init_board(start_player)
        entities = {1: entity1, 2: entity2}
        end: bool = False
        winner = -1
        while True:
            current_thread: StoppableThread = threading.current_thread()
            if current_thread.stopped():
                print("点击返回菜单使得棋局线程中断")
                return 0
            # 循环直到对局结束
            current_player = self.board.get_current_player()
            entity_in_turn = entities[current_player]
            # 获取下棋位置
            move = entity_in_turn.get_action(self.board)

            print("location: {}, player: {}".format(self.board.move_to_location(move).__str__(),
                                                    "black" if current_player == start_player else "white"))

            if move == -1:
                print("程序手动中断")
                return 0

            # 棋盘执行落子
            self.board.do_move(move)
            # GUI显示
            end, winner = self.board.game_end(fast_judge=True)
            self.gui()
            if end:
                entity1.set_end()
                entity2.set_end()
                self.finish = True
                time.sleep(0.2)
                print("棋局线程正常结束")
                return winner

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        # print("draw the board again")
        painter = QPainter(self)
        p = QPainter(self.pix)

        # 画棋盘
        p.setPen(self.BOARD_COLOR)
        p.setBrush(QBrush(self.BOARD_COLOR))
        p.drawRect(0, 0, self.size * self.n, self.size * self.n + self.margin)
        # 画网格线
        p.setPen(Qt.black)
        for i in range(self.n):
            p.drawLine(self.size * i + self.size // 2, self.size // 2,
                       self.size * i + self.size // 2, self.size * self.n - self.size // 2)
            p.drawLine(self.size // 2, self.size * i + self.size // 2,
                       self.size * self.n - self.size // 2, self.size * i + self.size // 2)

        pack = self.board.pack_board()
        # 或从其他渠道传来pack
        for count, (i, j, player) in enumerate(pack["pos_player"]):
            i = self.n - i - 1
            color = Qt.black if player == pack["start_player"] else Qt.white
            p.setPen(color)
            p.setBrush(QBrush(color))
            self.count += 1
            # 画圆
            p.drawEllipse(j * self.size + (self.size - self.dia) // 2, i * self.size + (self.size - self.dia) // 2,
                          self.dia, self.dia)

            # 在圆上写计数
            if self.show_step:
                color = Qt.white if player == pack["start_player"] else Qt.black
                p.setPen(color)
                p.setFont(QFont("Bold", 16))
                p.drawText(j * self.size + (self.size - self.dia) // 2, i * self.size + (self.size - self.dia) // 2,
                           self.dia, self.dia, Qt.AlignCenter, str(count + 1))

        if pack["finished"]:
            # 画出最后连成五子的结果，首先找到最后一步落子
            pos = pack["pos_player"][-1][:2]
            # 判断周围连续5个子的是哪五个子
            # ui_pos = (self.n-pos[0]-1, pos[1])
            # for i in range(pos[0]-4 if pos[0]>=4 else 0, pos+1):
            #     for j in range(i)

        painter.drawPixmap(0, 0, self.pix)

        if pack["finished"] and not self.informate:
            self.informate = True
            QMessageBox.information(self, "游戏结束",
                                    "赢家：{}".format("先手黑棋" if pack["winner"] == pack["start_player"] else "后手白棋"),
                                    QMessageBox.Yes, QMessageBox.Yes)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            if not self.finish:
                x, y = event.pos().x(), event.pos().y()
                j, i = x // self.size, y // self.size
                row, col = self.n - i - 1, j  # 棋盘参考系
                self.click_pos = (row, col)
                self.human_player_event.set()
                # 应将这个传给后台

    def stop_game(self):
        self.click_pos = -1, -1
        self.human_player_event.set()
        # print("已放行玩家接收的进程")
        self.game_thread.stop()
        self.game_thread.join()


class QtPlayer(PlayerBase):
    def __init__(self, area: QtGame, player=1):
        super(QtPlayer, self).__init__(player)
        self.event = area.human_player_event
        self.area = area

    def get_action(self, board: Board):
        # 通过信号和槽获取落子位置
        while True:
            self.event.wait()
            # print("set了event为true，程序继续运行")
            # 当被set后，恢复
            pos = self.area.click_pos
            if pos[0] == -1 and pos[1] == -1:
                print("中止输入")
                self.event.clear()
                return -1
            # print("click_pos:", pos, end=" ")
            move = board.location_to_move(pos)
            self.event.clear()
            if move in board.available:
                break
        # 返回落子位置
        return move


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self, flags=Qt.WindowFlags())
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.game = QtGame(Board(), threading.Event(), parent=self.widget_game)
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
        self.horizontalLayout.addWidget(self.game)

        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 8)

        # self.widget_game.setVisible(True)

    def start_new_pve(self):
        if self.widget_pve_para.isVisible():
            self.widget_pve_para.setVisible(False)
        else:
            self.widget_pve_para.setVisible(True)

    def confirm_new_pve(self):
        # ui
        self.get_into_ui("pve")
        size = self.get_from_cmb(self.cb_pve_size)
        size = int(size.split("x")[0])
        level = self.get_from_cmb(self.cb_pve_level)
        # func
        self.game.set_board(Board(size, size))
        game_policy = PolicyValueNet(size, size, model_file="../resources/current_policy{}x{}.model".format(size, size))
        entity1 = MCTSPlayer(game_policy.policy_value_fn, c_puct=5, n_playout=300)

        # entity1 = RandomTestPlayer(0.001)
        entity2 = QtPlayer(self.game)
        self.game.new_thread_player(entity1, entity2, 1)

    def watch_a_game(self):
        if self.widget_watch_para.isVisible():
            self.widget_watch_para.setVisible(False)
        else:
            self.widget_watch_para.setVisible(True)

    def confirm_watch(self):
        self.get_into_ui("watch")
        size = self.get_from_cmb(self.cb_watch_size)
        size = int(size.split("x")[0])
        level_black = self.get_from_cmb(self.cb_watch_level_b)
        level_white = self.get_from_cmb(self.cb_watch_level_w)
        # do something to backend
        self.game.set_board(Board(size, size))
        print(size)
        entity1 = RandomTestPlayer(0.001)
        entity2 = RandomTestPlayer(0.001)
        game_policy1 = PolicyValueNet(size, size, model_file="../resources/current_policy{}x{}.model".format(size, size))
        entity1 = MCTSPlayer(game_policy1.policy_value_fn, c_puct=5, n_playout=100)
        # game_policy2 = PolicyValueNet(size, size, model_file="../resources/current_policy.model")
        entity2 = MCTSPlayer(game_policy1.policy_value_fn, c_puct=5, n_playout=100)
        self.game.new_thread_player(entity1, entity2, 1)

    def start_new_pvp(self):
        if self.widget_pvp_para.isVisible():
            self.widget_pvp_para.setVisible(False)
        else:
            self.widget_pvp_para.setVisible(True)

    def confirm_new_pvp(self):
        self.get_into_ui("pvp")
        size = self.get_from_cmb(self.cb_pvp_size)
        size = int(size.split("x")[0])
        self.widget_pvp_para.setVisible(False)
        # do something
        self.game.set_board(Board(size, size))
        entity1 = QtPlayer(self.game)
        entity2 = QtPlayer(self.game)
        self.game.new_thread_player(entity1, entity2, 1)

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
        elif option == "pvp":
            self.widget_pvp_para.setVisible(False)
            self.pBtn_pre.setVisible(False)
            self.pBtn_next.setVisible(False)
            self.pBtn_undo.setVisible(False)
            self.pBtn_tip.setVisible(False)
            self.pBtn_surrender.setVisible(False)

        self.widget_game.setVisible(True)
        self.widget_menu.setVisible(False)

    def undo_for_pve(self):
        pass

    def next_for_watch(self):
        pass

    def pre_for_watch(self):
        pass

    def get_from_cmb(self, cb: QComboBox, ret_str=True):
        if ret_str:
            return cb.currentText()
        else:
            return cb.currentIndex(), cb.currentIndex()

    def tip(self):
        pass

    def surrender(self):
        pass

    def back_to_menu(self):
        # ui
        self.widget_menu.setVisible(True)
        self.widget_game.setVisible(False)
        # func
        self.game.stop_game()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    md = MainWindow()
    md.show()
    sys.exit(app.exec_())
