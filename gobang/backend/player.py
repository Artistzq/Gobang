import random
import re

import json
import socket
from gobang.utils import log

# from game import Board

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

    def get_action(self, board):
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

    def __init__(self, player=1, host="127.0.0.1", port=30606):
        super(SocketPlayer, self).__init__(player)
        self.ip = host
        self.port = port
        self.sk = socket.socket()  # 创建套接字
        self.sk.bind((self.ip, self.port))  # 绑定服务地址
        self.sk.listen(1)

    def get_action(self, board):
        logger.debug("监听输入中：")
        client_sock, addr = self.sk.accept()
        inp = ""

        # print("已建立链接")

        while True:
            rec = client_sock.recv(1024)
            # rec 长度不会为0
            msg = rec.decode("utf-8")
            inp += msg
            print(inp)
            if inp[-1] == '#':
                inp = inp[:-1]  # 接收全部输入
                # print("数据接收完了")
                break
        try:
            j_inp = json.loads(inp)
            i = j_inp["row"]
            j = j_inp["col"]
            logger.debug("已收到输入：{}行{}列".format(i, j))
            move = board.location_to_move((i, j))
        except:
            move = -1

        client_sock.close()
        # print(move)
        return move

    def set_end(self):
        self.end = True
        self.sk.close()


class HttpPlayer(PlayerBase):
    def __init__(self, player=1, url=None):
        super(HttpPlayer, self).__init__(player)
        self.url = url

    def get_action(self, board):
        pass