
def _get_board(tile):
    return int(tile / 9)


def _get_tile(tile):
    return tile % 9


class SuperTicTacToe:
    def __init__(self):
        self.currentPlayer = 1
        self.next_board = -1
        self.state = [0, 0, 0, 0, 0, 0, 0, 0, 0,  # Top Left 3x3
                      0, 0, 0, 0, 0, 0, 0, 0, 0,  # Top Middle 3x3
                      0, 0, 0, 0, 0, 0, 0, 0, 0,  # Top Right 3x3
                      0, 0, 0, 0, 0, 0, 0, 0, 0,  # Middle Left 3x3
                      0, 0, 0, 0, 0, 0, 0, 0, 0,  # Middle Middle 3x3
                      0, 0, 0, 0, 0, 0, 0, 0, 0,  # Middle Right 3x3
                      0, 0, 0, 0, 0, 0, 0, 0, 0,  # Bottom Left 3x3
                      0, 0, 0, 0, 0, 0, 0, 0, 0,  # Bottom Middle 3x3
                      0, 0, 0, 0, 0, 0, 0, 0, 0]  # Bottom Right 3x3

    def clone(self):
        clone = SuperTicTacToe()
        clone.currentPlayer = self.currentPlayer
        clone.state = self.state[:]
        clone.next_board = self.next_board
        return clone

    def applymove(self, move):
        self.state[move] = self.currentPlayer
        self.currentPlayer = 3 - self.currentPlayer

        # the next board is determined by the tile that the player moved into
        self.next_board = _get_tile(move)
        # if the next board is already decided then the player is given a wildcard move
        if self.get_sub_state(self.next_board) != 0:
            self.next_board = -1

    def getallmoves(self):
        # If the game is over then there are no more moves
        if self.getboardstate(1) != 0.5:
            return []
        # if the next board is not set then just do anything
        if self.next_board == -1:
            sub_states = self.get_sub_states()
            return [i for i in range(len(self.state)) if self.state[i] == 0 and sub_states[_get_board(i)] == 0]

        # if the next_board is set then only return the legal moves for that board
        if self.get_sub_state(self.next_board) == 0:
            return [9*self.next_board + i for i in range(9) if self.state[9*self.next_board + i] == 0]
        return []

    def getboardstate(self, player):
        boards = self.get_sub_states()
        for (a, b, c) in [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]:
            if boards[a] == boards[b] and boards[a] == boards[c] and boards[a] != 0 and boards[a] != 3:
                return 1.0 if boards[a] == player else 0.0
        return 0.5

    def get_sub_states(self):
        boards = [0, 0, 0,
                  0, 0, 0,
                  0, 0, 0]
        for i in range(len(boards)):
            boards[i] = self.get_sub_state(i)
        return boards

    def get_sub_state(self, board):
        for (a, b, c) in [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]:
            if self.state[9 * board + a] == self.state[9 * board + b] and self.state[9 * board + a] == self.state[9 * board + c] and \
                    self.state[9 * board + a] != 0:
                return self.state[9 * board + a]
        return 0 if [i for i in range(9) if self.state[9 * board + i] == 0] != [] else 3

    def isgameover(self):
        return self.getallmoves() == []

    def tostring(self):
        result = ""
        for a in range(3):
            for b in range(3):
                for c in range(3):
                    for d in range(3):
                        tile = d + 3 * b + 9 * c + 27 * a
                        state = self.get_sub_state(_get_board(tile))
                        if state == 0:
                            state = self.state[tile]
                        result += ['.', 'X', 'O', '-'][state]
                    result += " "
                result += "\n"
            result += "\n"
        return result
