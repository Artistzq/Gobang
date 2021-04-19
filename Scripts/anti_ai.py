from game import Board, Game
from mcts_alphaZero import MCTSPlayer
from policy_value_net_pytorch import PolicyValueNet
import re
import log

logger = log.Logger(log.path, logger_name=__name__).get_logger()
import sys


class Human:

    def __init__(self, player=1):
        self.player = player

    def set_player(self, player):
        self.player = player

    def get_action(self, board):
        while True:
            try:
                location = input("玩家 " + str(self.player) + " 落子（行 列）: ")
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


if __name__ == '__main__':
    assert len(sys.argv) == 3, "参数错误，应为 python anti_ai.py [width] [height]"
    width = int(sys.argv[1]) if int(sys.argv[1]) >= 0 else 12
    height = int(sys.argv[2]) if int(sys.argv[2]) >= 0 else 12
    board = Board(width, height)
    game = Game(board)
    entity1, entity2 = Human(), Human()
    # 人人对战，始终黑棋先下
    f = open(log.path, 'w')
    f.seek(0)
    f.truncate()
    f.close()
    sp = int(input("选择玩家1还是玩家2作为先手（执黑棋）？输入1或2："))
    game.start_play(entity1, entity2, start_player=sp, is_shown=1)
