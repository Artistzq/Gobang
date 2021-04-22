import sys

from game import Board, Game
from player import ConsolePlayer, SocketPlayer
from utils import log

logger = log.Logger(log.path, logger_name=__name__).get_logger()

if __name__ == '__main__':
    assert len(sys.argv) == 3, "参数错误，应为 python backend_game_manager.py [width] [height]"
    width = int(sys.argv[1]) if int(sys.argv[1]) >= 0 else 12
    height = int(sys.argv[2]) if int(sys.argv[2]) >= 0 else 12
    game = Game(Board(width, height))
    entity1, entity2 = ConsolePlayer(random_move=False), ConsolePlayer(random_move=False)
    # 人人对战，始终黑棋先下
    logger.debug("开始一场对局")
    sp = int(input("选择玩家1还是玩家2作为先手（执黑棋）？输入1或2："))
    game.start_play(entity1, entity2, start_player=sp, is_shown=1)
