'''
Author: Zeng Siwei
Date: 2021-09-18 17:09:16
LastEditors: Zeng Siwei
LastEditTime: 2021-09-19 00:04:54
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

if __name__ == "__main__":
    test_train()