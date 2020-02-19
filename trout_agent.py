#!/usr/bin/env python3

"""
File Name:      trout_agent.py
Authors:        Sergey Savelyev
Date:           1/21/20

Description:    Python file for Trout agent.
Source:         Adapted from recon-chess (https://pypi.org/project/reconchess/)
"""

import random
import chess
from player import Player

import chess.engine
import string
from Chess import Chess

class TroutAgent(Player):

    def create_engine(self):
        self.engine = chess.engine.SimpleEngine.popen_uci("./stockfish")

    def __init__(self):
        super().__init__()  # Pycharm complains without this line
        self.create_engine()

    def handle_game_start(self, color, board):
        """
        This function is called at the start of the game.

        :param color: chess.BLACK or chess.WHITE -- your color assignment for the game
        :param board: chess.Board -- initial board state
        :return:
        """
        self.color = color
        self.board = board
        self.scan_next = None
        if color == chess.BLACK:
            self.noPreviousMoves = False
        else:
            self.noPreviousMoves = True

    def handle_opponent_move_result(self, captured_piece, captured_square):
        """
        This function is called at the start of your turn and gives you the chance to update your board.

        :param captured_piece: bool - true if your opponents captured your piece with their last move
        :param captured_square: chess.Square - position where your piece was captured
        """
        if not self.noPreviousMoves:
            if captured_piece:
                self.scan_next = captured_square
            self.board.push(chess.Move.null())
            print(Chess(self.board).tostring())
            checking = self.board.is_check()
            self.board.pop()
            print(self.board.is_checkmate())
            if checking:
                self.scan_next = self.board.king(chess.WHITE if self.color == chess.BLACK else chess.BLACK)

    def choose_sense(self, possible_sense, possible_moves, seconds_left):
        """
        This function is called to choose a square to perform a sense on.

        :param possible_sense: List(chess.SQUARES) -- list of squares to sense around
        :param possible_moves: List(chess.Moves) -- list of acceptable moves based on current board
        :param seconds_left: float -- seconds left in the game

        :return: chess.SQUARE -- the center of 3x3 section of the board you want to sense
        :example: choice = chess.A1
        """
        if self.scan_next is not None:
            nex = self.scan_next
            self.scan_next = None
            return nex
        choices = [square for square in chess.SQUARES if self.board.piece_type_at(square) is None]
        if len(choices) == 0:
            return random.choice(possible_sense)
        return random.choice(choices)

    def handle_sense_result(self, sense_result):
        """
        This is a function called after your picked your 3x3 square to sense and gives you the chance to update your
        board.

        :param sense_result: A list of tuples, where each tuple contains a :class:`Square` in the sense, and if there
                             was a piece on the square, then the corresponding :class:`chess.Piece`, otherwise `None`.
        :example:
        [
            (A8, Piece(ROOK, BLACK)), (B8, Piece(KNIGHT, BLACK)), (C8, Piece(BISHOP, BLACK)),
            (A7, Piece(PAWN, BLACK)), (B7, Piece(PAWN, BLACK)), (C7, Piece(PAWN, BLACK)),
            (A6, None), (B6, None), (C8, None)
        ]
        """
        if not self.noPreviousMoves:
            self.board.push(chess.Move.null())
            for entry in sense_result:   
                self.board.set_piece_at(entry[0], entry[1])
            # Check if the king is now missing
            # Place the king at a random spot?

    def choose_move(self, possible_moves, seconds_left):
        """
        Choose a move to enact from a list of possible moves.

        :param possible_moves: List(chess.Moves) -- list of acceptable moves based only on pieces
        :param seconds_left: float -- seconds left to make a move
        
        :return: chess.Move -- object that includes the square you're moving from to the square you're moving to
        :example: choice = chess.Move(chess.F2, chess.F4)
        
        :condition: If you intend to move a pawn for promotion other than Queen, please specify the promotion parameter
        :example: choice = chess.Move(chess.G7, chess.G8, promotion=chess.KNIGHT) *default is Queen
        """
        try:
            return self.engine.play(self.board, chess.engine.Limit(white_clock=seconds_left, black_clock=seconds_left), game=''.join(random.choice(string.ascii_lowercase) for i in range(16))).move
        except:
            target = self.board.king(chess.WHITE if self.color == chess.BLACK else chess.BLACK)
            winning_moves = [move for move in self.board.legal_moves if move.to_square == target]
            print(winning_moves)
            return winning_moves[0]
        
    def handle_move_result(self, requested_move, taken_move, captured_piece, captured_square, reason):
        """
        This is a function called at the end of your turn/after your move was made and gives you the chance to update
        your board.

        :param requested_move: chess.Move -- the move you intended to make
        :param taken_move: chess.Move -- the move that was actually made
        :param reason: String -- description of the result from trying to make requested_move
        :param captured_piece: bool - true if you captured your opponents piece
        :param captured_square: chess.Square - position where you captured the piece
        """
        self.noPreviousMoves = False
        if taken_move is None:
            self.scan_next = requested_move.to_square
        self.board.push(taken_move if taken_move is not None else chess.Move.null())
        
    def handle_game_end(self, a, b):  # possible GameHistory object...
        """
        This function is called at the end of the game to declare a winner.
        """
        print("Game Over!")

