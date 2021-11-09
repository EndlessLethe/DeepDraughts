<!--
 * @Author: Zeng Siwei
 * @Date: 2021-09-12 00:27:58
 * @LastEditors: Zeng Siwei
 * @LastEditTime: 2021-11-09 20:28:26
 * @Description: 
-->
# DeepDraughts
## Main components
1. Draughts enviroment
2. AI train and play
3. Endgame database generator

### Component I: Draughts enviroment
Feature:
1. Play Draughts with friends on your computer or strong AI.
2. Carefully tested Rule.
   - Promotion, capture, king move and so on.
3. Runs Fast. 
   - Hard work on optimizing and runs quite fast. (one million move per second)
4. Support FEN format to load and save a game.
   - Describing a game will be much more easier as "W:WKG7:BH6,KD2." (A white king in G7, a black pawn in H6, a black king in D2)
5. Endgame database enabled.
   - Endgame database enhance AI's endgame plays, which means AI will never be wrong in endgames.
6. Easy to use this enviroment in other Python program.
   - File structure is well defined and just import the enviroment to build your own code with Python.

### Component II: AI

Feature:
1. Pure MCTS AI
2. Deep neural network AI (Alphazero AI)
3. Train pipline to train your own AI.
4. GUI (Graphical User Interface).

## Basic usage
### Installation
Via pip:
```
pip install deepdraughts
```

or via git:
```
git clone git@github.com:EndlessLethe/DeepDraughts.git
cd DeepDraughts/resources
# unzip endgame.zip for endgame database
cd ..
python setup.py build
python setup.py install
```

### Play with friends
To play with friends, just using following command:
```
cd DeepDraughts/run
python run.py
```

### Play with AI
To play with firends, 
1. just change the config.ini: set `play_with = human` instead of `play_with = puremcts`.
2. use commands above `python run.py` (make sure you're now in path `DeepDraughts/run`)

When you want to play with a stronger player, you can set `n_playout` larger.

Note:  
If using pure MCTS AI (a non-deeping AI method `play_with = puremcts`), by setting `n_playout = 10000` you will have a decent AI player, who're good at positioning piece and somehow weak at the end of a game. `n_playout = 1000` will bring you an unstable player whose choice may be confusing and bad rarely.


## Draughts enviroment
### Supported Rule
Draughts in 8x8 board has mainly two rule: [Russian](https://lidraughts.org/variant/russian) and [Brazilian Rule](https://draughts.github.io/brazilian-checkers.html). Because Russian Rule is used more in international competitions, our project only completes Russian Rule for now.

```
game = Game(rule = RUSSIAN_RULE)
```

The command below can create a game using Brazilian Rule, but following one is not supported.  
- In the situation where you have the choice between making multi-jumps over your opponent’s checkers, it is mandatory to choose the one that make you capture the maximum pieces.

```
game = Game(rule = BRAZILIAN_RULE)
```

### Usage
**Get available moves for current player**
```
moves = game.get_all_available_moves()
```

**Do move**
```
game_status = game.do_move(move)
```
Game status includes `GAME_CONTINUE`, `GAME_WHITE_WIN`, `GAME_BLACK_WIN`, `GAME_DRAW`  
The following method can help read game status: `game_is_over`, `game_is_drawn`, `game_winner`, `game_status_to_str`

**Load and save game with FEN format**
```
fen_str = "W:WKG7:BH6,KD2."
game = Game.load_fen(fen_str)
fen_str = game.to_fen()
```

## AI train and play
The following part is for programmers who's interested in creating an own AI.

### How to build you own AI player for game you like.
1. Make sure the game you like has no uncertainty and has two player involved.
    - Or it will be hard to take MCTS method into practice.
2. Design your own game env like "deepdraughts/env"
    - Playing a hundred times is recommended for fixing hidden bugs.
3. Add pure MCTS as a basic AI
4. Add AlphaZero-style AI
    - Implement AlphaZero-style AI (AlphaZero MCTS and untrained NN).
    - Running GUI to test.
    - Implement self-play and data collector with AlphaZero MCTS.
    - Training NN with self-play.
    - Make self-play paralleled.

### Implementation Details About Rule
I divide the rule into two parts: state-dependent rules, and state-independent rules.  

For state-dependent rules, they are implemented in class Board get_available_moves(pos). Board object only knows where's pieces and their states. This method will return all available moves following the rule for one given piece.

For state-independent rules as chain-taking and finishing the continuous capture, they are implemented in class Game get_available_moves(pos).

### Implementation Details About Paralleling
Though paralleling is an effective method to decrease running time in total, it's quite complicated when paralleling meets GPU training.  

I only use paralleling for self playing. It's sequential when training network and self play, so that NN args won't be read and write at the same time. In fact, self-play function is the most costly part.

## Endgame database genarator
Endgame database is generated by following `retrograde analysis` algorithm [retrograde analysis](http://www.fierz.ch/strategy3.htm):
1. Initialization: Generate two arrays of length N for the position values (WIN/LOSS/DRAW) and the DTC. Set all position values to UNKNOWN. Set all DTC counters to zero. As you can see, you need 4 distinct values for the position values, the array needs a data type with 4 possible values (2 bits). That doesn't exist of course, so you need to handle that yourself.
2. Mate pass: For all positions, check whether it's a mate - if yes, set the value of that position to a LOSS - the side to move has lost. If the game allows for stalemate, check that too and set the values to DRAW. Increment the DTC counter for all positions with value UNKNOWN.
3. For every position with value UNKNOWN, generate all successor positions and look at their values. If any of the successors has value LOSS, set the current position to WIN. If all successors have the value WIN, set the value to LOSS. If you pass through all positions without being able to set any value to WIN or LOSS, skip to step 5.
3. Increment the DTC counter for all positions with value UNKNOWN and go back to step 3.
4. Change the value to DRAW for all positions with value UNKNOWN. The algorithm has terminated.

### Generation speed
- one piece: 120 endgames within 1s.
- two piece: 10580 endgames within 10s.
- three piece: 470180 endgames within 256s.
- four piece: 13998502 endgames within 10119s.
- five piece: Nan.

### Tries on Paralleling
Due to the exponential growth of generation time (more than 32x when one more piece), I spent near one week on multiprocessing to speed up, and finally failed. Why I failed to make generator work in parallel is because some data must be shared cross processes and lock (even though reader writer lock) operation is so heavy. It's get slower when paralleling is enabled.