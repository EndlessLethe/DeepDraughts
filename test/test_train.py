'''
Author: Zeng Siwei
Date: 2021-09-18 17:09:16
LastEditors: Zeng Siwei
LastEditTime: 2021-09-24 15:25:19
Description: 
'''


from deepdraughts.train_pipline import TrainPipeline
from deepdraughts.net_pytorch import Model
from deepdraughts.env import *

def test_train():
    checkpoint_dir = "./savedata/"
    env_args = get_env_args()
    model = Model(env_args, name = "test_train")
    training_pipeline = TrainPipeline(model, checkpoint_dir)
    training_pipeline.run()

def test_run():
    checkpoint_dir = "./savedata/"
    env_args = get_env_args()
    model = Model(env_args, name = "test_run")
    training_pipeline = TrainPipeline(model, checkpoint_dir)
    training_pipeline.run()

if __name__ == "__main__":
    # test_train()
    # test_policy_evaluate()
    test_run()