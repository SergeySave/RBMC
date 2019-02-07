from Chess import Chess
from Network import load_network, convert_states, convert_move_probs, N, M, T, L
import json
import chess.pgn
import io
import numpy as np
import os


def train_network_from_games(training_network, num_games, epochs):
    inputs = []
    move_labels = []
    value_labels = []

    for i in range(num_games):
        if os.path.exists("output/" + str(i) + ".json"):
            print("Loading game " + str(i))
            states, moves, result = read_game_from_file('output/' + str(i) + '.json')
            for j in range(len(states)):
                inputs.append(convert_states(states[0:(j+1)]))
                move_labels.append(convert_move_probs(moves[j], j % 2 == 1))
                value_labels.append(result)

    training_network.model.optimizer.lr.assign(0.001)
    training_network.model.fit(x=np.array(inputs), y=[np.array(move_labels), np.array(value_labels)], epochs=epochs, batch_size=64)


def read_game_from_file(game_file_name):
    with open(game_file_name, 'r') as file:
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


if __name__ == "__main__":
    network = load_network("output/network1.h5")
    train_network_from_games(network, 4096, 64)
    network.save("output/network1.h5")
