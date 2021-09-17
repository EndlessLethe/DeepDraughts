# -*- coding: utf-8 -*-
"""
An implementation of the policyValueNet in PyTorch
Tested in PyTorch 0.2.0 and 0.3.0

@author: Junxiao Song
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.autograd import Variable
import numpy as np


def set_learning_rate(optimizer, lr):
    """Sets the learning rate to the given value"""
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr


class PolicyValueNet(nn.Module):
    """policy-value network module"""
    def __init__(self, nsize, n_states, n_actions):
        super(PolicyValueNet, self).__init__()

        self.board_width = nsize
        self.board_height = nsize
        self.n_states = n_states
        self.n_actions = n_actions

        # common layers
        self.conv1 = nn.Conv2d(4, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)

        # state layers
        self.st_fc1 = nn.Linear(n_states, 64)
        self.st_fc2 = nn.Linear(64, 64)

        # action policy layers
        self.act_conv1 = nn.Conv2d(128, 4, kernel_size=1)
        self.act_fc1 = nn.Linear(4*nsize*nsize+64, n_actions)

        # state value layers
        self.val_conv1 = nn.Conv2d(128, 2, kernel_size=1)
        self.val_fc1 = nn.Linear(2*nsize*nsize+64, 64)
        self.val_fc2 = nn.Linear(64, 1)

    def forward(self, vec_board, vec_state):
        if len(vec_board.shape) == 3:
            vec_board = torch.unsqueeze(vec_board, 0)
            vec_state = torch.unsqueeze(vec_state, 0)

        # common layers
        x = F.relu(self.conv1(vec_board))
        x = self.bn1(x)
        x = F.relu(self.conv2(x))
        x = self.bn2(x)
        x = F.relu(self.conv3(x))
        x = self.bn3(x)

        y = F.relu(self.st_fc1(vec_state))
        y = F.relu(y)

        # action policy layers
        x_act = F.relu(self.act_conv1(x))
        x_act = x_act.view(-1, 4*self.board_width*self.board_height)
        x_act = torch.cat((x_act, y), -1)

        x_act = F.log_softmax(self.act_fc1(x_act))

        # state value layers
        x_val = F.relu(self.val_conv1(x))
        x_val = x_val.view(-1, 2*self.board_width*self.board_height)
        x_val = torch.cat((x_val, y), -1)
        x_val = F.relu(self.val_fc1(x_val))
        x_val = F.tanh(self.val_fc2(x_val))

        return x_act, x_val


class Model():
    """policy-value network """
    def __init__(self, nsize, n_states, n_actions, MOVE_MAP, 
                 model_file=None, use_gpu=False):
        self.use_gpu = use_gpu
        self.board_width = nsize
        self.board_height = nsize
        self.MOVE_MAP = MOVE_MAP

        self.l2_const = 1e-4  # coef of l2 penalty
        # the policy value net module
        if self.use_gpu:
            self.policy_value_net = PolicyValueNet(nsize, n_states, n_actions).cuda()
        else:
            self.policy_value_net = PolicyValueNet(nsize, n_states, n_actions)
        self.optimizer = optim.Adam(self.policy_value_net.parameters(),
                                    weight_decay=self.l2_const)

        if model_file:
            net_params = torch.load(model_file)
            self.policy_value_net.load_state_dict(net_params)

    def policy_value_batch(self, state_batch):
        """
        input: a batch of states
        output: a batch of action probabilities and state values
        """
        if self.use_gpu:
            state_batch = Variable(torch.FloatTensor(state_batch).cuda())
            log_act_probs, value = self.policy_value_net(state_batch)
            act_probs = np.exp(log_act_probs.data.cpu().numpy())
            return act_probs, value.data.cpu().numpy()
        else:
            state_batch = Variable(torch.FloatTensor(state_batch))
            log_act_probs, value = self.policy_value_net(state_batch)
            act_probs = np.exp(log_act_probs.data.numpy())
            return act_probs, value.data.numpy()

    def policy_value_fn(self, state):
        """
        input: state
        output: a list of (action, probability) tuples for each available
        action and the score of the board state
        """
        legal_positions = state.get_all_available_moves()
        legal_position_ids = [self.MOVE_MAP[(x.pos[-2], x.pos[-1])] for x in legal_positions]
        vec_board, vec_state = state.to_vector()
        if self.use_gpu:
            log_act_probs, value = self.policy_value_net(
                    torch.from_numpy(vec_board).cuda().float(), 
                    torch.from_numpy(vec_state).cuda().float())
            act_probs = np.exp(log_act_probs.data.cpu().numpy().flatten())
        else:
            log_act_probs, value = self.policy_value_net(
                    torch.from_numpy(vec_board).float(),
                    torch.from_numpy(vec_state).float())
            act_probs = np.exp(log_act_probs.data.numpy().flatten())
        act_probs = zip(legal_positions, act_probs[legal_position_ids])
        value = value.data[0][0]
        return act_probs, value

    def train_step(self, state_batch, mcts_probs, winner_batch, lr):
        """perform a training step"""
        # wrap in Variable
        if self.use_gpu:
            state_batch = Variable(torch.FloatTensor(state_batch).cuda())
            mcts_probs = Variable(torch.FloatTensor(mcts_probs).cuda())
            winner_batch = Variable(torch.FloatTensor(winner_batch).cuda())
        else:
            state_batch = Variable(torch.FloatTensor(state_batch))
            mcts_probs = Variable(torch.FloatTensor(mcts_probs))
            winner_batch = Variable(torch.FloatTensor(winner_batch))

        # zero the parameter gradients
        self.optimizer.zero_grad()
        # set learning rate
        set_learning_rate(self.optimizer, lr)

        # forward
        log_act_probs, value = self.policy_value_net(state_batch)
        # define the loss = (z - v)^2 - pi^T * log(p) + c||theta||^2
        # Note: the L2 penalty is incorporated in optimizer
        value_loss = F.mse_loss(value.view(-1), winner_batch)
        policy_loss = -torch.mean(torch.sum(mcts_probs*log_act_probs, 1))
        loss = value_loss + policy_loss
        # backward and optimize
        loss.backward()
        self.optimizer.step()
        # calc policy entropy, for monitoring only
        entropy = -torch.mean(
                torch.sum(torch.exp(log_act_probs) * log_act_probs, 1)
                )
        return loss.data[0], entropy.data[0]
        #for pytorch version >= 0.5 please use the following line instead.
        #return loss.item(), entropy.item()

    def get_policy_param(self):
        net_params = self.policy_value_net.state_dict()
        return net_params

    def save_model(self, model_file):
        """ save model params to file """
        net_params = self.get_policy_param()  # get model params
        torch.save(net_params, model_file)
