import random
import json
import time

import numpy as np
from collections import defaultdict, deque
from play import MCTSPlayer


class Trainer:
    def __init__(self, game, policy_value_net, save_dir,
                 learn_rate=2e-4,
                 temp=1.0,
                 n_playout=300,
                 c_puct=5,
                 buffer_size=10000,
                 batch_size=512,
                 epochs=5,
                 check_freq=50,
                 play_batch_size=1,
                 game_batch_num=100000):
        """
        :param game: 具体某个游戏的Game对象
        :param policy_value_net: 具体某个游戏的PolicyValueNet对象
        :param save_dir: 模型保存目录
        :param learn_rate: 学习速率
        :param temp: 论文里面的温度值
        :param n_playout: 每步的蒙特卡洛搜索次数
        :param c_puct: 论文里面的c_puct。一个在范围(0, inf)的数字，控制探索等级。值越小越依赖于Q值，值越大越依赖于P值
        :param buffer_size: 数据集保存的大小
        :param batch_size: 训练参数
        :param epochs: 每次更新执行train_steps的次数
        :param check_freq: 每玩多少批次就保存
        :param play_batch_size: 每批次游戏有多少局
        :param game_batch_num: 总共玩多少批次游戏
        """
        self.game = game
        self.policy_value_net = policy_value_net
        self.save_dir = save_dir

        self.learn_rate = learn_rate  # 学习速率
        self.temp = temp  # 论文里面的温度值
        self.n_playout = n_playout  # 每步的蒙特卡洛搜索次数
        self.c_puct = c_puct  # 论文里面的c_puct。一个在范围(0, inf)的数字，控制探索等级。值越小越依赖于Q值，值越大越依赖于P值
        self.data_buffer = deque(maxlen=buffer_size)
        self.batch_size = batch_size  # 训练参数
        self.epochs = epochs  # 每次更新执行train_steps的次数
        self.check_freq = check_freq  # 每玩多少批次就保存
        self.play_batch_size = play_batch_size  # 每批次游戏有多少局
        self.game_batch_num = game_batch_num  # 总共玩多少批次游戏

        self.lr_multiplier = 1.0  # 根据KL调整学习速率
        self.kl_targ = 0.02

        self.mcts_player = MCTSPlayer(self.policy_value_net.policy_value_fn, c_puct=self.c_puct, n_playout=self.n_playout, is_selfplay=True)

    def get_equi_data(self, play_data):
        """
        通过翻转旋转这些等价替换来增加数据集数量。具体的游戏需要重写这个方法来实现。
        :param play_data: 原数据集
        :return: 增加后的数据集
        """
        return play_data

    def collect_selfplay_data(self, n_games=1):
        """
        通过自我对局，为训练收集游戏数据。
        :param n_games: 玩游戏的局数
        """
        for i in range(n_games):
            winner, play_data = self.game.start_self_play(self.mcts_player, temp=self.temp)
            play_data = list(play_data)[:]
            self.episode_len = len(play_data)
            play_data = self.get_equi_data(play_data)
            self.data_buffer.extend(play_data)

    def policy_update(self):
        """
        根据在自我对局中收集的游戏数据，训练神经网络。
        :return: 返回损失函数值和熵值
        """
        mini_batch = random.sample(self.data_buffer, self.batch_size)
        state_batch = [data[0] for data in mini_batch]
        mcts_probs_batch = [data[1] for data in mini_batch]
        winner_batch = [data[2] for data in mini_batch]
        old_probs, old_v = self.policy_value_net.policy_value(state_batch)
        for i in range(self.epochs):
            loss, entropy = self.policy_value_net.train_step(state_batch, mcts_probs_batch, winner_batch, self.learn_rate*self.lr_multiplier)
            new_probs, new_v = self.policy_value_net.policy_value(state_batch)
            kl = np.mean(np.sum(old_probs * (np.log(old_probs + 1e-10) - np.log(new_probs + 1e-10)), axis=1))
            if kl > self.kl_targ * 4:  # D_KL偏离太远
                break
        # 调整学习速率
        if kl > self.kl_targ * 2 and self.lr_multiplier > 0.01:
            self.lr_multiplier /= 1.5
        elif kl < self.kl_targ / 2 and self.lr_multiplier < 100:
            self.lr_multiplier *= 1.5

        explained_var_old = (1 - np.var(np.array(winner_batch) - old_v.flatten()) / np.var(np.array(winner_batch)))
        explained_var_new = (1 - np.var(np.array(winner_batch) - new_v.flatten()) / np.var(np.array(winner_batch)))
        print("loss={}, entropy={}, kl={:.5f}, lr_multiplier={:.3f}, explained_var_old={:.3f}, explained_var_new={:.3f}".format
            (loss, entropy, kl, self.lr_multiplier, explained_var_old, explained_var_new))
        return loss, entropy
    """
    def policy_evaluate(self, n_games=10):
        current_mcts_player = MCTSPlayer(self.policy_value_net.policy_value_fn, c_puct=self.c_puct, n_playout=self.n_playout)
        pure_mcts_player = MCTS_Pure(c_puct=5, n_playout=self.pure_mcts_playout_num)
        win_cnt = defaultdict(int)
        for i in range(n_games):
            winner = self.game.start_play(current_mcts_player, pure_mcts_player, start_player=i % 2, is_shown=False)
            win_cnt[winner] += 1
        win_ratio = 1.0*(win_cnt[1] + 0.5*win_cnt[-1]) / n_games
        print("win: {}, lose: {}, tie: {}, win_ratio: {}".format(win_cnt[1], win_cnt[2], win_cnt[-1], win_ratio))
        return win_ratio
    """
    def run(self):
        try:
            start_time = time.time()
            for i in range(self.game_batch_num):
                self.collect_selfplay_data(self.play_batch_size)
                print("batch_i={}, episode_len={}".format(i+1, self.episode_len))
                if len(self.data_buffer) > self.batch_size:
                    loss, entropy = self.policy_update()
                if (i+1) % self.check_freq == 0:
                    print("save model " + str(i+1))
                    save_dir = self.save_dir + "/" + str(i+1)
                    self.policy_value_net.save_model(save_dir + "/policy_value_net.model")
                    with open(save_dir + "/statistics.json", "w") as file:
                        json.dump({"loss": float(loss), "entropy": float(entropy), "time": time.time()-start_time}, file)
        except KeyboardInterrupt:
            print('\n\rquit')
