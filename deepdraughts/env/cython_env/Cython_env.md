<!--
 * @Author: Zeng Siwei
 * @Date: 2021-09-22 17:18:59
 * @LastEditors: Zeng Siwei
 * @LastEditTime: 2021-09-22 17:50:05
 * @Description: 
-->


# About using Cython
It's difficult for Cython to declear every var due to python writing style.  
I guess Cython is not effective for date type list or dict, beause Cython don't know what's in contrainers.  

# Code blocks
I convert all code blocks in `/env` except `env_utils` into Cython. The reason why I don't convert others is that Cython doesn't support Class inherit and there's no improvement while doing so.

# Result
With jupyter notebook "/test/test_cython.ipynb", it's only 30% faster which is way far from my target (2x fast by converting python into cpp).

With py file "/run/run.py", there's no signal that Cython is faster.

So recently (2021-09-22) I won't pay more attention on Cython. Rewriting in C++ seems more worthy, though there's much more things to be considered when sending neural network models between C++ and python .

# Further work
1. using c++ standard library to replace python list and dict
2. analyze why there's no improvement using Cython. (Maybe too many calls between C++ and Python?)
2. convert env_utils into Cython
3. convert all code including pytorch into Cython