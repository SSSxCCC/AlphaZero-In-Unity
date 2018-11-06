import numpy as np
from game import Board, Game


class Connect4Board(Board):
    """
    3*3棋盘被视为：
    6 7 8
    3 4 5
    0 1 2
    move=5时二维坐标是(1,2)
    """

    def __init__(self, width=7, height=6):
        self.width = width
        self.height = height
        self.n_in_row = 4  # 多少棋子连到一起就算赢
        self.states = {}  # 游戏状态，键是棋盘位置，值是棋子所属的玩家编号
        self.players = [1, 2]  # 玩家编号

    def init_board(self, start_player=0):
        """
        初始化棋盘。
        :param start_player: 为0表示第一个玩家先手，为1表示第二个玩家先手
        """
        self.current_player = self.players[start_player]
        self.states = {}
        self.last_move = -1

    def current_state(self):
        """
        返回以当前玩家的视角看到的棋盘状态（神经网络的输入）。
        :return: 3*height*width
        """
        square_state = np.zeros((3, self.height, self.width))
        if self.states:
            moves, players = np.array(list(zip(*self.states.items())))
            move_curr = moves[players == self.current_player]
            move_oppo = moves[players != self.current_player]
            square_state[0][move_curr // self.width, move_curr % self.width] = 1.0  # 所有自己棋子
            square_state[1][move_oppo // self.width, move_oppo % self.width] = 1.0  # 所有对手棋子
        if len(self.states) % 2 == 0:
            square_state[2][:, :] = 1.0  # 区分自己棋子颜色
        return square_state[:, ::-1, :]

    def __move_to_location(self, move):
        if move < self.width:
            while move in self.states:
                move += self.width
            return move
        else:
            return -1

    def do_move(self, move):
        """
        当前玩家执行动作值为move的动作。
        :param move: 动作值
        """
        if move < self.width:
            self.states[self.__move_to_location(move)] = self.current_player
        else:
            for loc in range(move - self.width, self.width * self.height, self.width):
                if loc not in self.states:
                    break
                elif (loc + self.width) not in self.states:
                    self.states.pop(loc)
                else:
                    self.states[loc] = self.states[loc + self.width]

        self.current_player = (self.players[0] if self.current_player == self.players[1] else self.players[1])  # 切换到另一个玩家
        self.last_move = move

    def __has_a_winner(self):
        """
        判断游戏是否结束。
        :return: 返回一个bool值表示游戏是否结束，以及一个整数，-1表示没有结束，其他值表示胜利的玩家。
        """
        width = self.width
        height = self.height
        states = self.states
        n = self.n_in_row

        locs = list(states.keys())
        if len(locs) < self.n_in_row + 2:
            return False, -1

        winner = -1
        has_winner = False

        for m in locs:
            h = m // width
            w = m % width
            player = states[m]

            if (w in range(width - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n))) == 1):
                if has_winner and winner != player:
                    return True, -1
                elif not has_winner:
                    winner = player
                    has_winner = True

            if (h in range(height - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * width, width))) == 1):
                if has_winner and winner != player:
                    return True, -1
                elif not has_winner:
                    winner = player
                    has_winner = True

            if (w in range(width - n + 1) and h in range(height - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * (width + 1), width + 1))) == 1):
                if has_winner and winner != player:
                    return True, -1
                elif not has_winner:
                    winner = player
                    has_winner = True

            if (w in range(n - 1, width) and h in range(height - n + 1) and
                    len(set(states.get(i, -1) for i in range(m, m + n * (width - 1), width - 1))) == 1):
                if has_winner and winner != player:
                    return True, -1
                elif not has_winner:
                    winner = player
                    has_winner = True

        if has_winner:
            return True, winner
        else:
            return False, -1

    def game_end(self):
        """
        检查游戏是否结束。
        :return: 返回游戏是否结束的bool值和赢了的玩家编号，玩家编号为-1表示没有人赢。
        """
        win, winner = self.__has_a_winner()
        if win:  # 玩家winnner赢了
            return True, winner
        elif not len(self.get_available_moves()):  # 平局
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
        return self.width * 2

    def get_available_moves(self):
        """
        :return: 能走的动作列表
        """
        availables = []
        for move in range(self.width):
            if (move + self.width * (self.height - 1)) not in self.states:
                availables.append(move)
        for move in range(self.width, self.width * 2):
            if (move - self.width) in self.states and self.states[move - self.width] == self.current_player:
                availables.append(move)
        return availables


class Connect4Game(Game):
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
        height = self.board.height

        print("Player", player1, "with X".rjust(3))
        print("Player", player2, "with O".rjust(3))
        print()
        for x in range(width):
            print("{0:8}".format(x), end='')
        print('\r\n')
        for i in range(height - 1, -1, -1):
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
