# -*- coding: utf-8 -*-
"""
Monte Carlo Tree Search in AlphaGo Zero style, which uses a policy-value
network to guide the tree search and evaluate the leaf nodes

@author: Junxiao Song
"""

'''
    # The code is mainly contributed by Junxiao Song.
    # The github link is: https://github.com/junxiaosong/AlphaZero_Gomoku/blob/master/mcts_pure.py
    #
    # Code is modified by EndlessLethe for further use.
'''

from .env.env_utils import actions2vec
from .mcts_pure import TreeNode, MCTS, MCTSPlayer

import numpy as np
import copy


def softmax(x):
    probs = np.exp(x - np.max(x))
    probs /= np.sum(probs)
    return probs


class MCTS_AlphaZero(MCTS):
    """An implementation of the modified Monte Carlo Tree Search by AlphaZero."""

    def __init__(self, policy_value_fn, c_puct=5, n_playout=10000):
        super().__init__(policy_value_fn, c_puct, n_playout)

    def get_move(self, state, temp=1e-3):
        """Run all playouts sequentially and return the available actions and
        their corresponding probabilities.
        state: the current game state
        temp: temperature parameter in (0, 1] controls the level of exploration
        """
        for n in range(self._n_playout):
            state_copy = copy.deepcopy(state)
            self._playout(state_copy)

        # calc the move probabilities based on visit counts at the root node
        act_visits = [(act, node._n_visits)
                      for act, node in self._root._children.items()]
        acts, visits = zip(*act_visits)
        act_probs = softmax(1.0/temp * np.log(np.array(visits) + 1e-10))

        return acts, act_probs

class MCTSPlayer_AlphaZero(MCTSPlayer):
    """AI player based on modified MCTS by AlphaZero"""

    def __init__(self, policy_value_function,
                 c_puct=5, n_playout=2000, inference=False):
        self.mcts = MCTS_AlphaZero(policy_value_function, c_puct, n_playout)
        self.inference = inference


    def get_action(self, game, temp=1e-3):
        sensible_moves = game.get_all_available_moves()
        # the pi vector returned by MCTS as in the alphaGo Zero paper
        if len(sensible_moves) > 0:
            acts, probs = self.mcts.get_move(game, temp)
            move_probs = actions2vec(acts, probs)
            if not self.inference:
                # add Dirichlet Noise for exploration (needed for
                # self-play training)
                move = np.random.choice(
                    acts,
                    p=0.75*probs + 0.25*np.random.dirichlet(0.3*np.ones(len(probs)))
                )
                # update the root node and reuse the search tree
                self.mcts.update_with_move(move)
            else:
                # with the default temp=1e-3, it is almost equivalent
                # to choosing the move with the highest prob
                move = np.random.choice(acts, p=probs)
                # reset the root node
                self.mcts.update_with_move(-1)
#                location = board.move_to_location(move)
#                print("AI move: %d,%d\n" % (location[0], location[1]))
            # print(move_probs)
            return move, move_probs
    
        elif len(sensible_moves) == 1:
            return sensible_moves[0], 1
        else:
            print("WARNING: the board is full")
