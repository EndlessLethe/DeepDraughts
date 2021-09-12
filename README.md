<!--
 * @Author: Zeng Siwei
 * @Date: 2021-09-12 00:27:58
 * @LastEditors: Zeng Siwei
 * @LastEditTime: 2021-09-12 22:31:00
 * @Description: 
-->
# DeepDraughts


## Play with friends
To play with firends, just using following command:
```
python gui.py
```



## Supported Rule
Draughts in 8x8 board has mainly two rule: Russian and [Brazilian Rule](https://draughts.github.io/brazilian-checkers.html). Because Russian Rule is used more in international competitions, our project only completes Russian Rule for now.

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
