
class TicTacToe:
    def __init__(self):
        self.currentPlayer = 1
        self.state = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    def clone(self):
        clone = TicTacToe()
        clone.currentPlayer = self.currentPlayer
        clone.state = self.state[:]
        return clone

    def applymove(self, move):
        self.state[move] = self.currentPlayer
        self.currentPlayer = 3 - self.currentPlayer

    def getallmoves(self):
        # If the game is over then there are no more moves
        if self.getboardstate(1) != 0.5:
            return []
        return [i for i in range(len(self.state)) if self.state[i] == 0]

    def getboardstate(self, player):
        for (a, b, c) in [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]:
            if self.state[a] == self.state[b] and self.state[a] == self.state[c] and self.state[a] != 0:
                return 1.0 if self.state[a] == player else 0.0
        return 0.5

    def isgameover(self):
        return self.getallmoves() == []

    def tostring(self):
        result = ""
        for i in range(3):
            for j in range(3):
                result += ['.', 'X', 'O'][self.state[i * 3 + j]]
            result += "\n"
        return result
