'''
Author: Zeng Siwei
Date: 2021-09-18 17:09:16
LastEditors: Zeng Siwei
LastEditTime: 2021-09-21 01:03:44
Description: 
'''


from deepdraughts.train_pipline import TrainPipeline
from deepdraughts.net_pytorch import Model
from deepdraughts.env.env_utils import *

def test_train():
    checkpoint_dir = "deepdraughts/savedata/"
    model = Model(N_SIZE_8, N_STATE_64, N_ACTION_64, MOVE_MAP_64, name = "test_train")
    training_pipeline = TrainPipeline(model, checkpoint_dir)
    training_pipeline.run()

def test_policy_evaluate():
    checkpoint_dir = "deepdraughts/savedata/"
    model = Model(N_SIZE_8, N_STATE_64, N_ACTION_64, MOVE_MAP_64, name = "test_policy")
    training_pipeline = TrainPipeline(model, checkpoint_dir)
    training_pipeline.policy_evaluate()

def test_run():
    checkpoint_dir = "deepdraughts/savedata/"
    model = Model(N_SIZE_8, N_STATE_64, N_ACTION_64, MOVE_MAP_64, name = "test_run")
    training_pipeline = TrainPipeline(model, checkpoint_dir)
    training_pipeline.run()

if __name__ == "__main__":
    # test_train()
    # test_policy_evaluate()
    test_run()