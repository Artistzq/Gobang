
from mcts_alphaZero import MCTSPlayer
from policy_value_net_pytorch import PolicyValueNet
import re

import log
from game import Board, Game
import sys
from player import ConsolePlayer


logger = log.Logger(log.path, logger_name=__name__).get_logger()

if __name__ == '__main__':
    assert len(sys.argv) == 3, "参数错误，应为 python anti_ai.py [width] [height]"
    width = int(sys.argv[1]) if int(sys.argv[1]) >= 0 else 12
    height = int(sys.argv[2]) if int(sys.argv[2]) >= 0 else 12
    board = Board(width, height)
    game = Game(board)
    entity1, entity2 = ConsolePlayer(), ConsolePlayer()
    # 人人对战，始终黑棋先下
    logger.debug("开始一场对局")
    sp = int(input("选择玩家1还是玩家2作为先手（执黑棋）？输入1或2："))
    game.start_play(entity1, entity2, start_player=sp, is_shown=1)
