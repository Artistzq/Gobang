class MCTSPlayer:
    """
    疑问4：这个类干嘛的
    """

    def __init__(self, fn=None, c_puct=0, n_playout=0, is_selfplay=1):
        self.player = 1

    def get_action(self, board, temperature=1e-3, return_prob: bool=True):
        if return_prob:
            return 1, 0.5


    def reset_player(self):
        pass

    def set_player_index(self, idx):
        self.player = idx
        pass