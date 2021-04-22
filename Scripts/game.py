import os

import numpy as np

from mcts_alphaZero import MCTSPlayer
from player import PlayerBase
from utils import log

logger = log.Logger(filename=log.path, logger_name=__name__).get_logger()


class Board:
    """
    棋盘类，提供棋盘的管理
    """

    def __init__(self, width=8, height=8, n_in_row=5):
        """
        初始化棋盘，设定参数
        :param width: 宽
        :param height: 高
        :param n_in_row: 该参数表示n个棋子连成一线可以获胜
        """
        assert width >= n_in_row and height >= n_in_row, "board too small"
        self.width = width
        self.height = height
        self.n_in_row = n_in_row
        self.players = [1, 2]  # 1：先手黑棋，2：后手白棋
        self.states = {}  # {走子: 对应玩家(1, 2)}
        self.current_player = 1  # 当前玩家，即当前局面下该走子的玩家，1或2
        self.available = list(range(self.width * self.height))
        self.last_move = -1
        self.winner = -1
        self.end = -1

    def init_board(self, start_player=1):
        """
        重置棋盘，设定先手，清空落子位置，清空对局记录，清空最后一步
        :param start_player: 设定先手，1为黑棋先手，2为白棋先手
        """
        self.start_player = start_player
        # 当前玩家设置为初始玩家
        self.current_player = start_player
        # 可落子位置设置为全部位置
        self.available = list(range(self.width * self.height))
        # 棋局走子记录设为空
        self.states = {}  # {走子: 对应玩家(1, 2)}
        # 最后一步设为-1，即没有落子
        self.last_move = -1

    def move_to_location(self, move):
        return [move // self.width, move % self.width]

    def location_to_move(self, location):
        """
        :param location: 行，列
        :return:
        """
        if len(location) != 2:
            return -1
        h, w = location
        if w + h * self.width not in range(self.width * self.height):
            return -1
        return w + h * self.width

    def do_move(self, move):
        """
        根据落子位置记录一些状态
        :param move: 落子位置
        """
        # 记录落子位置和落子玩家编号
        self.states[move] = self.current_player
        # 可落子位置中移除该位置
        self.available.remove(move)
        # 改变当前玩家
        self.current_player = self.players[0] if self.current_player == self.players[1] else self.players[1]
        # 记录最后一个落子位置
        self.last_move = move

    def get_current_player(self):
        """
        返回当前该落子的玩家
        :return: 玩家，1或2
        """
        return self.current_player

    def current_state(self, feat_nums=4):
        """
        返回局面，矩阵表示，用于神经网络输入
        :param feat_nums: 二值特征平面个数
        :return: shape(feat_nums, height, width)
        """
        square_state = np.zeros((feat_nums, self.width, self.height))
        if self.states:
            moves, players = np.array(list(zip(*self.states.items())))
            move_curr = moves[players == self.current_player]
            move_oppo = moves[players != self.current_player]
            square_state[0][move_curr // self.width, move_curr % self.width] = 1.0
            # 等价写法
            # h, w = self.move_to_location(moves[...])
            # square_state[0][h, w] = 1.0
            square_state[1][move_oppo // self.width, move_oppo % self.width] = 1.0
            # 第三个平面，只置了一个1
            square_state[2][self.last_move // self.width, self.last_move % self.width] = 1.0
            if len(self.states) % 2 == 0:
                # state长为偶数，即当前双方都已走完子，当前的player应该为先手玩家，置1
                square_state[3][:, :] = 1.0
            # 疑问1 为什么要倒序
            # 答：把每个棋局上下翻转了一下，不知道为什么，翻转之后左下角就是0，0了
            return square_state[:, ::-1, :]

    def judge_with_last_move(self):
        pass

    def has_a_winner(self):
        """
        判断是否有赢家
        :return: Tuple(是否有赢家 True/False，赢家是谁 1,2, -1)
        """
        width = self.width
        height = self.height
        states = self.states
        n = self.n_in_row

        # 落子状况
        # 所有位置 - 可获得位置（空位置），就是已落子位置
        moved = list(set(range(width * height)) - set(self.available))
        # 双方博弈，最少也有 n 个棋子 + 另外两个，一方才够5子
        # 疑问2
        if len(moved) < self.n_in_row + 2:
            return False, -1

        # 遍历已落子位置
        for move in moved:
            h, w = move // width, move % width
            player = states[move]
            # 水平方向n子连成一线，则落子位置到落子位置水平+n, 这n个位置里，对应的玩家应该只有一个值，即len==1，不是0即为1，
            # 若有没下过，则get返回-1，否则get返回0或-1。不可能全为-1，因为当前位置move记录了某个玩家
            if w in range(width - n + 1) and len(set(states.get(i, -1) for i in range(move, move + n))) == 1:
                return True, player
            # 左上到左下，range 步长=width+1
            if h in range(height - n + 1) and len(
                    set(states.get(i, -1) for i in range(move, move + n * width, width))) == 1:
                return True, player

            if w in range(width - n + 1) and h in range(height - n + 1) and len(
                    set(states.get(i, -1) for i in range(move, move + n * (width + 1), width + 1))) == 1:
                return True, player

            if w in range(n - 1, width) and h in range(height - n + 1) and len(
                    set(states.get(i, -1) for i in range(move, move + n * (width - 1), width - 1))) == 1:
                return True, player

        return False, -1

    def game_end(self):
        """
        判断该棋盘上局面是否结束，若结束且非平局，返回胜者
        :return: 是否结束，胜利者；
        """
        win, winner = self.has_a_winner()
        if win:
            # 有胜者
            return True, winner
        elif not len(self.available):
            # 没有胜者，也没有落子位置，则游戏结束，平局
            return True, -1
        else:
            # 没有赢家，还有落子位置，接着下，没结束
            return False, -1

    def pack_board(self):
        pack = {"length": self.width, "n": self.n_in_row, "states": self.states,
                "pos": [self.move_to_location(move) for move in self.states.keys()], "start": self.start_player}
        return pack


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
                self.graphic(self.board, p1, p2)

            # 判断结束否
            isEnd, winner = self.board.game_end()

            if isEnd:
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

    def graphic(self, board: Board, player1, player2, start_player=1):
        """
        绘制
        :param board:
        :param player1: 先手玩家，黑棋
        :param player2: 白棋
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

    def start_play(self, entity1: PlayerBase, entity2: PlayerBase, start_player=1, is_shown=1):
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
            self.graphic(self.board, entity1.player, entity2.player, start_player)
            logger.debug("先手（执黑棋）玩家：" + str(start_player))

        end: bool = False
        winner = -1
        while True:
            # 循环直到对局结束
            current_player = self.board.get_current_player()
            entity_in_turn = entities[current_player]
            # 获取下棋位置
            move = entity_in_turn.get_action(self.board)

            if move == -2:
                end = True
                winner = -1
                logger.warning("游戏意外结束，平局")
                return winner

            # 棋盘执行落子
            self.board.do_move(move)

            if is_shown:
                self.graphic(self.board, entity1.player, entity2.player, start_player)

            if self.board.states:
                loc = self.board.move_to_location(move)
                player = self.board.states.get(move)
                logger.debug("本次落子由玩家" + str(player) + " 放置在" + str(loc[0]) + "行" + str(loc[1]) + "列")

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

