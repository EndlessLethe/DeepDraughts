<!--
 * @Author: Zeng Siwei
 * @Date: 2021-09-12 00:27:58
 * @LastEditors: Zeng Siwei
 * @LastEditTime: 2021-09-14 23:41:35
 * @Description: 
-->
# DeepDraughts


## Play with friends
To play with firends, just using following command:
```
python run.py
```

## Play with AI
To play with firends, just using following command:
```
python run.py --player pure_mcts
```

If using pure MCTS AI (a non-deeping AI method), by setting `n_playout = 10000` you will have a decent AI player, 
who're good at positioning piece and somehow weak at the end of a game. `n_playout = 1000` will bring you an 
unstable player whose choice may be confusing and bad rarely.

When you want to play with a stronger player, you can use following command:
```
python run.py --player alphazero
```



## Supported Rule
Draughts in 8x8 board has mainly two rule: [Russian](https://lidraughts.org/variant/russian) and [Brazilian Rule](https://draughts.github.io/brazilian-checkers.html). Because Russian Rule is used more in international competitions, our project only completes Russian Rule for now.

```
game = Game(rule = RUSSIAN_RULE)
```

The command below can create a game using Brazilian Rule, but following one is not supported.  
- In the situation where you have the choice between making multi-jumps over your opponent’s checkers, it is mandatory to choose the one that make you capture the maximum pieces.

```
game = Game(rule = BRAZILIAN_RULE)
```

## Implementation Detail About Rule
I divide the rule into two parts: state-dependent rules, and state-independent rules.  

For state-dependent rules, they are implemented in class Board get_available_moves(pos). Board object only knows where's pieces and their states. This method will return all available moves following the rule for one given piece.

For state-independent rules as chain-taking and finishing the continuous capture, they are implemented in class Game get_available_moves(pos).
