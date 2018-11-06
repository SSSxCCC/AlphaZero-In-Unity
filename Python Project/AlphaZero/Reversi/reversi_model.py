import numpy as np
import tensorflow as tf
from model import PolicyValueNet


class ReversiPolicyValueNet(PolicyValueNet):
    def __init__(self, board_width=8, model_file=None):
        self.board_width = board_width

        # 定义网络结构
        # 1. 输入
        self.input_states = tf.placeholder(tf.float32, shape=[None, 3, board_width, board_width], name="input_states")
        self.input_state = tf.transpose(self.input_states, [0, 2, 3, 1], name="input_state")
        # 2. 卷积层
        self.conv1 = tf.layers.conv2d(inputs=self.input_state, filters=32, kernel_size=[3, 3], padding="same",
                                      data_format="channels_last", activation=tf.nn.relu, name="conv1")
        self.conv2 = tf.layers.conv2d(inputs=self.conv1, filters=64, kernel_size=[3, 3], padding="same",
                                      data_format="channels_last", activation=tf.nn.relu, name="conv2")
        self.conv3 = tf.layers.conv2d(inputs=self.conv2, filters=128, kernel_size=[3, 3], padding="same",
                                      data_format="channels_last", activation=tf.nn.relu, name="conv3")
        # 3. P数组输出
        self.action_conv = tf.layers.conv2d(inputs=self.conv3, filters=4, kernel_size=[1, 1], padding="same",
                                            data_format="channels_last", activation=tf.nn.relu, name="action_conv")
        self.action_conv_flat = tf.reshape(self.action_conv, [-1, 4 * board_width * board_width], name="action_conv_flat")
        self.action_fc = tf.layers.dense(inputs=self.action_conv_flat, units=board_width * board_width + 1,
                                         activation=tf.nn.log_softmax, name="action_fc")
        # 4. v值输出
        self.evaluation_conv = tf.layers.conv2d(inputs=self.conv3, filters=2, kernel_size=[1, 1], padding="same",
                                                data_format="channels_last", activation=tf.nn.relu, name="evaluation_conv")
        self.evaluation_conv_flat = tf.reshape(self.evaluation_conv, [-1, 2 * board_width * board_width], name="evaluation_conv_flat")
        self.evaluation_fc1 = tf.layers.dense(inputs=self.evaluation_conv_flat, units=64, activation=tf.nn.relu, name="evaluation_fc1")
        self.evaluation_fc2 = tf.layers.dense(inputs=self.evaluation_fc1, units=1, activation=tf.nn.tanh, name="evaluation_fc2")

        # 定义损失函数
        # 1. v值损失函数
        self.labels = tf.placeholder(tf.float32, shape=[None, 1], name="labels")  # 标记游戏的输赢，对应self.evaluation_fc2
        self.value_loss = tf.losses.mean_squared_error(self.labels, self.evaluation_fc2)
        # 2. P数组损失函数
        self.mcts_probs = tf.placeholder(tf.float32, shape=[None, board_width * board_width + 1], name="mcts_probs")
        self.policy_loss = tf.negative(tf.reduce_mean(tf.reduce_sum(tf.multiply(self.mcts_probs, self.action_fc), 1)), name="policy_loss")
        # 3. L2正则项
        l2_penalty_beta = 1e-4
        vars = tf.trainable_variables()
        l2_penalty = l2_penalty_beta * tf.add_n([tf.nn.l2_loss(v) for v in vars if 'bias' not in v.name.lower()])
        # 4. 所有加起来成为损失函数
        self.loss = self.value_loss + self.policy_loss + l2_penalty

        # 计算熵值
        self.entropy = tf.negative(tf.reduce_mean(tf.reduce_sum(tf.exp(self.action_fc) * self.action_fc, 1)), name="entropy")

        # 训练用的优化器
        self.learning_rate = tf.placeholder(tf.float32, name="learning_rate")
        self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate, name="optimizer").minimize(self.loss)

        # tensorflow的session
        self.session = tf.Session()
        self.session.run(tf.global_variables_initializer())

        # 模型的存储
        self.saver = tf.train.Saver(max_to_keep=123456789)  # max_to_keep设置一个很大的值防止保存的中间模型被删除
        if model_file is not None:
            self.restore_model(model_file)

    def policy_value(self, state_batch):
        log_act_probs, value = self.session.run(
                [self.action_fc, self.evaluation_fc2],
                feed_dict={self.input_states: state_batch})
        act_probs = np.exp(log_act_probs)
        return act_probs, value

    def policy_value_fn(self, board):
        legal_moves = board.get_available_moves()
        current_state = np.ascontiguousarray(board.current_state().reshape(
                -1, 3, self.board_width, self.board_width))
        act_probs, value = self.policy_value(current_state)
        act_probs = zip(legal_moves, act_probs[0][legal_moves])
        return act_probs, value

    def train_step(self, state_batch, mcts_probs, winner_batch, lr):
        winner_batch = np.reshape(winner_batch, (-1, 1))
        loss, entropy, _ = self.session.run(
                [self.loss, self.entropy, self.optimizer],
                feed_dict={self.input_states: state_batch,
                           self.mcts_probs: mcts_probs,
                           self.labels: winner_batch,
                           self.learning_rate: lr})
        return loss, entropy

    def save_model(self, model_path):
        self.saver.save(self.session, model_path)

    def restore_model(self, model_path):
        self.saver.restore(self.session, model_path)


class ReversiPretrainedPolicyValueNet():
    def __init__(self, board_width, graph_file):
        self.board_width = board_width

        graph_def = tf.GraphDef()
        with open(graph_file, "rb") as file:
            graph_def.ParseFromString(file.read())
        tf.import_graph_def(graph_def, name="pretrained")

        # tensorflow的session
        self.session = tf.Session()
        self.session.run(tf.global_variables_initializer())

        self.input_states = self.session.graph.get_tensor_by_name("pretrained/input_states:0")
        self.action_fc = self.session.graph.get_tensor_by_name("pretrained/action_fc/LogSoftmax:0")
        self.evaluation_fc2 = self.session.graph.get_tensor_by_name("pretrained/evaluation_fc2/Tanh:0")

    def policy_value(self, state_batch):
        log_act_probs, value = self.session.run(
                [self.action_fc, self.evaluation_fc2],
                feed_dict={self.input_states: state_batch})
        act_probs = np.exp(log_act_probs)
        return act_probs, value

    def policy_value_fn(self, board):
        legal_moves = board.get_available_moves()
        current_state = np.ascontiguousarray(board.current_state().reshape(
                -1, 3, self.board_width, self.board_width))
        act_probs, value = self.policy_value(current_state)
        act_probs = zip(legal_moves, act_probs[0][legal_moves])
        return act_probs, value
