import numpy as np
from train import Trainer
from Connect4.connect4_game import *
from Connect4.connect4_model import *


class Connect4Trainer(Trainer):

    def get_equi_data(self, play_data):
        extend_data = []
        for state, mcts_prob, winner in play_data:
            extend_data.append((state, mcts_prob, winner))
            # 水平翻转
            equi_state = [np.fliplr(s) for s in state]
            mcts_prob = list(mcts_prob)
            last_half_mcts_prob = mcts_prob[len(mcts_prob) // 2:][::-1]
            equi_mcts_prob = mcts_prob[:len(mcts_prob) // 2][::-1]
            equi_mcts_prob.extend(last_half_mcts_prob)
            extend_data.append((equi_state, equi_mcts_prob, winner))
        return extend_data


if __name__ == "__main__":
    game = Connect4Game(Connect4Board())
    policy_value_net = Connect4PolicyValueNet()
    trainer = Connect4Trainer(game=game, policy_value_net=policy_value_net, save_dir="model")
    trainer.run()
