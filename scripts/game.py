import numpy as np
from mcts_alphaZero import MCTSPlayer


class Board:

    def __init__(self, width=8, height=8, n_in_row=5) -> None:
        self.width = width
        self.height = height
        self.n_in_row = n_in_row
        self.players = (1, 2)
        self.states = {}
        self.current_player = 0

    def init_board(self, player_index=0):
        assert self.width >= self.n_in_row and self.height >= self.n_in_row, "board too small"
        # 当前玩家设置为初始玩家
        self.current_player = self.players[player_index]
        # 可落子位置设置为全部位置
        self.available = list(range(self.width * self.height))
        # 棋局走子记录设为空
        self.states = {}  # 走子: 对应玩家
        # 最后一步设为-1，即没有落子
        self.last_move = -1

    def move_to_location(self, move):
        return [move // self.width, move % self.width]

    def location_to_move(self, location):
        h, w = location
        return h + w * self.width

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
        self.current_player = self.players[0 if self.current_player == self.players[1] else 1]
        # 记录最后一个落子位置
        self.last_move = move

    def get_current_player(self):
        return self.current_player

    def current_state(self, feat_nums=4):
        """
        返回局面，用于神经网络输入
        :param feat_nums: 二值特征平面个数
        :return: shape(feat_nums, height, width)
        """
        square_state = np.zeros((feat_nums, self.width, self.height))
        if self.states:
            # not null
            moves, players = np.array(list(zip(*self.states.items())))
            move_curr = moves[players == self.current_player]
            move_oppo = moves[players != self.current_player]
            square_state[0][move_curr // self.width, move_curr % self.width] = 1.0
            # 等价写法
            # h, w = self.move_to_location(moves[...])
            # square_state[0][h, w] = 1.0
            square_state[1][move_oppo // self.width, move_oppo % self.width] = 1.0
            square_state[2][self.last_move // self.width, self.last_move % self.width] = 1.0
            if len(self.states) % 2 == 0:
                square_state[3][:, :] = 1.0
            # 疑问1 为什么要倒序
            return square_state[:, ::-1, :]

    def judge_immediately(self, location):
        pass

    def has_a_winner(self):
        """
        :return: does it has a winner (bool), the winner (int)
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
            if w in range(width - n + 1) and len(set(states.get(i, default=-1) for i in range(move, move + n))) == 1:
                return True, player
            # 左上到左下，range 步长=width+1
            if h in range(height - n + 1) and len(
                    set(states.get(i, default=-1) for i in range(move, move + n * (width + 1), width + 1))) == 1:
                return True, player

            if w in range(width - n + 1) and h in range(height - n + 1) and len(
                    set(states.get(i, -1) for i in range(move, move + n * (width + 1), width + 1))) == 1:
                return True, player

            if w in range(n - 1, width) and h in range(height - n + 1) and len(
                    set(states.get(i, -1) for i in range(move, move + n * (width - 1), width - 1))) == 1:
                return True, player

        return False, -1

    def game_end(self):
        win, winner = self.has_a_winner()
        if win:
            return True, winner
        elif len(self.available):
            return True, -1
        else:
            # 没有可落子位置，而且没有胜者，则平局
            return False, -1


class Game(object):

    def __init__(self, board: Board):
        self.board = board

    def start_self_play(self, player: MCTSPlayer, is_shown=False, temperature=1e-3):
        """
        执行一段完整的对局
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

    def graphic(self, board: Board, player1, player2):
        width, height = board.width, board.height
        print("Player", player1, "with X".rjust(3))
        print("Player", player2, "with O".rjust(3))
        print()

        for x in range(width):
            print("{0:8}".format(x), end='')
        print("\r\n")

        for i in range(height - 1, -1, -1):
            print("{0:4d}".format(i), end='')
            for j in range(width):
                loc = i * width + j
                p = board.states.get(loc, -1)
                if p == player1:
                    print('X'.center(8), end='')
                elif p == player2:
                    print('O'.center(8), end='')
                else:
                    print('_'.center(8), end='')
            print("\r\n\r\n")

        pass

    def start_play(self, player1: MCTSPlayer, player2: MCTSPlayer, start_player=0, is_shown=1):
        """

        :param player1:
        :param player2:
        :param start_player:
        :param is_shown:
        :return: 赢家
        """
        assert start_player in (0, 1), "player not exist"
        self.board.init_board(player_index=start_player)
        p1, p2 = self.board.players
        player1.set_player_index(p1)
        player2.set_player_index(p2)
        players = {p1: player1, p2: player2}  # 疑问5：为什么多此一举用字典，不是元组
        if is_shown:
            self.graphic(self.board, player1.player, player2.player)
        while True:
            current_player = self.board.get_current_player()
            player_in_turn: MCTSPlayer = players[current_player]
            move = player_in_turn.get_action(self.board)
            self.board.do_move(move)

            end: bool = False
            winner = -1
            if is_shown:
                self.graphic(self.board, player1.player, player2.player)
                end, winner = self.board.game_end()

            if end:
                if is_shown:
                    if winner != -1:
                        print("Game end. Winner is ", players[winner])
                    else:
                        print("Game end. Tie")
                return winner


if __name__ == '__main__':
    board = Board()
    game = Game(board)
    player1, player2 = MCTSPlayer(), MCTSPlayer()
    game.start_play(player1, player2, 0)
