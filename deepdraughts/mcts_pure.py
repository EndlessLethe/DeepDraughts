# -*- coding: utf-8 -*-
"""
A pure implementation of the Monte Carlo Tree Search (MCTS)

@author: Junxiao Song
"""

'''
    # The code is mainly contributed by Junxiao Song.
    # The github link is: https://github.com/junxiaosong/AlphaZero_Gomoku/blob/master/mcts_pure.py
    #
    # Code is modified by EndlessLethe for further use.
'''

'''
    For readers who want to use pure MCTS in their own project, 

    To reuse this code about pure mcts, following apis are required:
1. Class Game / Board to store current game state
2. methed to get availabel moves "get_all_available_moves()"
3. methed to make a move "do_move()"
4. methed to check game state "is_over()"

    Code needs modifying:
1. policy_fn
2. MCTS Class code blocks with listed metheds above

'''

import numpy as np
import copy
from operator import itemgetter

def rollout_policy_fn(game):
    """a coarse, fast version of policy_fn used in the rollout phase."""
    # rollout randomly
    availables = game.get_all_available_moves()
    action_probs = np.random.rand(len(availables))
    return zip(availables, action_probs)


def policy_value_fn(game):
    """a function that takes in a state and outputs a list of (action, probability)
    tuples and a score for the state"""
    # return uniform probabilities and 0 score for pure MCTS
    availables = game.get_all_available_moves()
    action_probs = np.ones(len(availables))/len(availables)
    return zip(availables, action_probs), 0


class TreeNode(object):
    """A node in the MCTS tree. Each node keeps track of its own value Q,
    prior probability P, and its visit-count-adjusted prior score u.
    """

    def __init__(self, parent, prior_p):
        self._parent = parent
        self._children = {}  # a map from action to TreeNode
        self._n_visits = 0
        self._Q = 0
        self._u = 0
        self._P = prior_p

    def expand(self, action_priors):
        """Expand tree by creating new children.
        action_priors: a list of tuples of actions and their prior probability
            according to the policy function.
        """
        for action, prob in action_priors:
            if action not in self._children:
                self._children[action] = TreeNode(self, prob)

    def select(self, c_puct):
        """Select action among children that gives maximum action value Q
        plus bonus u(P).
        Return: A tuple of (action, next_node)
        """
        return max(self._children.items(),
                   key=lambda act_node: act_node[1].get_value(c_puct))

    def update(self, leaf_value):
        """Update node values from leaf evaluation.
        leaf_value: the value of subtree evaluation from the current player's
            perspective.
        """
        # Count visit.
        self._n_visits += 1
        # Update Q, a running average of values for all visits.
        self._Q += 1.0*(leaf_value - self._Q) / self._n_visits

    def get_value(self, c_puct):
        """Calculate and return the value for this node.
        It is a combination of leaf evaluations Q, and this node's prior
        adjusted for its visit count, u.
        c_puct: a number in (0, inf) controlling the relative impact of
            value Q, and prior probability P, on this node's score.
        """
        self._u = (c_puct * self._P *
                   np.sqrt(self._parent._n_visits) / (1 + self._n_visits))
        return self._Q + self._u

    def is_leaf(self):
        """Check if leaf node (i.e. no nodes below this have been expanded).
        """
        return self._children == {}

    def is_root(self):
        return self._parent is None


class MCTS(object):
    """A simple implementation of Monte Carlo Tree Search."""

    def __init__(self, policy_value_fn, c_puct=5, n_playout=10000):
        """
        policy_value_fn: a function that takes in a board state and outputs
            a list of (action, probability) tuples and also a score in [-1, 1]
            (i.e. the expected value of the end game score from the current
            player's perspective) for the current player.
        c_puct: a number in (0, inf) that controls how quickly exploration
            converges to the maximum-value policy. A higher value means
            relying on the prior more.
        """
        self._root = TreeNode(None, 1.0)
        self._policy = policy_value_fn
        self._c_puct = c_puct
        self._n_playout = n_playout

    def _playout(self, state):
        """Run a single playout from the root to the leaf, getting a value at
        the leaf and propagating it back through its parents.
        State is modified in-place, so a copy must be provided.
        """
        node = self._root
        list_node = [node]
        list_player = [state.current_player]
        while True:
            if node.is_leaf():
                break

            # Greedily select next move.
            action, node = node.select(self._c_puct)
            state.do_move(action)
            list_node.append(node)
            list_player.append(state.current_player)

        action_probs, _ = self._policy(state)
        # Check for end of game
        is_over, _ = state.is_over()
        if not is_over:
            node.expand(action_probs)
        # Evaluate the leaf node by random rollout
        current_player = state.current_player
        leaf_value = self._evaluate_rollout(state)
        
        # Update value and visit count of nodes in this traversal.
        # Applied recursively for all ancestors
        # Note: 
        # 1. node.update() is an indepentent operation. So the order is unneccesary.
        # 2. Why update -leaf_value? Easily to check by playing a game. Or see: https://github.com/junxiaosong/AlphaZero_Gomoku/issues/25

        for node, player in zip(list_node, list_player):
            node.update(-leaf_value if player == current_player else leaf_value)

    def _evaluate_rollout(self, state, limit=1000):
        """Use the rollout policy to play until the end of the game,
        returning +1 if the current player wins, -1 if the opponent wins,
        and 0 if it is a tie.

        Returns:
            value: Value of current state.
        """
        start_player = state.current_player
        value = None
        for i in range(limit):
            is_over, winner = state.is_over()
            if is_over: 
                if winner == None:
                    value = 0
                else:
                    value = 1 if winner == start_player else -1
                break
            action_probs = rollout_policy_fn(state)
            max_action = max(action_probs, key=itemgetter(1))[0]
            state.do_move(max_action)
        if value is None:
            # If no break from the loop, issue a warning.
            print("WARNING: rollout reached move limit")
            value = 0
        return value

     # It's impossible for python to parallel here. Theading is not real multi-theading for python!
    def get_move(self, state):
        """Runs all playouts sequentially and returns the most visited action.
        state: the current game state

        Return: the selected action
        """
        for n in range(self._n_playout):
            state_copy = copy.deepcopy(state)
            self._playout(state_copy)
        return max(self._root._children.items(),
                   key=lambda act_node: act_node[1]._n_visits)[0]

    def update_with_move(self, last_move):
        """Step forward in the tree, keeping everything we already know
        about the subtree.
        """
        if last_move in self._root._children:
            self._root = self._root._children[last_move]
            self._root._parent = None
        else:
            self._root = TreeNode(None, 1.0)

    def __str__(self):
        return "MCTS"


class MCTSPlayer(object):
    """AI player based on MCTS"""
    def __init__(self, c_puct=5, n_playout=2000):
        self.mcts = MCTS(policy_value_fn, c_puct, n_playout)

    def reset(self):
        self.mcts.update_with_move(-1)

    def get_action(self, game, temp=None):
        '''
        Args: 
            game: Current game states.

        Returns: 
            move: Move selected by AI player.
            prob: Action prob to be selected.
		
        '''        
        sensible_moves = game.get_all_available_moves()
        if len(sensible_moves) >= 2:
            move = self.mcts.get_move(game)
            self.mcts.update_with_move(-1)
            return move, 1
        elif len(sensible_moves) == 1:
            return sensible_moves[0], 1
        else:
            print("WARNING: the game is full")

    def __str__(self):
        return "MCTS {}".format(self.player)
