
import chess


TYPES = ['♚', '♛', '♜', '♝', '♞', '♟', ' ', '♙', '♘', '♗', '♖', '♕', '♔']


# Moves are encoded the same way as they  are in the AlphaGoZero paper
class Chess:
    def __init__(self):
        self.board = chess.Board()
        self.currentPlayer = 1

    def clone(self):
        clone = Chess()
        clone.board = self.board.copy()
        clone.currentPlayer = self.currentPlayer
        return clone

    def mirror(self):
        mirror = Chess()
        mirror.board = self.board.mirror()
        mirror.currentPlayer = 3 - self.currentPlayer
        return mirror

    def __eq__(self, other):
        if type(other) is not Chess:
            return False
        return self.board == other.board

    # Assumes that the move is legal
    def applymove(self, move):
        if move is None:
            self.board.push(chess.Move.null())
        else:
            self.board.push(move)
        self.currentPlayer = 3 - self.currentPlayer
        return self

    # Assumes that the move is legal
    def apply_move_did_capture(self, move):
        capture = self.board.piece_at(move.to_square) is not None
        self.applymove(move)
        return capture

    def try_apply_move(self, move):
        if move in self.board.legal_moves:
            self.applymove(move)
            return True
        return False

    def try_apply_move_did_capture(self, move):
        if move in self.board.legal_moves:
            return True, self.apply_move_did_capture(move)
        return False, False

    def getallmoves(self):
        legal_moves_ = [move for move in self.board.legal_moves]
        legal_moves_.append(None)  # No move is a legal move
        return legal_moves_

    def getboardstate(self, player):
        score = 0.5
        if self.board.result() == "1-0":
            score = 1.0
        elif self.board.result() == "0-1":
            score = 0.0
        return score if player == 1 else 1-score

    def isgameover(self):
        return self.board.result() != "*"

    def gettype(self, tile):
        piece = self.board.piece_at(tile)
        return piece.piece_type if piece is not None else 0

    def getchar(self, tile):
        piece = self.board.piece_at(tile)
        if piece is None:
            return TYPES[6]
        return TYPES[piece.piece_type * (1 if piece.color == chess.WHITE else -1) + 6]

    def getblindchar(self, tile):
        piece = self.board.piece_at(tile)
        if piece is None or self.currentPlayer != (1 if piece.color == chess.WHITE else 2):
            return '·'
        return TYPES[piece.piece_type * (1 if piece.color == chess.WHITE else -1) + 6]

    def tostring(self):
        result = ""
        for i in range(8):
            for j in range(8):
                result += self.getchar(8*(7 - i) + j)
            result += "\n"
        return result

    def boundary_string(self):
        result = " abcdefgh\n"
        for i in range(8):
            result += str(8 - i) + ""
            for j in range(8):
                result += self.getchar(8*(7 - i) + j)
            result += "" + str(8 - i) + "\n"
        result += " abcdefgh\n"
        return result

    def blind_boundary_string(self, letter, number):
        result = " abcdefgh\n"
        for i in range(8):
            result += str(8 - i) + ""
            for j in range(8):
                if (letter - j)**2 + (number - 7 + i)**2 <= 2:
                    result += self.getchar(8*(7 - i) + j)
                else:
                    result += self.getblindchar(8*(7 - i) + j)
            result += "" + str(8 - i) + "\n"
        result += " abcdefgh\n"
        return result

    def __hash__(self):
        # noinspection PyProtectedMember
        return hash(self.board._transposition_key())


class ChessMove:
    def __init__(self, from_tile, to_tile, promote = 0):
        self.from_tile = from_tile
        self.to_tile = to_tile
        self.promote = promote
