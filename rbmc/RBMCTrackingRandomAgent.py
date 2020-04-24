#!/usr/bin/env python3

"""
File Name:      RBMCTrackingRandomAgent.py
Authors:        Sergey Savelyev
Date:           4/20/20

Description:    Python file for RBMC Tracking Random Agent.
Source:         Adapted from recon-chess (https://pypi.org/project/reconchess/)
"""

import chess
import numpy as np

from reconchess import Player, Color, GameHistory, WinReason, Square
from Information import LegalMove, IllegalMove, PiecePresentAt, consistent_with_all
from Information import SomethingMovedTo
from Information import ViewportInformation
from Information import NothingCaptured
from RandomPossibleGameGenerator import generate_possible_states
from Turn import generate_next_states_probs
from StateGeneratorNormal import generate_states_from_priors_pre_move, generate_states_from_priors
from rbmc.RBMCConstants import *
from collections import Counter
import random
# from rbmc.RBMCMCTS import *


class RBMCTrackingRandomAgent(Player):

    def __init__(self):
        self.input_beliefs = []
        self.tracking_beliefs = []
        self.info = []
        self.belief = Counter()
        self.color = None
        self.initialBoard = None
        self.noPreviousMoves = True
        self.belief_zero_count = 0
        self.turns = 0
        self.prev_prop = None
        self.scans = []
        self.moves = []
        self.random_mode = False

    def handle_game_start(self, color, board, opponent_name=None):
        """
        This function is called at the start of the game.

        :param color: chess.BLACK or chess.WHITE -- your color assignment for the game
        :param board: chess.Board -- initial board state
        :return:
        """
        self.color = color
        self.initialBoard = board
        self.belief = generate_possible_states(BELIEF_SIZE, [], max_attempts=1)
        self.tracking_beliefs.append(self.belief)
        if color == chess.BLACK:
            self.noPreviousMoves = False

    def handle_opponent_move_result(self, captured_piece, captured_square):
        """
        This function is called at the start of your turn and gives you the chance to update your board.

        :param captured_piece: bool - true if your opponents captured your piece with their last move
        :param captured_square: chess.Square - position where your piece was captured
        """
        if not self.noPreviousMoves and not self.random_mode:
            opponent_move = [SomethingMovedTo(captured_square)] if captured_piece else [NothingCaptured()]
            self.info.append(opponent_move)

            self.prev_prop = len(self.belief) <= 5

            if self.prev_prop:
                # Propagate moves 1 step forward
                self.belief = sum((Counter(d) for d in (generate_next_states_probs(state, amount, opponent_move)
                                                        for state, amount in self.belief.items())), Counter())

                self.belief += generate_states_from_priors_pre_move(self.tracking_beliefs, self.info, NOW_FRACTION,
                                                                    BELIEF_SIZE - sum(self.belief.values()),
                                                                    len(self.tracking_beliefs) - 1,
                                                                    len(self.info) - 1,
                                                                    max_attempts=RETRIES)

    def choose_sense(self, possible_sense, possible_moves, seconds_left):
        """
        This function is called to choose a square to perform a sense on.

        :param possible_sense: List(chess.SQUARES) -- list of squares to sense around
        :param possible_moves: List(chess.Moves) -- list of acceptable moves based on current board
        :param seconds_left: float -- seconds left in the game

        :return: chess.SQUARE -- the center of 3x3 section of the board you want to sense
        :example: choice = chess.A1
        """
        scan = random.choice(range(36))
        self.scans.append(np.ones(36) / 36)
        return chess.square(scan % 6 + 1, scan // 6 + 1)

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
        if not self.noPreviousMoves and not self.random_mode:
            # Add the information to our information list
            scan_viewport_info = ViewportInformation(dict(sense_result))
            self.info[-1].append(scan_viewport_info)

            if self.prev_prop:
                # Remove illegal states
                self.belief = Counter({state: amount for state, amount in self.belief.items() if
                                      scan_viewport_info.consistent_with(state, None)})
            else:
                # Propogate moves 1 step forward
                self.belief = sum(
                    (Counter(d) for d in (generate_next_states_probs(state, amount, self.info[-1]) for state, amount in
                                          self.belief.items())), Counter())

            if int(BELIEF_SIZE) - sum(self.belief.values()) > 0:
                self.belief += generate_states_from_priors_pre_move(self.tracking_beliefs, self.info, NOW_FRACTION,
                                                                    BELIEF_SIZE - sum(self.belief.values()),
                                                                    len(self.tracking_beliefs) - 1,
                                                                    len(self.info) - 1,
                                                                    max_attempts=RETRIES)

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
        self.input_beliefs.append(self.belief)
        print(self.color)
        all_possible_moves = set()
        for game, c in self.belief.items():
            all_possible_moves = all_possible_moves | set(game.getallmoves())
        for m in all_possible_moves:
            if m not in possible_moves:
                print(m)
        print()
        move = random.choice(possible_moves)
        self.moves.append({move: 1})
        return move

    def handle_move_result(self, requested_move, taken_move, captured_piece, captured_square, reason=None):
        """
        This is a function called at the end of your turn/after your move was made and gives you the chance to update
        your board.

        :param requested_move: chess.Move -- the move you intended to make
        :param taken_move: chess.Move -- the move that was actually made
        :param reason: String -- description of the result from trying to make requested_move
        :param captured_piece: bool - true if you captured your opponents piece
        :param captured_square: chess.Square - position where you captured the piece
        """
        if not self.random_mode:
            if not self.noPreviousMoves:
                added_beliefs = []
                if requested_move != taken_move:  # The requested move was illegal
                    added_beliefs.append(IllegalMove(requested_move))
                # The move that was taken is always legal
                added_beliefs.append(LegalMove(taken_move))
                if captured_piece:  # If we captured an opponent piece we now know a bit more
                    added_beliefs.append(PiecePresentAt(captured_square))
                self.info[-1].extend(added_beliefs)
                #self.info[-1].append(GameNotOver())
                self.belief = Counter({state.clone().applymove(taken_move): amount for state, amount in self.belief.items()
                                       if consistent_with_all(state, taken_move, added_beliefs)})
            else:
                self.noPreviousMoves = False
                self.belief = Counter({g.clone().applymove(taken_move): c for g, c in self.belief.items()})
            self.info.append(taken_move)
            self.belief += generate_states_from_priors(self.tracking_beliefs, self.info, NOW_FRACTION,
                                                       BELIEF_SIZE - sum(self.belief.values()),
                                                       len(self.tracking_beliefs) - 1,
                                                       len(self.info) - 1,
                                                       max_attempts=RETRIES)
        self.tracking_beliefs.append(self.belief)

    def handle_game_end(self, winner_color, win_reason, game_history):  # possible GameHistory object...
        """
        This function is called at the end of the game to declare a winner.

        :param game_history: 
        """
        return self.input_beliefs, self.moves, self.scans

