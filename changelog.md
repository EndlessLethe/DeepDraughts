<!--
 * @Author: Zeng Siwei
 * @Date: 2021-10-11 15:34:11
 * @LastEditors: Zeng Siwei
 * @LastEditTime: 2021-10-14 00:26:27
 * @Description: 
-->

# Change Log
## v1.1 (2021/10/11)
### About v1.1
Happy to see selfplay process using pure MCTS is 4x faster by refactoring game functions in `pyenv`.

As Figure2 below shows, forwarding costs most of time when selfplay, which means the way 
to speed up selfplay process is to aviod double computing for the same state.

<center>Figure1 selfplay time for pure mcts</center>

![image](./savedata/selfplay_profile_1_1_20211010_0045.svg)

<center>Figure2 selfplay time for alphazero</center>

![image](./savedata/selfplay_profile_1_1_20211010_1226.svg)

**Todo List**
1. [pyenv] support FEN format 
2. [pyenv] introduce endgame database to decrease the length of game especally when game is drawn.
3. [selfplay] utilize temporal locality when MCTS plays out many times under a given state (to aviod double computing for possible follow-up states).
4. [cython_env] keep `cython_env` in sync with `pyenv`.
5. [cython_env] using c++ standard library to replace python `list` and `dict`

### Details
- [pyenv] fix chain-taking bug when chain is long.
- [pyenv] refactor game functions which are performance bottlenecks and selfplay using pure mcts is 4x faster.
- [pyenv] refactor MCTS_alphazero leaf_value type and MCTS_alphazero is 1.2x faster.
- [selfplay] fix multiprocessing OSError([Errno 24] Too many open files).
- [train] fix same random seed in multuiprocessing.

## v1.0 (2012/09/24)
### About v1.0
Cython enviroment is added into this project as an optional game enviroment , thought it's not effective as expected. Default env is still `pyenv`.

**Todo List**
1. [test] profile selfplay process and deal with performance bottlenecks. 
2. [cython_env] using c++ standard library to replace python list and dict.

### Details
- [cython_env] add cython version as an optional game enviroment.
- [run] add config, which makes setting args easier.

## v0.1 (2021/09/19)
### About v0.1
Now users of DeepDaughts can play draughts with GUI.
And AI players based on pure MCTS and AlphaZero is ready to be your opponent.

Training your own deep neural network model is also supported.

### Details
- [pyenv] add draughts game env.
- [run] add GUI for playing with human and AI.
- [selfplay] add parallel self play.
- [train] add code for training neural network model.

## start point (2021/09/12)
- First commit.
