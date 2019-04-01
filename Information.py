import chess


def consistent_with_all(state, action, info_list):
    return all(info.consistent_with(state, action) for info in info_list)


class Information:
    def consistent_with(self, state, action):
        pass


# Says that the state is consistent with a given viewport of the game
class ViewportInformation(Information):

    def __init__(self, info):
        self.info = info

    def consistent_with(self, state, action):
        return all(state.board.piece_at(tile) == contents for tile, contents in self.info.items())

    def __repr__(self):
        from Chess import TYPES
        result = ""
        for i in range(8):
            for j in range(8):
                if chess.square(j, 7-i) not in self.info:
                    result += "·"
                else:
                    piece = self.info[chess.square(j, 7-i)] if chess.square(j, 7-i) in self.info else None
                    if piece is None:
                        result += TYPES[6]
                    else:
                        result += TYPES[piece.piece_type * (1 if piece.color == chess.WHITE else -1) + 6]
            result += "\n"
        return result


# Says that the player moved some piece to a given tile
class SomethingMovedTo(Information):

    def __init__(self, tile):
        self.moved_to = tile

    def consistent_with(self, state, action):
        return action.to_square == self.moved_to


# Says that the given move is illegal to make after this player has gone
class IllegalMove(Information):

    def __init__(self, move):
        self.move = move

    def consistent_with(self, state, action):
        return self.move not in state.board.legal_moves


# Says that the given move is legal to make after this player has gone
class LegalMove(Information):

    def __init__(self, move):
        self.move = move

    def consistent_with(self, state, action):
        return self.move in state.board.legal_moves


class NothingInSix(Information):
    def consistent_with(self, s, action):
        return s.gettype(chess.A6) + s.gettype(chess.B6) + s.gettype(chess.C6) + s.gettype(chess.D6) + \
               s.gettype(chess.E6) + s.gettype(chess.F6) + s.gettype(chess.G6) + s.gettype(chess.H6) == 0


class MovedKnight(Information):
    def consistent_with(self, s, action):
        return s.gettype(action.to_square) == chess.KNIGHT


class BlackMissingPawn(Information):
    def consistent_with(self, state, action):
        return state.board.fen().count('p') < 8  # Using fen bad for efficiency


class WhiteMissingKnight(Information):
    def consistent_with(self, state, action):
        return state.board.fen().count('N') < 2  # Using fen bad for efficiency