import os
import chess.pgn
import json
import io
from Chess import Chess
import random
from Network import convert_states, convert_move_probs
import numpy as np


class GameManager:

    def __init__(self, total_num_games, verbose=False):
        self.current_game = 0
        self.game_lengths_strs = []
        self.total_num_games = total_num_games
        self.verbose = verbose
        self.exporter = chess.pgn.StringExporter(headers=False, comments=False, variations=False)

    def update_state(self):
        if os.path.exists("output/game/current.txt"):
            with open("output/game/current.txt", 'r') as file:
                lines = file.readlines()
                fixed = [x[:-1] for x in lines]
                self.current_game = int(fixed[0])
                self.game_lengths_strs = fixed[1:-1] + [lines[-1]]

    def save_next_game(self, states, moves, result):
        self.update_state()  # Ensure we know how many games there are
        print("Saving game " + str(self.current_game))
        with open("output/game/" + str(self.current_game) + ".json", 'w') as file:
            json.dump({"game": chess.pgn.Game.from_board(states[-1].board).accept(self.exporter),
                       "move_probs": [{move.uci(): prob for (move, prob) in probs.items()} for probs in moves],
                       "result": result}, file, indent=4)
        while len(self.game_lengths_strs) <= self.current_game:
            self.game_lengths_strs.append(0)
        self.game_lengths_strs[self.current_game] = str(len(moves))
        self.current_game += 1
        if self.current_game >= self.total_num_games:  # Keep cycling games 0 through total_num_games
            self.current_game = 0
        with open("output/game/current.txt", 'w') as file:  # Save the state
            state = "\n".join([str(self.current_game)] + [x for x in self.game_lengths_strs])
            file.writelines(state)

    @staticmethod
    def load_game(game_num):
        with open("output/game/" + str(game_num) + ".json", 'r') as file:
            game_read = json.load(file)

        game = chess.pgn.read_game(io.StringIO(game_read['game']))
        state = Chess()
        states = []
        for move in game.mainline_moves():
            states.append(state.clone())
            state.applymove(move)
        states.append(state)
        moves = [{chess.Move.from_uci(uci): prob for (uci, prob) in probs.items()} for probs in game_read['move_probs']]
        result = game_read['result']
        return states, moves, result

    def get_samples(self, sampled):
        inputs = []
        move_outs = []
        result_outs = []
        move_count = 0
        sample_index = 0
        for i in range(self.total_num_games):
            move_count += int(self.game_lengths_strs[i])
            if sampled[sample_index] < move_count:
                old_move_count = move_count - int(self.game_lengths_strs[i])
                states, moves, result = self.load_game(i)
                while sampled[sample_index] < move_count:
                    index = sampled[sample_index] - old_move_count  # get the index within this game
                    state = convert_states(states[0:(index + 1)])
                    move = convert_move_probs(moves[index], index % 2 == 1)
                    inputs.append(state)
                    move_outs.append(move)
                    result_outs.append(result)
                    sample_index += 1
                    if sample_index >= len(sampled):
                        return np.array(inputs), np.array(move_outs), np.array(result_outs)
        return np.array(inputs), np.array(move_outs), np.array(result_outs)

    def sample_moves(self, num_samples):
        self.update_state()
        total_moves = sum([int(x) for x in self.game_lengths_strs])
        sampled = random.sample(range(total_moves), num_samples)
        sampled.sort()  # Sorting makes it easier to retrieve the samples
        inputs, move_outs, result_outs = self.get_samples(sampled)
        shuffle = np.random.permutation(num_samples)
        return inputs[shuffle], move_outs[shuffle], result_outs[shuffle]
