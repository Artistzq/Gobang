from __future__ import print_function

import random
import time
from collections import deque
from typing import List, Tuple

import sys
import os
sys.path.append(os.path.split(os.path.split(sys.path[0])[0])[0])

import numpy as np
from gobang.backend.board import Board
from gobang.backend.game import Game
from gobang.backend.mcts_alphaZero import MCTSPlayer
from gobang.backend.policy_value_net_pytorch import PolicyValueNet


class TrainPipeline:

    def __init__(self, width=8, height=8, n=300, init_model=None):
        self.save_model_path = init_model
        self.board_width = 8
        self.board_width = width
        self.board_height = 8
        self.board_height = height
        self.n_in_row = 5
        self.board = Board(width=self.board_width, height=self.board_height, n_in_row=self.n_in_row)
        self.game = Game(self.board)
        # 自我博弈参数
        self.temperature = 1
        self.c_puct = 5  # 蒙特卡洛树平衡参数
        self.n_playout = 300  # MCTS模拟次数
        self.n_playout = n
        # 训练更新 相关参数
        self.learn_rate = 2e-3
        self.buffer_size = 10000
        self.batch_size = 512
        self.data_buffer = deque(maxlen=self.buffer_size)
        self.check_freq = 1  # 保存模型的频率
        self.game_batch_num = 1000  # 训练更新的次数, epoch，自我博弈次数

        if init_model is not None:
            self.policy_value_net = PolicyValueNet(self.board_width, self.board_height, init_model)
        else:
            # 随机初始化网络
            self.policy_value_net = PolicyValueNet(self.board_width, self.board_height)
        self.mcts_player = MCTSPlayer(self.policy_value_net.policy_value_fn, self.c_puct, self.n_playout,
                                      is_self_play=1)

    def get_equi_data(self, playdata: List[Tuple[np.ndarray, np.ndarray, int]]):
        """
        获得更多的等价局面，旋转翻转
        :param playdata: List[(state, mcts_prob, winner_z)]
        :return:
        """
        augment_data = []
        for state, mcts_prob, winner in playdata:
            for i in range(1, 5):
                # 逆时针
                equi_state = np.array([np.rot90(s, i) for s in state])
                equi_mcts_prob = np.rot90(np.flipud(mcts_prob.reshape(self.board_height, self.board_width)), i)
                augment_data.append((equi_state, np.flipud(equi_mcts_prob).flatten(), winner))
                # 水平翻转
                equi_state = np.array([np.fliplr(s) for s in equi_state])
                equi_mcts_prob = np.fliplr(equi_mcts_prob)
                augment_data.append((equi_state, np.flipud(equi_mcts_prob).flatten(), winner))
        return augment_data

    def collect_selfplay_data(self):
        """
        调用Game中的自我对弈函数，收集训练中的自我对弈数据，用来训练
        :return:
        """
        winner, play_data = self.game.start_self_play(self.mcts_player, temperature=self.temperature)
        play_data = list(play_data)[:]  # 意义何在？
        episode_len = len(play_data)

        # 旋转局面，获得更多的训练数据
        play_data = self.get_equi_data(play_data)
        self.data_buffer.extend(play_data)
        return episode_len

    def policy_update(self):
        """
        更新策略价值网络
        :return:
        """
        mini_batch = random.sample(self.data_buffer, self.batch_size)
        state_batch, mcts_probs_batch, winner_batch = zip(*mini_batch)
        loss, entropy = self.policy_value_net.train_step(
            state_batch,
            mcts_probs_batch,
            winner_batch,
            self.learn_rate
        )
        return loss, entropy

    def run(self):
        """
        完整的训练流程
        :return:
        """
        try:
            for i in range(self.game_batch_num):
                # whats this
                # get action一次0.5s
                start = time.perf_counter()
                episode_len = self.collect_selfplay_data()  # 疑问：这是什么用的
                selfplay_end = time.perf_counter()
                # print("self_play_time_cost: {}".format(selfplay_end - start))
                # print(len(self.data_buffer))
                # print(self.batch_size)
                if len(self.data_buffer) > self.batch_size:
                    loss, entropy = self.policy_update()
                    print("batch_size: {}, batch i:{}, episode_len: {}, loss:{:.4f}, entropy:{:.4f}".format(
                        self.batch_size, i + 1, episode_len, loss, entropy))
                else:
                    print("batch i:{}, episode_len:{}".format(i + 1, episode_len))
                end = time.perf_counter()
                print("time cost: {}s".format(end - start))
                # save model
                if (i + 1) % self.check_freq == 0:
                    # self.policy_value_net.save_model("../resources/current_policy{}x{}.model".format(self.board_width, self.board_width))
                    self.policy_value_net.save_model(self.save_model_path)
        except KeyboardInterrupt:
            print("\n quit")


if __name__ == '__main__':

    training_pipeline = TrainPipeline(init_model="../resources/current_policy{}x{}.model".format(8, 8))
    training_pipeline.run()
