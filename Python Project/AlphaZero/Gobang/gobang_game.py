import numpy as np
from game import Board, Game


class GobangBoard(Board):
    """
    3*3棋盘被视为：
    6 7 8
    3 4 5
    0 1 2
    move=5时二维坐标是(1,2)
    """

    def __init__(self, width=8, n_in_row=5):
        self.width = width
        self.n_in_row = n_in_row  # 多少棋子连到一起就算赢
        self.states = {}  # 游戏状态，键是动作值（棋盘位置），值是棋子所属的玩家编号
        self.players = [1, 2]  # 玩家编号

    def init_board(self, start_player=0):
        """
        初始化棋盘。
        :param start_player: 为0表示第一个玩家先手，为1表示第二个玩家先手
        """
        if self.width < self.n_in_row:
            raise Exception('棋盘的长和宽不能小于{}'.format(self.n_in_row))
        self.current_player = self.players[start_player]
        self.availables = list(range(self.width * self.width))  # 可以走的动作
        self.states = {}
        self.last_move = -1

    def move_to_location(self, move):
        """
        动作值转化为二维坐标。
        :param move: 动作值
        :return: 二维坐标
        """
        h = move // self.width
        w = move % self.width
        return [h, w]

    def location_to_move(self, location):
        """
        二维坐标转化为动作值。
        :param location: 二维坐标
        :return: 动作值
        """
        if len(location) != 2:
            return -1
        h = location[0]
        w = location[1]
        move = h * self.width + w
        if move not in range(self.width * self.width):
            return -1
        return move

    def current_state(self):
        """
        返回以当前玩家的视角看到的棋盘状态（神经网络的输入）。
        :return: 4*width*width
        """
        square_state = np.zeros((4, self.width, self.width))
        if self.states:
            moves, players = np.array(list(zip(*self.states.items())))
            move_curr = moves[players == self.current_player]
            move_oppo = moves[players != self.current_player]
            square_state[0][move_curr // self.width, move_curr % self.width] = 1.0  # 所有自己棋子
            square_state[1][move_oppo // self.width, move_oppo % self.width] = 1.0  # 所有对手棋子
            square_state[2][self.last_move // self.width, self.last_move % self.width] = 1.0  # 上一步棋子落点
        if len(self.states) % 2 == 0:
            square_state[3][:, :] = 1.0  # 区分自己棋子颜色
        return square_state[:, ::-1, :]

    def do_move(self, move):
        """
        当前玩家执行动作值为move的动作。
        :param move: 动作值
        """
        self.states[move] = self.current_player
        self.availables.remove(move)
        self.current_player = (self.players[0] if self.current_player == self.players[1] else self.players[1])  # 切换到另一个玩家
        self.last_move = move

    def __has_a_winner(self):
        """
        判断游戏是否结束。
        :return: 返回一个bool值表示游戏是否结束，以及一个整数，-1表示没有结束，其他值表示胜利的玩家。
        """
        width = self.width
        states = self.states
        n = self.n_in_row

        moved = list(set(range(width * width)) - set(self.availables))
        if len(moved) < self.n_in_row + 2:
            return False, -1

        for m in moved:
            h = m // width
            w = m % width
            player = states[m]

            if (w in range(width - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n))) == 1):
                return True, player

            if (h in range(width - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * width, width))) == 1):
                return True, player

            if (w in range(width - n + 1) and h in range(width - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * (width + 1), width + 1))) == 1):
                return True, player

            if (w in range(n - 1, width) and h in range(width - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * (width - 1), width - 1))) == 1):
                return True, player

        return False, -1

    def game_end(self):
        """
        检查游戏是否结束。
        :return: 返回游戏是否结束的bool值和赢了的玩家编号，玩家编号为-1表示没有人赢。
        """
        win, winner = self.__has_a_winner()
        if win:  # 玩家winnner赢了
            return True, winner
        elif not len(self.availables):  # 平局
            return True, -1
        return False, -1  # 还没结束

    def get_current_player(self):
        """
        :return: 当前待落子玩家编号。
        """
        return self.current_player

    def get_action_count(self):
        """
        得到动作总数量。每个动作是在[0, 动作总数量)之间的一个整数。
        :return: 玩家动作总数量
        """
        return self.width * self.width

    def get_available_moves(self):
        """
        :return: 能走的动作列表
        """
        return self.availables


class GobangGame(Game):
    """
    五子棋游戏。
    """
    def graphic(self, player1, player2):
        """
        打印棋盘状态。
        :param board: 棋盘
        :param player1: 第一个玩家编号
        :param player2: 第二个玩家编号
        """
        width = self.board.width

        print("Player", player1, "with X".rjust(3))
        print("Player", player2, "with O".rjust(3))
        print()
        for x in range(width):
            print("{0:8}".format(x), end='')
        print('\r\n')
        for i in range(width - 1, -1, -1):
            print("{0:4d}".format(i), end='')
            for j in range(width):
                loc = i * width + j
                p = self.board.states.get(loc, -1)
                if p == player1:
                    print('X'.center(8), end='')
                elif p == player2:
                    print('O'.center(8), end='')
                else:
                    print('_'.center(8), end='')
            print('\r\n\r\n')
