import numpy as np


class Board:
    """
    棋盘类，提供棋盘的管理
    """

    def __init__(self, width=12, height=12, n_in_row=5, start_player=1):
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
        self.init_board(start_player)

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

    def reset_board(self):
        self.init_board(self.start_player)

    def move_to_location(self, move):
        return move // self.width, move % self.width

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

    def current_state(self, feat_nums=4) -> np.ndarray:
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
        """
        根据最后落子快速判断输赢
        :return:
        """
        width = self.width
        height = self.height
        states = self.states
        n = self.n_in_row

        moved = list(set(range(width * height)) - set(self.available))
        # 双方博弈，最少也有 n 个棋子 + 另外两个，一方才够5子
        # 疑问2
        if len(moved) < self.n_in_row + 2:
            return False, -1

        move = moved[-1]
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

    def game_end(self, fast_judge=False):
        """
        判断该棋盘上局面是否结束，若结束且非平局，返回胜者
        :return: 是否结束，胜利者；
        """
        if fast_judge:
            win, winner = self.judge_with_last_move()
        else:
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

    def pack_last(self):
        """
        返回最近一步的状态
        :return:
        """
        pass

    def pack_board(self):
        """
        :return: 棋局的全部状态{"width", "n", "start_player", "pos_player"}
        """
        # pos_player = dict([(self.move_to_location(move), player) for (move, player) in self.states.items()])
        pos_player = [self.move_to_location(move) + (player, ) for (move, player) in self.states.items()]
        pack = {"width": self.width, "n": self.n_in_row, "start_player": self.start_player, "pos_player": pos_player,
                "current_player": self.current_player, "finished": (self.has_a_winner())[0],
                "winner": (self.has_a_winner())[1]}
        return pack
