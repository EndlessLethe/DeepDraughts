'''
Author: Zeng Siwei
Date: 2021-09-18 17:09:16
LastEditors: Zeng Siwei
LastEditTime: 2021-10-25 19:52:01
Description: 
'''

import configparser
from deepdraughts.train_pipline import TrainPipeline
from deepdraughts.net_pytorch import Model
from deepdraughts.env import *


def test_run(config):
    save_dir = "./savedata/"

    checkpoint = None
    name = "test_run"
    use_gpu = config.getboolean("model_args", "use_gpu")
    l2_const = config.getfloat("model_args", "l2_const")

    if not checkpoint:
        env_args = get_env_args()
        model = Model(env_args, name = name, use_gpu = use_gpu, l2_const = l2_const)
    else:
        model = Model.load(checkpoint)

    training_pipeline = TrainPipeline(model, save_dir, config)
    training_pipeline.run()

if __name__ == "__main__":
    conf_ini = "./config.ini"
    config = configparser.ConfigParser()
    config.read(conf_ini, encoding="utf-8")
    
    import multiprocessing
    manager = multiprocessing.Manager()
    init_endgame_database(manager)
    
    test_run(config)