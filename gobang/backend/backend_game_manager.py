import json
import socket

from game import Board, OnlineGame
from gobang.utils import log

logger = log.Logger(log.path, logger_name=__name__).get_logger()


def get_init_para(socket):
    # s = socket(host, port)
    pass


def send_init_para(main_socket: socket.socket, width, pack):
    msg = json.dumps([width, pack])
    main_socket.sendall(msg.encode("utf-8"))


if __name__ == '__main__':
    # assert len(sys.argv) == 3, "参数错误，应为 python backend_game_manager.py [width] [height]"
    # width = int(sys.argv[1]) if int(sys.argv[1]) >= 0 else 19
    # height = int(sys.argv[2]) if int(sys.argv[2]) >= 0 else 19
    width = 19
    host, port = "127.0.0.1", 20223
    ui_address = ("127.0.0.1", 20488)
    game = OnlineGame(Board(width, width), host_port=(host, port), ui_address=ui_address)

    # 人人对战，始终黑棋先下
    # logger.debug("开始一场对局")
    # sp = int(input("选择玩家1还是玩家2作为先手（执黑棋）？输入1或2："))
    # game.start_play(entity1, entity2, start_player=sp, is_shown=0)
    # logger.debug("主程序等待连接")
    # main_socket = socket.socket()
    # main_socket.bind((host, port))
    # main_socket.listen(5)
    # ui_socket, _ = main_socket.accept()
    # logger.debug("主程序已连接UI")
    # pack = game.board.pack_board()
    # send_init_para(ui_socket, width, pack)
    # ui_socket.close()
    # logger.debug("主程序已向UI发送参数，开始游戏")
    # main_socket.close()
    # game已经开始监听