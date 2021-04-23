import json
import random
import re
import socket

from gobang.backend.board import Board
from gobang.utils import log

logger = log.Logger(log.path, logger_name=__name__).get_logger()


class PlayerBase:
    """基类"""

    def __init__(self, player):
        self.player = player
        self.end = False

    def set_player(self, player):
        """
        设置玩家编号
        :param player:
        :return:
        """
        self.player = player

    def get_action(self, board: Board):
        """
        返回落子位置
        :param board:
        :return:
        """
        return -1

    def set_end(self):
        """
        告知棋盘已结束
        :return:
        """
        self.end = True


class ConsolePlayer(PlayerBase):

    def __init__(self, player=1, random_move=False):
        super(ConsolePlayer, self).__init__(player)
        self.random_move = random_move

    def set_player(self, player):
        self.player = player

    def get_action(self, board):
        if self.random_move:
            # time.sleep(0.2)
            return random.choice(board.available)
        while True:
            try:
                location = input("玩家" + str(self.player) + "执" +
                                 ("黑" if self.player == board.start_player else "白") + "棋，输入落子（行 列）: ")
                if isinstance(location, str):
                    location = [int(n, 10) for n in re.split("[, ]", location)]
                move = board.location_to_move(location)
                if location[0] == -1 and location[1] == -1:
                    return -2
            except:
                move = -1

            if move != -1 and move not in board.available:
                logger.info("当前落子位置已有棋子，请换一个位置")
                continue

            if move == -1:
                logger.warning("严重错误：输入格式错误，应为 1,2 或 1 2")
                continue

            return move

    def __str__(self):
        return "Human {}".format(self.player)


class SocketPlayer(PlayerBase):

    def __init__(self, host, port, player=1):
        super(SocketPlayer, self).__init__(player)
        self.ip = host
        self.port = port
        self.sk = socket.socket()  # 创建套接字
        self.sk.bind((self.ip, self.port))  # 绑定服务地址
        self.sk.listen(1)

    def get_action(self, board):
        logger.debug("等待落子：")
        inp = ""

        # 遗留问题，无法重复落子
        # 落子重复该在哪一级检测？

        move = -1
        while move not in board.available:
            client_sock, _ = self.sk.accept()
            # 从UI获取输入
            while True:
                rec = client_sock.recv(1024)
                # rec 长度不会为0
                msg = rec.decode("utf-8")
                inp += msg
                if inp == "":
                    break
                if inp[-1] == '#':
                    inp = inp[:-1]  # 接收全部输入
                    # print("数据接收完了")
                    break
            # print(inp)
            js_inp = json.loads(inp)
            i = js_inp["row"]
            j = js_inp["col"]
            logger.debug("已收到输入{}行{}列".format(i, j))
            move = board.location_to_move((i, j))
            if move not in board.available:
                move = -1
            client_sock.close()

        # 把棋盘状态通过同一个socket返回给UI
        # pack = board.pack_board()
        # j_pack = json.dumps(pack) + "@"
        # client_sock.sendall(j_pack.encode("utf-8"))

        # 关闭这个socket对象
        return move

    def set_end(self):
        self.end = True
        # 关闭整个socket连接
        self.sk.close()


class HttpPlayer(PlayerBase):
    def __init__(self, player=1, url=None):
        super(HttpPlayer, self).__init__(player)
        self.url = url

    def get_action(self, board):
        pass