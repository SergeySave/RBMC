#!/usr/bin/env python3

"""
File Name:      random_agent.py
Authors:        Michael Johnson and Leng Ghuy
Date:           March 9th, 2019

Description:    Python file of a random bot
Source:         Adapted from recon-chess (https://pypi.org/project/reconchess/)
"""

import random
from reconchess import Player


class Random(Player):
        
    def handle_game_start(self, color, board, opponent_name):
        pass
        
    def handle_opponent_move_result(self, captured_piece, captured_square):
        pass

    def choose_sense(self, possible_sense, possible_moves, seconds_left):
        return random.choice(possible_sense)
        
    def handle_sense_result(self, sense_result):
        pass

    def choose_move(self, possible_moves, seconds_left):
        return random.choice(possible_moves)
        
    def handle_move_result(self, requested_move, taken_move, captured_piece, captured_square):
        pass
        
    def handle_game_end(self, winner_color, win_reason, game_history):
        pass
