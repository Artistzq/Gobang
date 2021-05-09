import copy
from typing import Dict

import numpy as np

from gobang.backend.board import Board
from gobang.backend.player import PlayerBase


def softmax(x):
    probs = np.exp(x - np.max(x))
    probs /= np.sum(probs)
    return probs


class TreeNode:
    """
    蒙特卡洛搜索树节点
    """

    def __init__(self, parent, prior_p):
        """
        初始化节点
        :param parent: 父节点
        :param prior_p: 当前节点被选择的先验概率
        """
        self.parent: TreeNode = parent
        self.children: Dict[int, TreeNode] = {}  # {动作(action，即落子位置)：树节点(TreeNode)}
        self.n_visits = 0  # 该节点被访问次数
        self._Q = 0  # Q值
        self._P = prior_p
        self._U = 0

    def select(self, c_puct):
        """
        在子结点中选择U+Q最大的子节点并返回
        :param c_puct:
        :return: Tuple(被选择的动作，执行该动作后跳转的结点)
        """
        return max(self.children.items(), key=lambda act_node: act_node[1].get_value(c_puct))

    def get_value(self, c_puct):
        self._U = (c_puct * self._P * np.sqrt(self.parent.n_visits) / (1 + self.n_visits))
        return self._Q + self._U

    def expand(self, actions_priors):
        """
        扩展self结点
        :param actions_priors: self结点下的可行动作和其对应的先验概率 列表
        """
        for action, prior in actions_priors:
            if action not in self.children:
                self.children[action] = TreeNode(parent=self, prior_p=prior)

    def update(self, leaf_value):
        """
        根据叶节点的值 更新self结点的访问次数和Q值
        :param leaf_value: 叶节点的值
        :return:
        """
        self.n_visits += 1
        # print("注意这里删除了1.0*")
        self._Q += 1.0 * (leaf_value - self._Q) / self.n_visits

    def update_recursively(self, leaf_value):
        """
        递归更新从叶子节点到根节点这整条路经上的结点的访问次数和Q值
        :param leaf_value:
        :return:
        """
        if not self.is_root():
            # 注意取反
            self.parent.update_recursively(-leaf_value)
        self.update(leaf_value)

    def is_leaf(self):
        return len(self.children) == 0

    def is_root(self):
        return self.parent is None


class MCTS():
    """
    蒙特卡洛树搜索算法的实现
    """

    def __init__(self, policy_value_fn, c_puct=5, n_playout=10000):
        """
        :param policy_value_fn: 策略价值网络中的方法
        :param c_puct: MCTS执行过程中探索的程度
        :param n_playout: MCTS循环执行的次数
        """
        self._root = TreeNode(None, 1.0)
        # 疑问：先验概率为什么要1.0
        self._policy = policy_value_fn
        self._c_puct = c_puct
        self._n_playout = n_playout

    def _playout(self, state: Board):
        """
        从根节点出发，完整的执行MCTS的选择，扩展，评估和回传
        :param state: 根节点（棋盘局面）
        :return: None
        """
        node = self._root
        # 选择，直到叶节点，而不是到棋盘终局
        while not node.is_leaf():
            # 获取动作（落子位置），以及选择该动作后的棋盘局面（结点）
            action, node = node.select(self._c_puct)
            state.do_move(action)
        # 扩展，局面输入神经网络，返回落子概率和对应的叶节点值，局面评估
        action_priors, leaf_value = self._policy(state)
        end, winner = state.game_end()
        if not end:
            # 如果还没到终局，则扩展该节点
            node.expand(action_priors)
        else:
            # 否则，设定leaf_value值
            if winner == -1:
                leaf_value = 0.0
            else:
                leaf_value = 1.0 if winner == state.get_current_player() else -1.0
        node.update_recursively(-leaf_value)

    def get_move_probs(self, state: Board, temp=1e-3):
        """
        返回该棋盘状态下，所有可行动作及其对应的概率
        :param state: 棋盘局面
        :param temp: 控制探索程度
        :return:
        """
        for n in range(self._n_playout):
            state_copy = copy.deepcopy(state)
            # 更新了self树
            self._playout(state_copy)

        action_visits = [(act, node.n_visits) for act, node in self._root.children.items()]
        acts, visits = zip(*action_visits)  # 类似转置
        act_probs = softmax(1.0 / temp * np.log(np.array(visits) + 1e-10))  # 公式
        return acts, act_probs

    def update_with_move(self, last_move):
        """
        复用搜索子树
        :param last_move:
        :return:
        """
        if last_move in self._root.children:
            # 如果已被扩展，可以复用
            self._root = self._root.children[last_move]
            self._root.parent = None
        else:
            # 没被扩展，新建一棵树
            self._root = TreeNode(None, 1.0)


class MCTSPlayer(PlayerBase):
    """
    AI玩家
    """

    def __init__(self, policy_value_fn=None, c_puct=5, n_playout=2000, is_self_play=0, player=0):
        super(MCTSPlayer, self).__init__(player)
        self.mcts = MCTS(policy_value_fn, c_puct, n_playout)
        self.is_self_play = is_self_play

    def get_action(self, board, temperature=1e-3, return_prob: bool = False):
        """
        根据MCTS和策略价值网络计算落子位置，并返回
        :param board: 棋盘局面
        :param temperature: 探索程度
        :param return_prob: 是否返回棋盘每个落子概率 pi， 自我对弈收集数据时需要设置为True，人机对战设为False即可
        :return: 落子位置
        """
        sensible_moves = board.available
        move_probs = np.zeros(board.width*board.height) # 相当于打表，
        if len(sensible_moves) > 0:
            # 还有落子的位置
            acts, probs = self.mcts.get_move_probs(board, temperature)
            move_probs[list(acts)] = probs # 设置对应落子位置的概率
            if self.is_self_play:
                # 自我博弈收集数据
                move = np.random.choice(
                    acts, p=0.75 * probs + 0.25 * np.random.dirichlet(0.3*np.ones(len(probs)))
                )
                # 更新根节点，复用搜索子树
                # 疑问：不懂
                self.mcts.update_with_move(move)
            else:
                # 人机对弈
                move = np.random.choice(acts, p=probs)
                # 重置根节点
                self.mcts.update_with_move(-1)
                print("AI落子：{}".format(board.move_to_location(move)))

            if return_prob:
                return move, move_probs
            else:
                return move

        else:
            print("没有落子位置了，应该在Game层级结束棋局，结果为平局，玩家实例随着游戏实例的结束而结束，这句话在平局的最后一步出现，概率很小")

    def reset_player(self):
        """
        :return:
        """
        self.mcts.update_with_move(-1)
