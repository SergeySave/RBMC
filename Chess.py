
def _getrow(tile):
    return int(tile / 8)


def _getcol(tile):
    return tile % 8


def _gettile(row, col):
    return 8 * row + col


def _getsmarttile(row, col, team):
    if team > 0:
        return 8 * (7 - row) + col
    return 8 * row + col


PAWN = 1
ROOK = 2
KNIGHT = 3
BISHOP = 4
QUEEN = 5
KING = 6


KNIGHT_MOVES = [[1, 2], [2, 1], [2, -1], [1, -2], [-1, -2], [-2, -1], [-2, 1], [-1, 2]]
TYPES = ['♚', '♛', '♝', '♞', '♜', '♟', ' ', '♙', '♖', '♘', '♗', '♕', '♔']
DIRECTIONS = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]


cache = {}


# Moves are encoded the same way as they  are in the AlphaGoZero paper
class Chess:
    def __init__(self):
        self.currentPlayer = 1
        self.whiteCastleKS = True
        self.whiteCastleQS = True
        self.blackCastleKS = True
        self.blackCastleQS = True
        self.state = [-ROOK, -KNIGHT, -BISHOP, -QUEEN, -KING, -BISHOP, -KNIGHT, -ROOK,  # row = 7
                      -PAWN, -PAWN, -PAWN, -PAWN, -PAWN, -PAWN, -PAWN, -PAWN,
                      0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0,
                      PAWN, PAWN, PAWN, PAWN, PAWN, PAWN, PAWN, PAWN,
                      ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK]  # row = 0
        self.basemoves = None

    def clone(self):
        clone = Chess()
        clone.currentPlayer = self.currentPlayer
        clone.whiteCastleKS = self.whiteCastleKS
        clone.whiteCastleQS = self.whiteCastleQS
        clone.blackCastleKS = self.blackCastleKS
        clone.blackCastleQS = self.blackCastleQS
        clone.state = self.state[:]
        return clone

    # Assumes that the move is legal
    def applymove(self, move):
        desired_tile = move.toTile
        desired_row = _getrow(desired_tile)
        desired_col = _getcol(desired_tile)
        if not (0 <= desired_col <= 7 and 0 <= desired_row <= 7):
            return False

        tile = move.fromTile
        row = _getrow(tile)
        col = _getcol(tile)

        if self.currentPlayer > 0:
            row = 7 - row
            desired_row = 7 - desired_row

        # If something changes with the rooks then castling becomes invalid
        if desired_tile == _gettile(0, 0):
            self.blackCastleQS = False
        elif desired_tile == _gettile(0, 7):
            self.blackCastleKS = False
        elif desired_tile == _gettile(7, 0):
            self.whiteCastleQS = False
        elif desired_tile == _gettile(7, 7):
            self.whiteCastleKS = False
        if tile == _gettile(0, 0):
            self.blackCastleQS = False
        elif tile == _gettile(0, 7):
            self.blackCastleKS = False
        elif tile == _gettile(7, 0):
            self.whiteCastleQS = False
        elif tile == _gettile(7, 7):
            self.whiteCastleKS = False

        self.currentPlayer = -self.currentPlayer
        piece = self.state[tile]
        self.state[tile] = 0  # Remove the piece

        if abs(piece) == KING:
            if self.currentPlayer == -1:
                self.whiteCastleKS = False
                self.whiteCastleQS = False
            elif self.currentPlayer == 1:
                self.blackCastleKS = False
                self.blackCastleQS = False

        self.state[desired_tile] = piece if move.promote == 0 else move.promote

    def get_move_target(self, move):
        desired_tile = move.toTile
        return desired_tile

    def is_tile_under_attack(self, tile):
        basemoves = self.getallbasemoves()
        for move in basemoves:
            if self.get_move_target(move) == tile:
                return True
        return False

    def findfirstunit(self, unit):
        try:
            return self.state.index(unit)
        except ValueError:
            return None

    def islegal(self, move):
        islegal = self.isbaselegal(move)
        if islegal:
            newone = self.clone()
            newone.applymove(move)
            first_unit = newone.findfirstunit(KING * self.currentPlayer)
            if first_unit is None:
                return False
            return not newone.is_tile_under_attack(first_unit)
        return False

    def isbaselegal(self, move, do_castling_check = True):
        desired_tile = move.toTile
        desired_row = _getrow(desired_tile)
        desired_col = _getcol(desired_tile)
        if not (0 <= desired_col <= 7 and 0 <= desired_row <= 7):
            return False

        tile = move.fromTile
        row = _getrow(tile)
        col = _getcol(tile)

        if self.currentPlayer > 0:
            row = 7 - row
            desired_row = 7 - desired_row

        if self.state[tile] * self.currentPlayer <= 0:  # Make sure it's the current player's piece
            return False

        piece_type = self.gettype(tile)
        if piece_type == PAWN:
            if self.state[desired_tile] == 0:
                if desired_col == col:
                    if row == 1 and (desired_row == 2 or desired_row == 3):
                        return True
                    if (desired_row - row) == 1:
                        return True
                return False
            elif abs(desired_col - col) == 1 and desired_row - row == 1:
                return True
            return False
        elif piece_type == ROOK:
            if row == desired_row:  # Vertical movement
                direction = 1 if desired_col > col else -1
                for i in range(1, abs(desired_col-col)):
                    mid_tile = _getsmarttile(row, col + i * direction, self.currentPlayer)
                    if self.state[mid_tile] != 0:
                        return False
                return self.state[_getsmarttile(row, desired_col, self.currentPlayer)] * self.currentPlayer <= 0
            elif col == desired_col:  # Horizontal movement
                direction = 1 if desired_row > row else -1
                for i in range(1, abs(desired_row-row)):
                    mid_tile = _getsmarttile(row + i * direction, col, self.currentPlayer)
                    if self.state[mid_tile] != 0:
                        return False
                return self.state[_getsmarttile(desired_row, col, self.currentPlayer)] * self.currentPlayer <= 0
            return False
        elif piece_type == KNIGHT:
            dr = desired_row - row
            dc = desired_col - col
            return (dr * dr + dc * dc) == 5 and \
                self.state[_getsmarttile(desired_row, desired_col, self.currentPlayer)] * self.currentPlayer <= 0
        elif piece_type == BISHOP:
            dr = desired_row - row
            dc = desired_col - col
            if dr == dc:  # Positive slope movement
                direction = 1 if dr > 0 else -1
                for i in range(1, abs(dr)):
                    mid_tile = _getsmarttile(row + i * direction, col + i * direction, self.currentPlayer)
                    if self.state[mid_tile] != 0:
                        return False
                return self.state[_getsmarttile(desired_row, desired_col, self.currentPlayer)] * self.currentPlayer <= 0
            elif dr == -dc:  # Negative slope movement
                direction = 1 if dr > 0 else -1
                for i in range(1, abs(dr)):
                    mid_tile = _getsmarttile(row + i * direction, col - i * direction, self.currentPlayer)
                    if self.state[mid_tile] != 0:
                        return False
                return self.state[_getsmarttile(desired_row, desired_col, self.currentPlayer)] * self.currentPlayer <= 0
            return False
        elif piece_type == QUEEN:
            if row == desired_row:  # Vertical movement
                direction = 1 if desired_col > col else -1
                for i in range(1, abs(desired_col-col)):
                    mid_tile = _getsmarttile(row, col + i * direction, self.currentPlayer)
                    if self.state[mid_tile] != 0:
                        return False
                return self.state[_getsmarttile(row, desired_col, self.currentPlayer)] * self.currentPlayer <= 0
            elif col == desired_col:  # Horizontal movement
                direction = 1 if desired_row > row else -1
                for i in range(1, abs(desired_row-row)):
                    mid_tile = _getsmarttile(row + i * direction, col, self.currentPlayer)
                    if self.state[mid_tile] != 0:
                        return False
                return self.state[_getsmarttile(desired_row, col, self.currentPlayer)] * self.currentPlayer <= 0
            dr = desired_row - row
            dc = desired_col - col
            if dr == dc:  # Positive slope movement
                direction = 1 if dr > 0 else -1
                for i in range(1, abs(dr)):
                    mid_tile = _getsmarttile(row + i * direction, col + i * direction, self.currentPlayer)
                    if self.state[mid_tile] != 0:
                        return False
                return self.state[_getsmarttile(desired_row, desired_col, self.currentPlayer)] * self.currentPlayer <= 0
            elif dr == -dc:  # Negative slope movement
                direction = 1 if dr > 0 else -1
                for i in range(1, abs(dr)):
                    mid_tile = _getsmarttile(row + i * direction, col - i * direction, self.currentPlayer)
                    if self.state[mid_tile] != 0:
                        return False
                return self.state[_getsmarttile(desired_row, desired_col, self.currentPlayer)] * self.currentPlayer <= 0
            return False
        elif piece_type == KING:
            dr = desired_row - row
            dc = desired_col - col
            if (dr * dr + dc * dc) <= 2:
                return self.state[_getsmarttile(desired_row, desired_col, self.currentPlayer)] * self.currentPlayer <= 0
            if not do_castling_check:
                return False
            if self.currentPlayer == 1:
                if dc > 0 and not self.whiteCastleKS:
                    return False
                if dc < 0 and not self.whiteCastleQS:
                    return False
            if self.currentPlayer == -1:
                if dc > 0 and not self.blackCastleKS:
                    return False
                if dc < 0 and not self.blackCastleQS:
                    return False
            # As the tiles are on the same row taking the average of the tile and desired tile gets the
            # tile in between the two
            return (not self.is_tile_under_attack(tile)) and (not self.is_tile_under_attack((tile + desired_tile) / 2))\
                and self.state[desired_tile] == 0 and self.state[(tile + desired_tile) / 2] == 0

    def getallmoves(self):
        # If the game is over then there are no more moves
        if self.getboardstate(1) != 0.5:
            return []
        moves = []
        for i in range(64):
            moves.extend([move for move in self.possible_moves(i) if self.islegal(move)])
        return moves

    def getallbasemoves(self):
        # If the game is over then there are no more moves
        if self.basemoves is not None:
            return self.basemoves
        if self.getboardstate(1) != 0.5:
            self.basemoves = []
            return self.basemoves
        moves = []
        for i in range(64):
            moves.extend([move for move in self.possible_moves(i) if self.isbaselegal(move, False)])
        self.basemoves = moves
        return self.basemoves

    def possible_moves(self, tile):
        row = _getrow(tile)
        col = _getcol(tile)
        if self.currentPlayer > 0:
            row = 7 - row
        piece_type = self.gettype(tile)

        if tile in cache:
            if piece_type in cache[tile]:
                if self.currentPlayer in cache[tile][piece_type]:
                    return cache[tile][piece_type][self.currentPlayer]

        moves = []
        if piece_type == PAWN:
            if row < 6:
                moves.append(ChessMove(tile, _getsmarttile(row + 1, col, self.currentPlayer)))
                moves.append(ChessMove(tile, _getsmarttile(row + 1, col - 1, self.currentPlayer)))
                moves.append(ChessMove(tile, _getsmarttile(row + 1, col + 1, self.currentPlayer)))
                moves.append(ChessMove(tile, _getsmarttile(row + 2, col, self.currentPlayer)))
            else:
                for i in range(2, 6):
                    moves.append(ChessMove(tile, _getsmarttile(row + 1, col, self.currentPlayer), i))
                    moves.append(ChessMove(tile, _getsmarttile(row + 1, col - 1, self.currentPlayer), i))
                    moves.append(ChessMove(tile, _getsmarttile(row + 1, col + 1, self.currentPlayer), i))
        elif piece_type == ROOK:
            for i in range(8):
                if i != row:
                    moves.append(ChessMove(tile, _getsmarttile(i, col, self.currentPlayer)))
                if i != col:
                    moves.append(ChessMove(tile, _getsmarttile(row, i, self.currentPlayer)))
        elif piece_type == KNIGHT:
            moves.append(ChessMove(tile, _getsmarttile(row + 1, col + 2, self.currentPlayer)))
            moves.append(ChessMove(tile, _getsmarttile(row + 1, col - 2, self.currentPlayer)))
            moves.append(ChessMove(tile, _getsmarttile(row - 1, col + 2, self.currentPlayer)))
            moves.append(ChessMove(tile, _getsmarttile(row - 1, col - 2, self.currentPlayer)))
            moves.append(ChessMove(tile, _getsmarttile(row + 2, col + 1, self.currentPlayer)))
            moves.append(ChessMove(tile, _getsmarttile(row + 2, col - 1, self.currentPlayer)))
            moves.append(ChessMove(tile, _getsmarttile(row - 2, col + 1, self.currentPlayer)))
            moves.append(ChessMove(tile, _getsmarttile(row - 2, col - 1, self.currentPlayer)))
        elif piece_type == BISHOP:
            for i in range(8):
                row1 = row - col + i
                row2 = row + col - i
                col_spot = col + i
                if col != col_spot:
                    if 0 <= row1 <= 7:
                        moves.append(ChessMove(tile, _getsmarttile(row1, col_spot, self.currentPlayer)))
                    if 0 <= row2 <= 7:
                        moves.append(ChessMove(tile, _getsmarttile(row2, col_spot, self.currentPlayer)))
        elif piece_type == QUEEN:
            for i in range(8):
                if i != row:
                    moves.append(ChessMove(tile, _getsmarttile(i, col, self.currentPlayer)))
                if i != col:
                    moves.append(ChessMove(tile, _getsmarttile(row, i, self.currentPlayer)))
                row1 = row - col + i
                row2 = row + col - i
                col_spot = col + i
                if col != col_spot:
                    if 0 <= row1 <= 7:
                        moves.append(ChessMove(tile, _getsmarttile(row1, col_spot, self.currentPlayer)))
                    if 0 <= row2 <= 7:
                        moves.append(ChessMove(tile, _getsmarttile(row2, col_spot, self.currentPlayer)))
        elif piece_type == KING:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i != 0 or j != 0:
                        moves.append(ChessMove(tile, _getsmarttile(row + i, col + j, self.currentPlayer)))
        if tile not in cache:
            cache[tile] = {}
        if piece_type not in cache[tile]:
            cache[tile][piece_type] = {}
        if self.currentPlayer not in cache[tile][piece_type]:
            cache[tile][piece_type][self.currentPlayer] = moves
        return moves

    def getboardstate(self, player):
        curr_king = self.findfirstunit(KING * player)
        enemy_king = self.findfirstunit(KING * -player)
        if curr_king is None:
            return 0.0
        if enemy_king is None:
            return 1.0
        return 0.5

    def isgameover(self):
        return self.getallmoves() == []

    def gettype(self, tile):
        return abs(self.state[tile])

    def getchar(self, tile):
        return TYPES[self.state[tile] + 6]

    def tostring(self):
        result = ""
        for i in range(8):
            for j in range(8):
                result += self.getchar(8*i + j)
            result += "\n"
        return result


class ChessMove:
    def __init__(self, fromTile, toTile, promote = 0):
        self.fromTile = fromTile
        self.toTile = toTile
        self.promote = promote