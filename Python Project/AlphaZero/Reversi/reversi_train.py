import numpy as np
from train import Trainer
from Reversi.reversi_game import ReversiBoard, ReversiGame
from Reversi.reversi_model import *


class ReversiTrainer(Trainer):

    def get_equi_data(self, play_data):
        extend_data = []
        for state, mcts_porb, winner in play_data:
            for i in [1, 2, 3, 4]:
                # 逆时针旋转
                equi_state = np.array([np.rot90(s, i) for s in state])
                pass_prob = mcts_porb[-1]
                equi_mcts_prob = mcts_porb[0:len(mcts_porb)-1]
                equi_mcts_prob = np.rot90(np.flipud(equi_mcts_prob.reshape(self.game.board.width, self.game.board.width)), i)
                flatten_mcts_prob = list(np.flipud(equi_mcts_prob).flatten())
                flatten_mcts_prob.append(pass_prob)
                extend_data.append((equi_state, flatten_mcts_prob, winner))
                # 水平翻转
                equi_state = np.array([np.fliplr(s) for s in equi_state])
                equi_mcts_prob = np.fliplr(equi_mcts_prob)
                flatten_mcts_prob = list(np.flipud(equi_mcts_prob).flatten())
                flatten_mcts_prob.append(pass_prob)
                extend_data.append((equi_state, flatten_mcts_prob, winner))
        return extend_data


if __name__ == "__main__":
    game = ReversiGame(ReversiBoard(width=6))
    #policy_value_net = GobangPolicyValueNet2(board_width=8, model_file=None)
    policy_value_net = ReversiPolicyValueNet(board_width=6)
    trainer = ReversiTrainer(game=game, policy_value_net=policy_value_net, save_dir="model_6")
    trainer.run()
