#!/usr/bin/env python3

"""
File Name:      my_agent.py
Authors:        Sergey Savelyev
Date:           4/1/19

Description:    Python file for my agent.
Source:         Adapted from recon-chess (https://pypi.org/project/reconchess/)
"""

import random
import chess
from player import Player

from collections import Counter

from ScanningChooser import heuristic_scan3x3_loc
from Versus import heuristic_move_selector
from Turn import material_heuristic
from RandomPossibleGameGenerator import generate_possible_states
from Information import SomethingMovedTo
from Information import ViewportInformation
from Turn import generate_next_states_probs
from StateGeneratorNormal import generate_states_from_priors_pre_move, update_prior_beliefs
from Information import LegalMove, IllegalMove, PiecePresentAt, consistent_with_all
from Turn import generate_states_from_priors
from ChessMonteCarloTreeSearch import *
from LeelaNetwork import LeelaNetwork
from net import Net
import tfprocess
import yaml
import chess
import tensorflow as tf


# TODO: Rename this class to what you would like your bot to be named during the game.
class MyAgent(Player):

    def __init__(self):
        super().__init__()  # Pycharm complains without this line
        self.belief_states = []
        self.info = []
        self.exploration = 1.4142135624
        self.temperature = 0.05
        self.iterations = 800
        self.now_fraction = 6 / 10
        self.retries = 10
        self.belief_size = 7500
        self.belief = Counter()
        self.color = None
        self.initialBoard = None
        self.noPreviousMoves = True
        self.region_selector = heuristic_scan3x3_loc
        #self.heursitic = material_heuristic
        #self.move_selector = lambda x: heuristic_move_selector(x, self.heursitic, self.iterations,
        #                                                       self.temperature, self.exploration)
        with open("leela_config.yml", "rb") as file:
            cfg = yaml.safe_load(file.read())

        net = Net()
        # net.parse_proto("weights_run1_42700.pb.gz")  # 2019-07-02 15:13:26 +00:00
        net.parse_proto("weights_run3_42872.pb.gz")  # 2019-09-09 03:25:41 +00:00

        filters, blocks = net.filters(), net.blocks()
        weights = net.get_weights()

        x = [
            tf.placeholder(tf.float32, [None, 112, 8 * 8]),
            tf.placeholder(tf.float32, [None, 1858]),
            tf.placeholder(tf.float32, [None, 3]),
            tf.placeholder(tf.float32, [None, 3]),
        ]

        tfp = tfprocess.TFProcess(cfg)
        tfp.init_net(x)
        tfp.replace_weights(weights)

        self.network = LeelaNetwork(tfp, x[0])
        self.prev_prop = False

    def handle_game_start(self, color, board):
        """
        This function is called at the start of the game.

        :param color: chess.BLACK or chess.WHITE -- your color assignment for the game
        :param board: chess.Board -- initial board state
        :return:
        """
        self.color = color
        self.initialBoard = board
        self.belief = generate_possible_states(self.belief_size, [], max_attempts=1)
        self.belief_states.append(self.belief)
        if color == chess.BLACK:
            self.noPreviousMoves = False
            #from Turn import material_heuristic

    def handle_opponent_move_result(self, captured_piece, captured_square):
        """
        This function is called at the start of your turn and gives you the chance to update your board.

        :param captured_piece: bool - true if your opponents captured your piece with their last move
        :param captured_square: chess.Square - position where your piece was captured
        """
        if not self.noPreviousMoves:
            opponent_move = [SomethingMovedTo(captured_square)] if captured_piece else []
            self.info.append(opponent_move)

            self.prev_prop = len(self.belief) <= 5

            if self.prev_prop:
                # Propagate moves 1 step forward
                from Turn import generate_states_from_priors_pre_move, generate_next_states_probs
                self.belief = sum((Counter(d) for d in (generate_next_states_probs(state, amount, opponent_move)
                                                        for state, amount in self.belief.items())), Counter())

                self.belief += generate_states_from_priors_pre_move(self.belief_states, self.info, self.now_fraction,
                                                                    self.belief_size - sum(self.belief.values()),
                                                                    len(self.belief_states) - 1,
                                                                    len(self.info) - 1,
                                                                    max_attempts=self.retries)

    def choose_sense(self, possible_sense, possible_moves, seconds_left):
        """
        This function is called to choose a square to perform a sense on.

        :param possible_sense: List(chess.SQUARES) -- list of squares to sense around
        :param possible_moves: List(chess.Moves) -- list of acceptable moves based on current board
        :param seconds_left: float -- seconds left in the game

        :return: chess.SQUARE -- the center of 3x3 section of the board you want to sense
        :example: choice = chess.A1
        """
        if self.noPreviousMoves:
            return possible_sense[0] # Don't care as the result will not have any effect
        else:
            # Select a region
            region_location = self.region_selector(self.belief)
            # Return the square at the center of this region
            # This should always be in the list of possible sensing locations
            return chess.square(region_location[0] + 1, region_location[1] + 1)

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

            if int(self.belief_size / 2) - sum(self.belief.values()) > 0:
                state_gens = generate_states_from_priors_pre_move(self.belief_states, self.info, self.now_fraction,
                                                                  int(self.belief_size / 2) - sum(self.belief.values()),
                                                                  len(self.belief_states) - 1,
                                                                  len(self.info) - 1,
                                                                  max_attempts=self.retries)
                self.belief += update_prior_beliefs(self.belief_states, state_gens, self.belief_size)

            # # Repopulate with legal states
            # from Turn import generate_states_from_priors_pre_move
            # self.belief += generate_states_from_priors_pre_move(self.belief_states, self.info, self.now_fraction,
            #                                                     self.belief_size - sum(self.belief.values()),
            #                                                     max_attempts=self.retries)

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
        print(str(seconds_left) + " seconds left, belief size: " + str(len(self.belief)))
        if len(self.belief) < 50:
            self.iterations = 400
        elif len(self.belief) < 250:
            self.iterations = 200
        elif len(self.belief) < 500:
            self.iterations = 100
        else:
            self.iterations = 50
        move_prob_sums = sum((Counter({n[0]: p*c for n, p in
                                           perform_search([s], self.iterations, self.temperature, self.exploration, self.network, None).items()})
                                  for s, c in self.belief.items() if c > 1), Counter())
        return pick_action(move_prob_sums)
        
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
        if not self.noPreviousMoves:
            added_beliefs = []
            if requested_move != taken_move:  # The requested move was illegal
                added_beliefs.append(IllegalMove(requested_move))
            # The move that was taken is always legal
                added_beliefs.append(LegalMove(taken_move))
            if captured_piece:  # If we captured an opponent piece we now know a bit more
                added_beliefs.append(PiecePresentAt(captured_square))
            self.info[-1].extend(added_beliefs)
            self.belief = Counter({state.clone().applymove(taken_move): amount for state, amount in self.belief.items()
                                   if consistent_with_all(state, None, added_beliefs)})
        else:
            self.noPreviousMoves = False
            self.belief = Counter({g.clone().applymove(taken_move): c for g, c in self.belief.items()})
        self.info.append(taken_move)
        self.belief += generate_states_from_priors(self.belief_states, self.info, self.now_fraction,
                                                   self.belief_size - sum(self.belief.values()),
                                                   len(self.belief_states) - 1,
                                                   len(self.info) - 1,
                                                   max_attempts=self.retries)
        self.belief_states.append(self.belief)
        
    def handle_game_end(self, winner_color, win_reason):  # possible GameHistory object...
        """
        This function is called at the end of the game to declare a winner.

        :param winner_color: Chess.BLACK/chess.WHITE -- the winning color
        :param win_reason: String -- the reason for the game ending
        """
        print("End of game")
