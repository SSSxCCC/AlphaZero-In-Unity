import numpy as np
from train import Trainer
from Gobang.gobang_game import GobangBoard, GobangGame
from Gobang.gobang_model import *


class GobangTrainer(Trainer):

    def get_equi_data(self, play_data):
        extend_data = []
        for state, mcts_porb, winner in play_data:
            for i in [1, 2, 3, 4]:
                # 逆时针旋转
                equi_state = np.array([np.rot90(s, i) for s in state])
                equi_mcts_prob = np.rot90(np.flipud(mcts_porb.reshape(self.game.board.width, self.game.board.width)), i)
                extend_data.append((equi_state, np.flipud(equi_mcts_prob).flatten(), winner))
                # 水平翻转
                equi_state = np.array([np.fliplr(s) for s in equi_state])
                equi_mcts_prob = np.fliplr(equi_mcts_prob)
                extend_data.append((equi_state, np.flipud(equi_mcts_prob).flatten(), winner))
        return extend_data


if __name__ == "__main__":
    game = GobangGame(GobangBoard(width=3, n_in_row=3))
    #policy_value_net = GobangPolicyValueNet2(board_width=8, model_file=None)
    policy_value_net = TictactoePolicyValueNet()
    trainer = GobangTrainer(game=game, policy_value_net=policy_value_net, save_dir="model_3_3_3")
    trainer.run()
