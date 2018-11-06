import numpy as np


class Board:
    """"
    棋盘以及对玩家动作的反应方法
    """
    def init_board(self, start_player=0):
        """
        初始化棋盘。
        :param start_player: 为0表示第一个玩家先手，为1表示第二个玩家先手
        """
        pass

    def current_state(self):
        """
        返回以当前玩家的视角看到的棋盘状态，神经网络的输入。
        :return: 当前玩家的视角看到的棋盘状态，输入到神经网络
        """
        pass

    def do_move(self, move):
        """
        当前玩家执行动作值为move的动作。
        :param move: 动作值
        """
        pass

    def game_end(self):
        """
        检查游戏是否结束。
        :return: 返回游戏是否结束的bool值和赢了的玩家编号，玩家编号为-1表示没有人赢。
        """
        pass

    def get_current_player(self):
        """
        :return: 当前待落子玩家编号。
        """
        pass

    def get_action_count(self):
        """
        得到动作总数量。每个动作是在[0, 动作总数量)之间的一个整数。
        :return: 玩家动作总数量
        """
        pass

    def get_available_moves(self):
        """
        :return: 能走的动作列表
        """
        pass


class Game:
    """
    双人博弈游戏。
    """
    def __init__(self, board):
        self.board = board

    def graphic(self, player1, player2):
        """
        打印棋盘状态。
        :param board: 棋盘
        :param player1: 第一个玩家编号
        :param player2: 第二个玩家编号
        """
        pass

    def start_play(self, player1, player2, start_player=0, is_shown=True, temp=1e-3):
        """
        开始一局游戏，返回胜利玩家编号，如果游戏结束没有人赢则返回-1。
        :param player1: 玩家一
        :param player2: 玩家二
        :param start_player: 为0表示玩家一先走，为1表示玩家二先走
        :param is_shown: 是否显示棋盘
        :return: 胜利玩家编号，或者-1
        """
        """start a game between two players"""
        if start_player not in (0, 1):
            raise Exception('start_player should be either 0 (player1 first) '
                            'or 1 (player2 first)')
        self.board.init_board(start_player)
        p1, p2 = self.board.players
        player1.set_player_ind(p1)
        player2.set_player_ind(p2)
        players = {p1: player1, p2: player2}
        if is_shown:
            self.graphic(player1.player, player2.player)
        while True:
            current_player = self.board.get_current_player()
            player_in_turn = players[current_player]
            move = player_in_turn.get_action(self.board, temp=temp)
            self.board.do_move(move)
            if is_shown:
                self.graphic(player1.player, player2.player)
            end, winner = self.board.game_end()
            if end:
                if is_shown:
                    if winner != -1:
                        print("Game end. Winner is", players[winner])
                    else:
                        print("Game end. Tie")
                return winner

    def start_self_play(self, player, is_shown=False, temp=1e-3):
        """
        自我对局，返回对局数据(state, mcts_probs, z)，用来训练。
        :param player: MCTSPlayer
        :param is_shown: 是否显示棋盘
        :param temp: 论文里面的温度值
        :return: 赢了的玩家编号和对局数据(state, mcts_probs, z)列表
        """
        self.board.init_board()
        p1, p2 = self.board.players
        states, mcts_probs, current_players = [], [], []
        while True:
            move, move_probs = player.get_action(self.board, temp=temp, return_prob=True)
            states.append(self.board.current_state())  # 保存棋局状态
            mcts_probs.append(move_probs)  # 保存pi值
            current_players.append(self.board.current_player)

            self.board.do_move(move)
            if is_shown:
                self.graphic(p1, p2)
            end, winner = self.board.game_end()
            if end:
                winners_z = np.zeros(len(current_players))
                if winner != -1:
                    winners_z[np.array(current_players) == winner] = 1.0
                    winners_z[np.array(current_players) != winner] = -1.0
                player.reset_player()
                if is_shown:
                    if winner != -1:
                        print("Game end. Winner is player:", winner)
                    else:
                        print("Game end. Tie")
                return winner, zip(states, mcts_probs, winners_z)
