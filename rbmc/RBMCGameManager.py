import os
import chess.pgn
import json
import io
from Chess import Chess
import random
from rbmc.RBMCNetwork import convert_states, convert_move_probs
import numpy as np
from rbmc.RBMCConstants import *
import glob
from collections import Counter
import pickle

class GameManager:

    def __init__(self, total_num_games, verbose=False):
        self.current_game = 0
        self.verbose = verbose

    def update_state(self, write=None):
        if write is None:
            if os.path.exists("output/rbmcgame/current.txt"):
                with open("output/rbmcgame/current.txt", 'r') as file:
                    self.current_game = int(file.readline())
        else:
            self.current_game = write
            with open("output/rbmcgame/current.txt", 'w') as file:
                    file.writelines([str(write)])

    def save_game(self, states, moves, result, scans, team):
        self.update_state()
        games = len(moves)
        start_game = self.current_game
        next_game = (start_game + games) % GAME_KEEP_NUM
        print("Saving game starting at " + str(start_game) + " until " + str(next_game))
        self.update_state(next_game)
        for i in range(games):
            move_probs = moves[i]
            scan_probs = scans[i]
            with open("output/rbmcgame/" + str((start_game + i) % GAME_KEEP_NUM) + ".rbmcgame", 'wb') as file:
                pickle.dump({
                    "beliefs": [({b.board.fen(): c for b, c in states[j].items()} if i + 1 - j < 8 else {}) for j in range(i+1)],
                    "move_probs": {m.uci(): p for m, p in move_probs.items()},
                    "result": result,
                    "scan_probs": {i: scan_probs[i].astype(float) for i in range(len(scan_probs))},
                    "team": team
                }, file)

    def read_game(self, path):
        with open(path, 'rb') as file:
            game = pickle.load(file)

            def play_out_game(fen):
                return Chess(chess.Board(fen))

            states = [Counter({play_out_game(fen): c for fen, c in b.items()}) for b in game["beliefs"]]
            return states,\
                {chess.Move.from_uci(uci): p for uci, p in game["move_probs"].items()},\
                game["result"],\
                {t: p for t, p in game["scan_probs"].items()}

    def sample_moves(self, num_samples):
        self.update_state()
        inputs = []
        move_outs = []
        result_outs = []
        scan_outs = []

        sample = random.choices(glob.glob("output/rbmcgame/*.rbmcgame"), k=num_samples)
        for path in sample:
            i, m_o, r_o, s_o = self.read_game(path)
            inputs.append(convert_states(i))
            move_outs.append(convert_move_probs(m_o, False))
            result_outs.append(r_o)
            scan_outs.append(np.array([s_o[i] for i in range(36)]))

        return np.array(inputs), np.array(move_outs), np.array(result_outs), np.array(scan_outs)
