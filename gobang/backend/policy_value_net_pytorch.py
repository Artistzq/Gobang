import numpy as np
import torch
import torch.nn as nn
from torch import optim
from torch.autograd import Variable
from torch.nn import functional as F

from gobang.backend.board import Board

def set_learning_rate(optimizer, lr):
    for param_group in optimizer.param_groups:
        param_group["lr"] = lr


use_gpu = torch.cuda.is_available()
print(use_gpu)
use_gpu = True
# 使用三层全卷积网络，而不是残差网络


class Net(nn.Module):
    """策略价值网络结构"""

    def __init__(self, board_width, board_height=None):
        super(Net, self).__init__()
        self.board_width = board_width
        self.board_height = board_width

        # 公共层
        self.conv1 = nn.Conv2d(4, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)

        # 策略层 卷积，全连接
        self.action_conv1 = nn.Conv2d(128, 4, kernel_size=1)
        self.action_fc1 = nn.Linear(4 * board_width * board_width, board_width * board_width)

        # 价值层
        self.value_conv1 = nn.Conv2d(128, 2, kernel_size=1)
        self.value_fc1 = nn.Linear(2 * board_width * board_width, 64)
        self.value_fc2 = nn.Linear(64, 1)

    def forward(self, state_input):
        # 公共层
        x = F.relu(self.conv1(state_input))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))

        # 策略层
        x_act = F.relu(self.action_conv1(x))
        x_act = x_act.view(-1, 4 * self.board_width * self.board_width)
        inp = self.action_fc1(x_act)
        if inp.dim() == 0 or inp.dim() == 1 or inp.dim() == 3:
            ret = 0
        else:
            ret = 1
        x_act = F.log_softmax(inp, dim=ret)

        # 价值层
        x_val = F.relu(self.value_conv1(x))
        x_val = x_val.view(-1, 2 * self.board_width * self.board_width)
        x_val = F.relu(self.value_fc1(x_val))
        # x_val = F.tanh(self.value_fc2(x_val))
        x_val = torch.tanh(self.value_fc2(x_val))
        return x_act, x_val


class PolicyValueNet:
    def __init__(self, width, height, model_file=None):
        self.board_width = width
        self.board_height = height
        self.l2_const = 1e-4
        self.policy_value_net = Net(width, height)
        self.optimizer = optim.Adam(
            self.policy_value_net.parameters(),
            weight_decay=self.l2_const
        )
        if model_file:
            net_params = torch.load(model_file)
            self.policy_value_net.load_state_dict(net_params)

    def policy_value_fn(self, board: Board):
        availables = board.available
        current_states = np.ascontiguousarray(
            board.current_state().reshape((-1, 4, self.board_width, self.board_height)))
        # 这就核心的预测
        current_states_tensor = Variable(torch.from_numpy(current_states)).float()

        if use_gpu:
            current_states_tensor = current_states_tensor.cuda()
            self.policy_value_net = self.policy_value_net.cuda()

        log_act_probs, value = self.policy_value_net(current_states_tensor)

        if use_gpu:
            log_act_probs, value = log_act_probs.cpu(), value.cpu()

        act_probs = np.exp(log_act_probs.data.numpy().flatten())
        # 所有可行位置及其对应落子概率
        act_probs = zip(availables, act_probs[availables])
        # 局面评估值
        # 尝试用item()替代
        value = value.data[0][0]
        return act_probs, value

    def train_step(self, state_batch, mcts_probs, winner_batch, lr):
        """
        进行一次训练
        :param state_batch:
        :param mcts_probs:
        :param winner_batch:
        :param lr:
        :return:
        """
        # 转为张量
        state_batch = Variable(torch.FloatTensor(state_batch))
        mcts_probs = Variable(torch.FloatTensor(mcts_probs))
        winner_batch = Variable(torch.FloatTensor(winner_batch))

        # 梯度清零，此处需要再研究
        self.optimizer.zero_grad()
        # 设置学习率
        set_learning_rate(self.optimizer, lr)
        # 前向训练

        if use_gpu:
            state_batch = state_batch.cuda()
            self.policy_value_net = self.policy_value_net.cuda()

        log_act_probs, value = self.policy_value_net(state_batch)

        if use_gpu:
            log_act_probs, value = log_act_probs.cpu(), value.cpu()

        # 定义损失函数
        value_loss = F.mse_loss(value.view(-1), winner_batch)
        policy_loss = -torch.mean(torch.sum(mcts_probs * log_act_probs, 1))
        loss: torch.Tensor = value_loss + policy_loss

        if use_gpu:
            loss = loss.cuda()
        # 反向回溯并优化
        loss.backward()

        if use_gpu:
            loss = loss.cpu()

        self.optimizer.step()
        # 观察用的策略熵
        entropy = -torch.mean(torch.sum(torch.exp(log_act_probs) * log_act_probs, 1))
        # return loss.data[0], entropy.data[0]
        return loss.item(), entropy.item()

    def get_policy_param(self):
        net_params = self.policy_value_net.state_dict()
        return net_params

    def save_model(self, model_file):
        net_params = self.get_policy_param()
        torch.save(net_params, model_file)
