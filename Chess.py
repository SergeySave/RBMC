
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
TYPES = ['♚', '♛', '♝', '♞', '♜', '♟', '⬚', '♙', '♖', '♘', '♗', '♕', '♔']
DIRECTIONS = [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]


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
        plane = int(move / (8*8))
        tile = move % (8*8)
        row = _getrow(tile)
        if self.currentPlayer > 0:
            row = 7 - row
        col = _getcol(tile)

        target = self.get_move_target(move)
        # If something changes with the rooks then castling becomes invalid
        if target == _gettile(0, 0):
            self.blackCastleQS = False
        elif target == _gettile(0, 7):
            self.blackCastleKS = False
        elif target == _gettile(7, 0):
            self.whiteCastleQS = False
        elif target == _gettile(7, 7):
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

        if 0 <= plane < 56:  # queen-like movement planes
            length = (plane % 7) + 1  # lengths 1-7
            direction = int(plane / 7)  # directions 0-7
            dir_coords = DIRECTIONS[direction]
            desired_row = row + dir_coords[0] * length
            desired_col = col + dir_coords[1] * length
            if 0 <= desired_row <= 7 and 0 <= desired_col <= 7:  # Make sure the desired tile is on the board
                desired_tile = _getsmarttile(desired_row, desired_col, -self.currentPlayer)
                if abs(piece) == PAWN or abs(piece) == ROOK or \
                        abs(piece) == BISHOP or abs(piece) == QUEEN:
                    if abs(piece) == PAWN and desired_row == 7:
                        self.state[desired_tile] = self.currentPlayer * -QUEEN
                    else:
                        self.state[desired_tile] = piece
                if abs(piece) == KING:
                    if self.currentPlayer == -1:  # Negated because current player was
                        self.whiteCastleKS = False
                        self.whiteCastleQS = False
                    if self.currentPlayer == 1:
                        self.blackCastleKS = False
                        self.blackCastleQS = False
                    if length == 1:  # Normal King move
                        self.state[desired_tile] = piece
                    else:  # Castling move
                        self.state[desired_tile] = piece
                        self.state[(tile + desired_tile)/2] = ROOK
                        if direction == 0:
                            self.state[_getsmarttile(0, 7, -self.currentPlayer)] = 0
                        if direction == 4:
                            self.state[_getsmarttile(0, 0, -self.currentPlayer)] = 0
        elif 56 <= plane < 64:  # knight movement planes
            direction = plane - 56
            move = KNIGHT_MOVES[direction]
            desired_row = row + move[0]
            desired_col = col + move[1]
            desired_tile = _getsmarttile(desired_row, desired_col, -self.currentPlayer)
            self.state[desired_tile] = piece
        else: # pawn underpromotion planes
            if 64 <= plane < 67:  # pawn underpromotion left attack planes
                self.state[_getsmarttile(row + 1, col - 1, -self.currentPlayer)] = \
                    (plane - 64 + ROOK) * -self.currentPlayer  # Set it to the promoted piece
            elif 67 <= plane < 70:  # pawn underpromotion forward planes
                self.state[_getsmarttile(row + 1, col, -self.currentPlayer)] = \
                    (plane - 67 + ROOK) * -self.currentPlayer  # Set it to the promoted piece
            elif 70 <= plane < 73:  # pawn underpromotion right attack planes
                self.state[_getsmarttile(row + 1, col + 1, -self.currentPlayer)] = \
                    (plane - 70 + ROOK) * -self.currentPlayer  # Set it to the promoted piece

    def get_move_target(self, move):
        plane = int(move / (8*8))
        tile = move % (8*8)
        row = _getrow(tile)
        if self.currentPlayer > 0:
            row = 7 - row
        col = _getcol(tile)

        if 0 <= plane < 56:  # queen-like movement planes
            length = (plane % 7) + 1  # lengths 1-7
            direction = int(plane / 7)  # directions 0-7
            dir_coords = DIRECTIONS[direction]
            desired_row = row + dir_coords[0] * length
            desired_col = col + dir_coords[1] * length
            if 0 <= desired_row <= 7 and 0 <= desired_col <= 7:  # Make sure the desired tile is on the board
                return _getsmarttile(desired_row, desired_col, self.currentPlayer)
        elif 56 <= plane < 64:  # knight movement planes
            direction = plane - 56
            move = KNIGHT_MOVES[direction]
            desired_row = row + move[0]
            desired_col = col + move[1]
            return _getsmarttile(desired_row, desired_col, self.currentPlayer)
        else: # pawn underpromotion planes
            if 64 <= plane < 67:  # pawn underpromotion left attack planes
                return _getsmarttile(row + 1, col - 1, self.currentPlayer)
            elif 67 <= plane < 70:  # pawn underpromotion forward planes
                return _getsmarttile(row + 1, col, self.currentPlayer)
            elif 70 <= plane < 73:  # pawn underpromotion right attack planes
                return _getsmarttile(row + 1, col + 1, self.currentPlayer)

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

    def isbaselegal(self, move, doCastlingCheck = True):
        plane = int(move / (8*8))
        tile = move % (8*8)
        row = _getrow(tile)
        if self.currentPlayer > 0:
            row = 7 - row
        col = _getcol(tile)

        if self.state[tile] * self.currentPlayer <= 0:  # Make sure it's the current player's piece
            return False
        if 0 <= plane < 56:  # queen-like movement planes
            length = (plane % 7) + 1  # lengths 1-7
            direction = int(plane / 7)  # directions 0-7
            if self.gettype(tile) == ROOK and direction in [1, 3, 5, 7]:
                return False  # Invalid directions for the rook
            if self.gettype(tile) == BISHOP and direction in [0, 2, 4, 6]:
                return False  # Invalid directions for the bishop
            if self.gettype(tile) == KING and (not (length == 1 or (length == 2 and direction in [0, 4]))):
                return False  # Invalid length for the king
            if self.gettype(tile) == KNIGHT:
                return False  # Knights cannot use the queen planes
            if self.gettype(tile) == PAWN and (length != 1 or direction in [0, 4, 5, 6, 7]):
                return False  # Invalid length for the path
            dir_coords = DIRECTIONS[direction]
            desired_row = row + dir_coords[0] * length
            desired_col = col + dir_coords[1] * length
            if 0 <= desired_row <= 7 and 0 <= desired_col <= 7:  # Make sure the desired tile is on the board
                desired_tile = _getsmarttile(desired_row, desired_col, self.currentPlayer)
                if self.gettype(tile) == PAWN:
                    if direction == 2:
                        return self.state[desired_tile] == 0
                    if direction == 1 or direction == 3:
                        return self.state[desired_tile] * self.currentPlayer < 0
                if self.gettype(tile) == ROOK or self.gettype(tile) == BISHOP or self.gettype(tile) == QUEEN:
                    for i in range(1, length):  # Make sure central tiles are empty
                        curr_row = row + dir_coords[0] * i
                        curr_col = col + dir_coords[1] * i
                        curr_tile = _getsmarttile(curr_row, curr_col, self.currentPlayer)
                        return self.state[curr_tile] == 0
                    return self.state[desired_tile] * self.currentPlayer <= 0  # Make sure final tile is empty or enemy
                if self.gettype(tile) == KING:
                    if length == 1:  # Normal King move
                        return self.state[desired_tile] * self.currentPlayer <= 0
                    elif doCastlingCheck:  # Castling move
                        # Make sure it is still legal
                        if self.currentPlayer == 1:
                            if direction == 0 and not self.whiteCastleKS:
                                return False
                            if direction == 4 and not self.whiteCastleQS:
                                return False
                        if self.currentPlayer == -1:
                            if direction == 0 and not self.blackCastleKS:
                                return False
                            if direction == 4 and not self.blackCastleQS:
                                return False
                        # As the tiles are on the same row taking the average of the tile and desired tile gets the
                        # tile in between the two
                        return (not self.is_tile_under_attack(tile)) and (not self.is_tile_under_attack((tile + desired_tile) / 2)) and \
                               self.state[desired_tile] == 0 and self.state[(tile + desired_tile)/2] == 0

            return False
        elif 56 <= plane < 64:  # knight movement planes
            if self.gettype(tile) != KNIGHT:  # Only knights can use the knight planes
                return False
            direction = plane - 56
            move = KNIGHT_MOVES[direction]
            desired_row = row + move[0]
            desired_col = col + move[1]
            if 0 <= desired_row <= 7 and 0 <= desired_col <= 7:  # Make sure the desired tile is on the board
                desired_tile = _getsmarttile(desired_row, desired_col, self.currentPlayer)
                return self.state[desired_tile] * self.currentPlayer <= 0  # make sure it's not your player's piece
            else:
                return False
        else: # pawn underpromotion planes
            if self.gettype(tile) != PAWN or row != 6:  # Only pawns at row 6 can use the underpromotion planes
                return False
            if 64 <= plane < 67:  # pawn underpromotion left attack planes
                # make sure that the tile is on the board and has an opponent piece 
                return col > 0 and \
                       self.state[_getsmarttile(row + 1, col - 1, self.currentPlayer)] * self.currentPlayer < 0
            elif 67 <= plane < 70:  # pawn underpromotion forward planes
                # make sure the tile is empty
                return self.state[_getsmarttile(row + 1, col, self.currentPlayer)] * self.currentPlayer == 0
            elif 70 <= plane < 73:  # pawn underpromotion right attack planes
                # make sure that the tile is on the board and has an opponent piece
                return col < 7 and \
                       self.state[_getsmarttile(row + 1, col + 1, self.currentPlayer)] * self.currentPlayer < 0

    def getallmoves(self):
        # If the game is over then there are no more moves
        if self.getboardstate(1) != 0.5:
            return []
        return [i for i in range(8*8*73) if self.islegal(i)]

    def getallbasemoves(self):
        # If the game is over then there are no more moves
        if self.getboardstate(1) != 0.5:
            return []
        return [i for i in range(8*8*73) if self.isbaselegal(i, False)]

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
    def __init__(self, fromTile, toTile):
        self.fromTile = fromTile
        self.toTile = toTile