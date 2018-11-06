

class PolicyValueNet():

    def policy_value(self, state_batch):
        """
        :param state_batch: 一堆棋局
        :return: 一堆动作P值和局面V值
        """
        pass

    def policy_value_fn(self, board):
        """
        论文里面的神经网络函数(p,v)=f(s)。
        :param board: 棋局
        :return: (action, probability)列表和v值
        """
        pass

    def train_step(self, state_batch, mcts_probs, winner_batch, lr):
        """
        训练一下。
        :param state_batch: 输入给神经网络的数据
        :param mcts_probs: 动作概率标签
        :param winner_batch: 胜率标签
        :param lr: 学习速度
        :return: 损失函数值和熵值
        """
        pass

    def save_model(self, model_path):
        """
        保存模型。
        :param model_path: 模型保存路径
        """
        pass

    def restore_model(self, model_path):
        """
        载入模型。
        :param model_path: 模型载入路径
        """
        pass
