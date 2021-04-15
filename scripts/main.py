from __future__ import  print_function

import random
import numpy as np
from collections import deque
from game import Board, Game
from mcts_alphaZero import MCTSPlayer
from policy_value_net_pytorch import PolicyValueNet

class TrainPipeline:

    def __init__(self, init_model=None):
        self.board_width = 8
        self.board_height = 8
        self.n_in_row = 5
        self.board = Board(width=self.board_width, height=self.board_height, n_in_row=self.n_in_row)
        self.game = Game(self.board)
        # 自我博弈参数
        self.temperature = 1.0
        self.c_puct = 5 # 蒙特卡洛树平衡参数
        self.n_playout = 400 # MCTS模拟次数
        # 训练更新 相关参数
        self.learn_rate = 2e-3
        self.buffer_size = 10000
        self.batch_size = 512
        self.data_buffer = deque(maxlen=self.buffer_size)
        self.check_freq = 50 # 保存模型的频率
        self.game_batch_num = 3000  # 训练更新的次数, epoch

        if init_model is not None:
            self.policy_value_net = PolicyValueNet(self.board_width, self.board_height, init_model)
        else:
            # 随机
            self.policy_value_net = PolicyValueNet(self.board_width, self.board_height)
        self.mcts_player = MCTSPlayer(self.policy_value_net.policy_value_fn, self.c_puct, self.n_playout, is_selfplay=1)

    def get_equi_data(self, playdata):
        """
        获得更多的等价局面
        :param playdata: List[(state, mcts_prob, winner_z)]
        :return:
        """
        augment_data = []
        for state, mcts_prob, winner in playdata:
            for i in range(1, 5):
                pass

        pass

    def collect_selfplay_data(self):
        """
        调用Game中的自我对弈函数，收集训练中的自我对弈数据，用来训练
        :return:
        """
        winner, play_data = self.game.start_self_play(self.mcts_player, temperature=self.temperature)
        play_data = list(play_data)[:] # 意义何在？
        episode_len = len(play_data)

        # 旋转局面，获得更多的训练数据
        play_data = self.get_equi_data(play_data)
        self.data_buffer.extend(play_data)
        return episode_len


    def policy_update(self):
        return []

    def run(self):
        """
        完整的训练流程
        :return:
        """
        try:
            for i in range(self.game_batch_num):
                # whats this
                episode_len = self.collect_selfplay_data() #疑问：这是什么用的
                if len(self.data_buffer) > self.batch_size:
                    loss, entropy = self.policy_update()
                    print("batch i:{}, episode_len: {}, loss:{:.4f}, entropy:{:.4f}".format(i+1, episode_len, loss, entropy))
                else:
                    print("batch i:{}, episode_len:{}".format(i+1, episode_len))
                # save model
                if (i+1)%self.check_freq == 0:
                    self.policy_value_net.save_model("./current_policy.model")
        except KeyboardInterrupt:
            print("\n quit")






