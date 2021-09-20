# -*- coding: utf-8 -*-
"""
An implementation of the policyValueNet in PyTorch
Tested in PyTorch 0.2.0 and 0.3.0

@author: Junxiao Song
"""


'''
    # The code is mainly contributed by Junxiao Song.
    # The github link is: https://github.com/junxiaosong/AlphaZero_Gomoku/blob/master/mcts_pure.py
    #
    # Code is modified by EndlessLethe for further use.
'''

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.autograd import Variable
import numpy as np
import os

def set_learning_rate(optimizer, lr):
    """Sets the learning rate to the given value"""
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr


def _initialize_weights(self):
    for m in self.modules():
        if isinstance(m, nn.Linear):
            weight = (param.data for name, param in m.named_parameters() if "weight" in name)
            for w in weight:
                torch.nn.init.xavier_uniform_(m.weight)

        if isinstance(m, torch.nn.LSTM):
            ih = (param.data for name, param in self.named_parameters() if 'weight_ih' in name)
            hh = (param.data for name, param in self.named_parameters() if 'weight_hh' in name)
            for w in ih:
                nn.init.xavier_uniform(w)
            for w in hh:
                nn.init.orthogonal(w)

        if isinstance(m, torch.nn.Conv2d):
            weight = (param.data for name, param in m.named_parameters() if "weight" in name)
            for w in weight:
                torch.nn.init.xavier_uniform_(m.weight)

        # b = (param.data for name, param in self.named_parameters() if 'bias' in name)
        # for w in b:
        #     nn.init.constant(w, 0)

    print(self.__class__.__name__ + ":\n" + str(list(self.modules())[0]))


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

        _initialize_weights(self)

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
    def __init__(self, nsize, n_states, n_actions, MOVE_MAP, name = "default", 
                use_gpu = False, l2_const = 1e-4):
        self.nsize = nsize
        self.n_states = n_states
        self.n_actions = n_actions
        self.board_width = nsize
        self.board_height = nsize
        self.MOVE_MAP = MOVE_MAP

        self.name = name
        self.checkpoint_n_epoch = None
        self.use_gpu = use_gpu
        self.l2_const = l2_const

        self.policy_value_net = PolicyValueNet(nsize, n_states, n_actions)
        if self.use_gpu:
            self.policy_value_net = self.policy_value_net.cuda()

        self.optimizer = optim.Adam(self.policy_value_net.parameters(),
                                    weight_decay=self.l2_const)


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

    def policy_value_batch(self, state_batch):
        """
        input: a batch of states
        output: a batch of action probabilities and state values
        """
        vec_board_batch, vec_state_batch = state_batch
        vec_board_batch = torch.from_numpy(vec_board_batch).float()
        vec_state_batch = torch.from_numpy(vec_state_batch).float()

        if self.use_gpu:
            vec_board_batch = vec_board_batch.cuda()
            vec_state_batch = vec_state_batch.cuda()
            log_act_probs, value = self.policy_value_net(vec_board_batch, vec_state_batch)
            act_probs = np.exp(log_act_probs.data.cpu().numpy())
            return act_probs, value.data.cpu().numpy()
        else:
            log_act_probs, value = self.policy_value_net(vec_board_batch, vec_state_batch)
            act_probs = np.exp(log_act_probs.data.numpy())
            return act_probs, value.data.numpy()


    def train_step(self, state_batch, mcts_probs_batch, policy_grad_batch, lr):
        """perform a training step"""
        vec_board_batch, vec_state_batch = state_batch
        vec_board_batch = torch.from_numpy(vec_board_batch).float()
        vec_state_batch = torch.from_numpy(vec_state_batch).float()
        mcts_probs_batch = torch.from_numpy(mcts_probs_batch).float()
        policy_grad_batch = torch.from_numpy(policy_grad_batch).float()

        if self.use_gpu:
            vec_board_batch = vec_board_batch.cuda()
            vec_state_batch = vec_state_batch.cuda()
            mcts_probs_batch = mcts_probs_batch.cuda()
            policy_grad_batch = policy_grad_batch.cuda()
            
        # zero the parameter gradients
        self.optimizer.zero_grad()
        # set learning rate
        set_learning_rate(self.optimizer, lr)

        # forward
        log_act_probs, value = self.policy_value_net(vec_board_batch, vec_state_batch)

        # define the loss = (z - v)^2 - pi^T * log(p) + c||theta||^2
        # Note: the L2 penalty is incorporated in optimizer
        value_loss = F.mse_loss(value.view(-1), policy_grad_batch)
        policy_loss = -torch.mean(torch.sum(mcts_probs_batch*log_act_probs, 1))
        loss = value_loss + policy_loss
        # backward and optimize
        loss.backward()
        self.optimizer.step()
        # calc policy entropy, for monitoring only
        entropy = -torch.mean(
                torch.sum(torch.exp(log_act_probs) * log_act_probs, 1)
                )
        return loss.item(), entropy.item()

    def save(self, checkpoint_dir, epoch, is_best=False):
        """ save model params to file """
        if is_best:
            savepath = os.path.join(checkpoint_dir, self.name+'_{}_best.pth.tar'.format(epoch))
        else:
            savepath = os.path.join(checkpoint_dir, self.name+'_{}.pth.tar'.format(epoch))
        torch.save({
                    'nsize': self.nsize,
                    'n_states': self.n_states, 
                    'n_actions': self.n_actions, 
                    'MOVE_MAP': self.MOVE_MAP, 
                    'name': self.name, 
                    'n_epoch': epoch, 
                    'use_gpu': self.use_gpu, 
                    'l2_const': self.l2_const, 

                    'model': self.policy_value_net.state_dict(),
                    'optimizer': self.optimizer.state_dict(),
                    },
                    savepath)

    @classmethod
    def load_checkpoint(self, model_file):
        model_params = torch.load(model_file)

        nsize = model_params['nsize']
        n_states = model_params['n_states']
        n_actions = model_params['n_actions']
        MOVE_MAP = model_params['MOVE_MAP']

        name = model_params['name']
        checkpoint_n_epoch = model_params['n_epoch']
        use_gpu = model_params['use_gpu']
        l2_const = model_params['l2_const']

        model = Model(nsize, n_states, n_actions, MOVE_MAP, name, use_gpu, l2_const)
        model.checkpoint_n_epoch = checkpoint_n_epoch
        model.policy_value_net.load_state_dict(model_params['model'])
        model.optimizer.load_state_dict(model_params['optimizer'])
        return model
        

