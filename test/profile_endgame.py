'''
Author: Zeng Siwei
Date: 2021-10-19 19:24:17
LastEditors: Zeng Siwei
LastEditTime: 2021-10-19 20:51:11
Description: 
'''

from deepdraughts.endgame.generator import *

if __name__ == "__main__":
    import cProfile, pstats, io, datetime

    pr = cProfile.Profile()
    pr.enable()

    # profile function
    # generate_two_kings_versus_one_king()
    generate_two_versus_two()

    pr.disable()

    dir_file = "./savedata/"
    filename = "endgame_profile_2v2"
    now_time = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    filepath = dir_file + filename + "_" + now_time +".prof"
    pr.dump_stats(filepath)
    # to see visualization via pip: "flameprof selfplay.prof > selfplay.svg"
    # or invoke flameprof.py directly: "python flameprof.py selfplay.prof > profile.svg"
    # about: https://github.com/baverman/flameprof

    s = io.StringIO()
    sortby = "cumtime"  # 仅适用于 3.6, 3.7 把这里改成常量了
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    result = s.getvalue()
    print(result)

    filepath = dir_file + filename + "_" + now_time +".txt"
    # save it to disk
    with open(filepath, 'w') as f:
        f.write(result)