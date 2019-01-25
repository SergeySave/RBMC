from Chess import Chess
from ChessMonteCarloTreeSearch import *


def generate_game(white_network, black_network, iterations, temperature, printing=False):
    game = Chess()
    if printing:
        print(game.tostring())

    game_states = []
    moves_probs = []

    while not game.isgameover():
        game_states.append(game.clone())
        network = white_network if (game.currentPlayer == 1) else black_network
        move_probs = perform_search(game_states, iterations, temperature, network)
        moves_probs.append(move_probs)
        move = pick_action(move_probs)
        game.applymove(move)
        if printing:
            print(game.tostring())

    return game_states, moves_probs, game.getboardstate(1)