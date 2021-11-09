<!--
 * @Author: Zeng Siwei
 * @Date: 2021-10-11 15:34:11
 * @LastEditors: Zeng Siwei
 * @LastEditTime: 2021-11-09 20:20:28
 * @Description: 
-->

# Change Log
## v1.2 (2021/11/09)
Suprise! Endgame database is generated and applied in draughts enviroment, which enhance AI's endgame plays.
Thanks to endgame database, the length of a game and runtime decreases a few.

The project comes to the end of a stage, and is released in [pypi](https://pypi.org/project/deepdraughts/).

Next step is to use fully trained DNN AI and build tools for game analysis. Let's wait for the AI getting fully trained with more thousands of games.

### Details
-  [pyenv] support FEN format.
-  [pyenv] use endgame database for better AI performance.
-  [test] fully check the whole project.

**Todo List**
1. [cython_env] keep `cython_env` in sync with `pyenv`.
2. [cython_env] using c++ standard library to replace python `list` and `dict`
3. [selfplay] enable gpu multiprocessing.
4. [selfplay] utilize temporal locality when MCTS plays out many times under a given state (to aviod double computing for possible follow-up states).

## v1.1 (2021/10/11)
### About v1.1
Happy to see selfplay process using pure MCTS is 4x faster by refactoring game functions in `pyenv`.

As Figure2 below shows, forwarding costs most of time when selfplay, which means the way 
to speed up selfplay process is to aviod double computing for the same state.

<center>Figure1 selfplay time for pure mcts</center>

![image](./resources/selfplay_profile_pureMCTS.svg)

<center>Figure2 selfplay time for alphazero</center>

![image](./resources/selfplay_profile_AlphaZero.svg)

### Details
- [pyenv] fix chain-taking bug when chain is long.
- [pyenv] refactor game functions which are performance bottlenecks and selfplay using pure mcts is 4x faster.
- [pyenv] refactor MCTS_alphazero leaf_value type and MCTS_alphazero is 1.2x faster.
- [selfplay] fix multiprocessing OSError([Errno 24] Too many open files).
- [train] fix same random seed in multuiprocessing.

**Todo List**
1. [pyenv] support FEN format 
2. [pyenv] introduce endgame database to decrease the length of game especally when game is drawn.
3. [selfplay] utilize temporal locality when MCTS plays out many times under a given state (to aviod double computing for possible follow-up states).
4. [cython_env] keep `cython_env` in sync with `pyenv`.
5. [cython_env] using c++ standard library to replace python `list` and `dict`

## v1.0 (2012/09/24)
### About v1.0
Cython enviroment is added into this project as an optional game enviroment , thought it's not effective as expected. Default env is still `pyenv`.

### Details
- [cython_env] add cython version as an optional game enviroment.
- [run] add config, which makes setting args easier.

**Todo List**
1. [test] profile selfplay process and deal with performance bottlenecks. 
2. [cython_env] using c++ standard library to replace python list and dict.


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
