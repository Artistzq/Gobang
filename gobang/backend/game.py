import os

import numpy as np

from gobang.backend.board import Board
from gobang.utils import log
from gobang.backend.mcts_alphaZero import MCTSPlayer
from gobang.backend.player import PlayerBase

logger = log.Logger(filename=log.path, logger_name=__name__).get_logger()


class Game(object):
    """
    一场对局，从初始化一个棋盘开始
    """
    PREVIOUS = 1
    LAST = 2

    def __init__(self, board: Board):
        """
        :param board: 棋盘
        """
        self.board = board

    def reset(self):
        self.board.reset_board()

    def start_self_play(self, player: MCTSPlayer, is_shown=False, temperature=1e-3):
        """
        执行一段完整的自我对局
        :param player:
        :param is_shown:
        :param temperature:
        :return: 胜者，以及（局面，概率，胜者）
        """
        self.board.init_board()
        p1, p2 = self.board.players
        states, mcts_probs, current_players = [], [], []
        while True:
            # 从树搜索获取下一步的策略
            move, move_probs = player.get_action(self.board, temperature, True)

            # 保存自我对弈的数据，即保存当前的棋局状态、玩家、落子概率
            states.append(self.board.current_state())
            mcts_probs.append(move_probs)
            current_players.append(self.board.current_player)

            # 落子
            self.board.do_move(move)

            # 绘制当前局面
            if is_shown:
                self.console_show(self.board, p1, p2)

            # 判断结束否
            is_end, winner = self.board.game_end()

            if is_end:
                # 从每一个state对应的player视角保存胜负信息
                # 疑问：为什么叫winner_z
                winners_z = np.zeros(len(current_players))  # shape: (len(current_players, )
                if winner != -1:
                    # 非平局，winner == 1 或 winner == 2
                    winners_z[np.array(current_players) == winner] = 1.0  # 胜者玩家对应位记为 1.0
                    winners_z[np.array(current_players) != winner] = -1.0
                player.reset_player()

                if is_shown:
                    if winner != -1:
                        # 非平局
                        print("Game end. Winner is player:", winner)
                    else:
                        print("Game end. Tile")

                # 疑问3：这个返回值用处是什么
                return winner, zip(states, mcts_probs, winners_z)

    def console_show(self, board: Board, player1, player2, start_player=1):
        """
        绘制
        :param board:
        :param player1: 先手玩家，黑棋
        :param player2: 白棋
        :param start_player:
        :return:
        """
        width, height = board.width, board.height
        os.system('cls')

        print("Player", start_player, "with 黑".rjust(3))
        print("Player", 2 if start_player == 1 else 1, "with 白".rjust(3))
        print("落子-1 -1，退出游戏")
        print()

        for i in range(height - 1, -1, -1):
            print("{0:4d}".format(i), end='')
            for j in range(width):
                loc = i * width + j
                p = board.states.get(loc, -1)
                # modified
                if p == start_player:
                    print('黑'.center(8), end='')
                elif p != -1:
                    print('白'.center(8), end='')
                else:
                    print('_'.center(8), end='')
            print("\r\n\r\n")

        for x in range(width):
            print("{0:8}".format(x), end='')
        print("\r\n")

    def start_play(self, entity1: PlayerBase, entity2: PlayerBase, start_player=1, is_shown=0):
        """
        实体1和实体2之间进行一场对局
        :param entity1:  第一个下棋实体
        :param entity2:  第二个下棋实体
        :param start_player: 指名谁是先手，谁是后手，先手执黑棋
        :param is_shown:
        :return: 赢家
        """
        # assert start_player in (0, 1), "player index overflow"
        # 初试化棋盘，即清空，且设置先手
        self.board.init_board(start_player)
        player1, player2 = self.board.players
        entity1.set_player(player1)
        entity2.set_player(player2)
        entities = {player1: entity1, player2: entity2}
        # 等价于：players = {1: entity1, 2: entity2}
        # entity1 和 entity2 是两个类，或者是蒙特卡洛树玩家，或者是人类玩家

        if is_shown:
            self.console_show(self.board, entity1.player, entity2.player, start_player)
            logger.debug("先手（执黑棋）玩家：" + str(start_player))

        end: bool = False
        winner = -1
        while True:
            # 循环直到对局结束
            current_player = self.board.get_current_player()
            entity_in_turn = entities[current_player]
            # 获取下棋位置
            move = entity_in_turn.get_action(self.board)
            entity_in_turn.send_pack()

            if move == -2:
                end = True
                winner = -1
                logger.warning("游戏意外结束，平局")
                return winner

            # 棋盘执行落子
            self.board.do_move(move)

            if is_shown:
                self.console_show(self.board, entity1.player, entity2.player, start_player)

            if self.board.states:
                loc = self.board.move_to_location(move)
                player = self.board.states.get(move)
                # logger.debug("本次落子由玩家" + str(player) + " 放置在" + str(loc[0]) + "行" + str(loc[1]) + "列")

            end, winner = self.board.game_end()
            if end:
                entity1.set_end()
                entity2.set_end()
                if is_shown:
                    if winner != -1:
                        print("游戏结束，胜者为：玩家", winner)
                    else:
                        print("平局")
                    print(self.board.current_state())
                return winner


class SocketGame(Game):
    def __init__(self, board):
        super(SocketGame, self).__init__(board)
        # 准备连接，提供一开始的棋盘等信息

    def play(self):
        pass
