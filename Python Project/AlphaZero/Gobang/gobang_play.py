from play import Player, MCTSPlayer
from Gobang.gobang_game import GobangBoard, GobangGame
from Gobang.gobang_model import *


class Human(Player):
    """
    人类玩家
    """
    def __init__(self):
        self.player = None

    def set_player_ind(self, p):
        self.player = p

    def get_action(self, board, temp=1e-3, return_prob=False):
        try:
            location = input("Your move: ")
            if isinstance(location, str):  # python3
                location = [int(n, 10) for n in location.split(",")]
            move = board.location_to_move(location)
        except Exception as e:
            move = -1
        if move == -1 or move not in board.get_available_moves():
            print("invalid move")
            move = self.get_action(board)
        return move

    def __str__(self):
        return "Human {}".format(self.player)


def human_versus_ai():
    board = GobangBoard(width=10, n_in_row=5)
    game = GobangGame(board)
    policy_value_net = GobangPolicyValueNet2(board_width=10, model_file="model2_10_10_5/7950/policy_value_net.model")
    try:
        mcts_player = MCTSPlayer(policy_value_net.policy_value_fn)
        game.start_play(Human(), mcts_player, start_player=1, is_shown=True)
    except KeyboardInterrupt:
        print('\n\rquit')


def test_ai():
    board = GobangBoard(width=10, n_in_row=5)
    game = GobangGame(board)
    policy_value_net = GobangPolicyValueNet2(10, "model2_10_10_5/10000/policy_value_net.model")
    policy_value_net2 = GobangPretrainedPolicyValueNet(10, "model_10_10_5/15800/graph.bytes")
    test_player = MCTSPlayer(policy_value_net.policy_value_fn)
    opponent = MCTSPlayer(policy_value_net2.policy_value_fn)
    win, lose, tie = 0, 0, 0
    try:
        for i in range(100):
            winner = game.start_play(test_player, opponent, start_player=i % 2, is_shown=False, temp=1)
            if winner == -1:
                tie += 1
            elif winner == board.players[0]:
                win += 1
            else:
                lose += 1
            print("win={}, lose={}, tie={}, ratio={}".format(win, lose, tie, (win + tie / 2) / (win + lose + tie)))
    except KeyboardInterrupt:
        print('\n\rquit')
    print("final result: win={}, lose={}, tie={}, ratio={}".format(win, lose, tie, (win + tie / 2) / (win + lose + tie)))


if __name__ == '__main__':
    test_ai()
