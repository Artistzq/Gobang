import random
import re
import log
from game import Board

logger = log.Logger(log.path, logger_name=__name__).get_logger()


class PlayerBase:

    def __init__(self, player):
        self.player = player

    def get_action(self, board):
        return -1


class ConsolePlayer(PlayerBase):

    def __init__(self, player=1, random_move=False):
        super(ConsolePlayer, self).__init__(player)
        self.random_move = random_move

    def set_player(self, player):
        self.player = player

    def get_action(self, board: Board):
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
