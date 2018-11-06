import numpy as np
from mcts import MCTS


class Player:
    def set_player_ind(self, player_ind):
        self.player = player_ind

    def get_action(self, board, temp=1e-3, return_prob=False):
        pass


class MCTSPlayer(Player):
    """
    基于蒙特卡洛树的电脑玩家
    """

    def __init__(self, policy_value_function, c_puct=5, n_playout=300, is_selfplay=False):
        """
        :param policy_value_function: 论文里面的(p,v)=f(s)函数。接受一个board作为参数并返回一个（动作，概率）列表和在[-1, 1]范围的局面胜率的函数
        :param c_puct: 论文里面的c_puct。一个在范围(0, inf)的数字，控制探索等级。值越小越依赖于Q值，值越大越依赖于P值
        :param n_playout: 找MCTS叶子节点次数，即每次搜索次数
        :param is_selfplay: 是否是自己与自己对局
        """
        self.mcts = MCTS(policy_value_function, c_puct, n_playout)
        self._is_selfplay = is_selfplay

    def set_player_ind(self, p):
        self.player = p

    def reset_player(self):
        self.mcts.update_with_move(-1)

    def get_action(self, board, temp=1e-3, return_prob=False):
        move_probs = np.zeros(board.get_action_count())  # alphaGo Zero论文里面由MCTS返回的的pi数组
        if len(board.get_available_moves()) > 0:
            acts, probs = self.mcts.get_move_probs(board, temp)
            move_probs[list(acts)] = probs
            if self._is_selfplay:
                move = np.random.choice(acts, p=0.75*probs + 0.25*np.random.dirichlet(0.3*np.ones(len(probs))))  # 增加一个Dirichlet Noise来探索
                self.mcts.update_with_move(move)
            else:
                move = np.random.choice(acts, p=probs)  # 如果用默认值temp=1e-3，就相当于选择P值最高的动作
                self.mcts.update_with_move(-1)
            if return_prob:
                return move, move_probs
            else:
                return move
        else:
            print("WARNING: the board is full")

    def __str__(self):
        return "MCTS {}".format(self.player)
