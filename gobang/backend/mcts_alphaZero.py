import numpy as np

from gobang.backend.player import PlayerBase


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
        self._parent = parent
        self._children = {}  # {动作：树节点}
        self._n_visits = 0  # 该节点被访问次数
        self._Q = 0  # Q值
        self._P = prior_p
        self._U = 0

    def select(self, c_puct):
        """
        在子结点中选择U+Q最大的子节点并返回
        :param c_puct:
        :return: Tuple(被选择的动作，执行该动作后跳转的节点)
        """
        return max(self._children.items(), key=lambda act_node: act_node[1].get_value(c_puct))

    def get_value(self, c_puct):
        self._U = (c_puct*self._P*np.sqrt(self._parent._n_visits)/(1+self._n_visits))
        return self._Q + self._U


class MCTSPlayer(PlayerBase):
    """
    实现蒙特卡洛树搜索
    """

    def __init__(self, fn=None, c_puct=0, n_playout=0, is_selfplay=1):
        super(MCTSPlayer, self).__init__(1)
        self.player = 1

    def get_action(self, board, temperature=1e-3, return_prob: bool=True):
        if return_prob:
            return 1, 0.5


    def reset_player(self):
        pass

    def set_player(self, player):
        self.player = player
        pass