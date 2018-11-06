import numpy as np
import copy


def softmax(x):
    probs = np.exp(x - np.max(x))
    probs /= np.sum(probs)
    return probs


class TreeNode:
    """
    蒙特卡洛树的一个节点，每个节点存了Q值，P值，N值
    """

    def __init__(self, parent, prior_p):
        self._parent = parent
        self._children = {}  # 键是动作值，值是节点
        self._n_visits = 0
        self._Q = 0
        self._P = prior_p

    def expand(self, action_priors):
        """
        展开一个叶子节点。
        :param action_priors: 一个元素为(action, P)的列表
        """
        for action, prob in action_priors:
            if action not in self._children:
                self._children[action] = TreeNode(self, prob)

    def select(self, c_puct):
        """
        选择所有子节点中Q+u(P)最大的返回。
        :param c_puct: 一个在范围(0, inf)的值，控制Q和P的比例
        :return: 二元组(action, next_node)
        """
        return max(self._children.items(), key=lambda act_node: act_node[1].get_value(c_puct))

    def update(self, leaf_value):
        """
        根据叶子节点的V值更新本节点的N值和Q值。
        :param leaf_value: 从当前玩家视角的子树评估值
        """
        self._n_visits += 1
        self._Q += (leaf_value - self._Q) / self._n_visits

    def update_recursive(self, leaf_value):
        """
        递归更新所有祖先节点的值。
        :param leaf_value: 从当前玩家视角的子树评估值
        """
        if self._parent:  # 优先更新父节点
            self._parent.update_recursive(-leaf_value)
        self.update(leaf_value)

    def get_value(self, c_puct):
        """
        得到该节点的Q+u(P)值
        :param c_puct: 一个在范围(0, inf)的值，控制Q和P的比例
        :return: 该节点的Q+u(P)值
        """
        u = c_puct * self._P * np.sqrt(self._parent._n_visits) / (1 + self._n_visits)
        return self._Q + u

    def is_leaf(self):
        """
        是否是叶子节点（是不是还没有被展开）。
        :return: 如果是叶子节点，返回True，否则返回False
        """
        return self._children == {}

    def is_root(self):
        """
        是否是根节点（是不是没有父节点）。
        :return: 如果是根节点，返回True，否则返回False
        """
        return self._parent is None


class MCTS:
    """
    蒙特卡洛树及其搜索方法。
    """

    def __init__(self, policy_value_fn, c_puct=5, n_playout=300):
        """
        :param policy_value_fn: 论文里面的(p,v)=f(s)函数。接受一个board作为参数并返回一个（动作，概率）列表和在[-1, 1]范围的局面胜率的函数
        :param c_puct: 论文里面的c_puct。一个在范围(0, inf)的数字，控制探索等级。值越小越依赖于Q值，值越大越依赖于P值
        :param n_playout: 找MCTS叶子节点次数，即每次搜索次数
        """
        self._root = TreeNode(None, 1.0)
        self._policy = policy_value_fn
        self._c_puct = c_puct
        self._n_playout = n_playout

    def _playout(self, state):
        """
        执行一次蒙特卡洛搜索，找到一个叶子节点，并更新路径上所有节点的值。
        :param state: 一个Board对象，在搜索过程中这个Board对象的状态会随之改变，所以这个参数传进来前需要复制一份。
        """
        node = self._root
        while not node.is_leaf():  # 找到一个叶子节点
            action, node = node.select(self._c_puct)
            state.do_move(action)

        action_probs, leaf_value = self._policy(state)  # 得到一个相对于当前玩家的(action, probability)列表和在范围[-1, 1]的V值

        end, winner = state.game_end()  # 检查游戏是否结束
        if not end:
            node.expand(action_probs)
        else:
            if winner == -1:  # 平局V值为0
                leaf_value = 0.0
            else:
                leaf_value = (1.0 if winner == state.get_current_player() else -1.0)  # 当前玩家赢了V值为1，输了V值为-1

        # 更新路径上所有节点的值
        node.update_recursive(-leaf_value)

    def get_move_probs(self, state, temp=1e-3):
        """
        执行蒙特卡洛搜索n_playout次，得到每个动作相应的概率pi值。
        :param state: 一个Board类的对象，描述了当前棋局
        :param temp: 在范围(0, 1]的温度值
        :return: 所有动作值和所有动作相应的所有概率pi值
        """
        for n in range(self._n_playout):
            state_copy = copy.deepcopy(state)
            self._playout(state_copy)

        # 计算每个动作的概率pi值
        act_visits = [(act, node._n_visits) for act, node in self._root._children.items()]
        acts, visits = zip(*act_visits)
        act_probs = softmax(1.0/temp * np.log(np.array(visits) + 1e-10))

        return acts, act_probs

    def update_with_move(self, last_move):
        """
        根据行动值更新树，继续使用子树。
        :param last_move: 上一次行动值
        """
        if last_move in self._root._children:
            self._root = self._root._children[last_move]
            self._root._parent = None
        else:
            self._root = TreeNode(None, 1.0)

    def __str__(self):
        return "MCTS"
