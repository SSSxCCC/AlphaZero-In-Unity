import numpy as np
from game import Board, Game


class ReversiBoard(Board):
    """
    3*3棋盘被视为：
    6 7 8
    3 4 5
    0 1 2
    move=5时二维坐标是(1,2)
    """

    def __init__(self, width=8):
        self.width = width
        self.states = {}  # 游戏状态，键是动作值（棋盘位置），值是棋子所属的玩家编号
        self.players = [1, 2]  # 玩家编号

    def init_board(self, start_player=0):
        """
        初始化棋盘。
        :param start_player: 为0表示第一个玩家先手，为1表示第二个玩家先手
        """
        self.current_player = self.players[start_player]
        opponent = self.players[0] if self.current_player == self.players[1] else self.players[1]
        middle = self.width // 2
        self.states = {self.location_to_move([middle-1, middle-1]): self.current_player, self.location_to_move([middle, middle]): self.current_player,
                       self.location_to_move([middle-1, middle]): opponent, self.location_to_move([middle, middle-1]): opponent}
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
        if move not in range(self.width * self.width + 1):
            return -1
        return move

    def current_state(self):
        """
        返回以当前玩家的视角看到的棋盘状态（神经网络的输入）。
        :return: 3*width*width
        """
        square_state = np.zeros((3, self.width, self.width))
        if self.states:
            moves, players = np.array(list(zip(*self.states.items())))
            move_curr = moves[players == self.current_player]
            move_oppo = moves[players != self.current_player]
            square_state[0][move_curr // self.width, move_curr % self.width] = 1.0  # 所有自己棋子
            square_state[1][move_oppo // self.width, move_oppo % self.width] = 1.0  # 所有对手棋子
        if len(self.states) % 2 == 0:
            square_state[2][:, :] = 1.0  # 区分自己棋子颜色
        return square_state[:, ::-1, :]

    def __search(self, player, h, w, reverse = False):
        """
        找位置(h,w)对于玩家player能不能下子，如果能则返回True，否则返回False。
        :param player: 玩家编号
        :param h: 纵轴位置
        :param w: 横轴位置
        :param reverse: 是否将找到的所有对手的能翻转的棋子变成player的棋子
        :return: 能不能下子
        """
        all_opponent_moves = []

        def find(scope):  # 往某个方向找
            find_self, opponent_moves = False, []
            for x, y in scope:
                move = self.location_to_move([y, x])
                if move in self.states:
                    if self.states[move] == player:
                        find_self = True
                        break
                    else:
                        opponent_moves.append(move)
                else:
                    break
            if find_self and len(opponent_moves) > 0:  # 这次找的有效
                all_opponent_moves.extend(opponent_moves)

        find(zip([w] * len(range(h + 1, self.width)), range(h + 1, self.width)))  # 往上找
        find(zip([w] * len(range(h - 1, -1, -1)), range(h - 1, -1, -1)))  # 往下找
        find(zip(range(w - 1, -1, -1), [h] * len(range(w - 1, -1, -1))))  # 往左找
        find(zip(range(w + 1, self.width), [h] * len(range(w + 1, self.width))))  # 往右找
        find(zip(range(w - 1, -1, -1), range(h + 1, self.width)))  # 往左上找
        find(zip(range(w + 1, self.width), range(h + 1, self.width)))  # 往右上找
        find(zip(range(w - 1, -1, -1), range(h - 1, -1, -1)))  # 往左下找
        find(zip(range(w + 1, self.width), range(h - 1, -1, -1)))  # 往右下找

        if len(all_opponent_moves) == 0:
            return False
        if reverse:
            for move in all_opponent_moves:
                self.states[move] = player
        return True

    def do_move(self, move):
        """
        当前玩家执行动作值为move的动作。
        :param move: 动作值
        """
        if move != self.width * self.width:  # 最后一个动作是不下子
            self.states[move] = self.current_player
            loc = self.move_to_location(move)
            self.__search(self.current_player, loc[0], loc[1], reverse=True)
        self.current_player = (self.players[0] if self.current_player == self.players[1] else self.players[1])  # 切换到另一个玩家
        self.last_move = move

    def game_end(self):
        """
        检查游戏是否结束。
        :return: 返回游戏是否结束的bool值和赢了的玩家编号，玩家编号为-1表示没有人赢。
        """
        player1_availables = self.__get_available_moves(self.players[0])
        player2_availables = self.__get_available_moves(self.players[1])
        if len(player1_availables) == 1 and len(player2_availables) == 1 and player1_availables[0] == self.width*self.width and player2_availables[0] == self.width*self.width:  # 游戏结束了
            player1_count, player2_count = 0, 0
            for move, player in self.states.items():
                if player == self.players[0]:
                    player1_count += 1
                elif player == self.players[1]:
                    player2_count += 1
                else:
                    print("严重错误：棋盘上存在非任何玩家棋子：" + str(player))
            if player1_count > player2_count:  # 玩家一赢了
                return True, self.players[0]
            elif player1_count < player2_count:  # 玩家二赢了
                return True, self.players[1]
            else:  # 平局
                return True, -1
        else:  # 还没结束
            return False, -1

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
        return self.width * self.width + 1

    def __get_available_moves(self, player):
        availables = []
        for h in range(self.width):
            for w in range(self.width):
                move = self.location_to_move([h, w])
                if move not in self.states and self.__search(player, h, w, reverse=False):
                    availables.append(move)
        if len(availables) == 0:
            availables.append(self.width * self.width)
        return availables

    def get_available_moves(self):
        """
        :return: 能走的动作列表
        """
        return self.__get_available_moves(self.current_player)


class ReversiGame(Game):
    """
    翻转棋游戏。
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
