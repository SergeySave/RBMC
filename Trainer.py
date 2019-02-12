from Chess import Chess
from ChessMonteCarloTreeSearch import *


def generate_game(white_network, black_network, iterations, temperature, exploration, printing=False):
    game = Chess()
    if printing:
        print(game.tostring())

    game_states = []
    moves_probs = []

    while not game.isgameover():
    # for i in range(4):
        game_states.append(game.clone())
        network = white_network if (game.currentPlayer == 1) else black_network
        move_probs = perform_search(game_states, iterations, temperature, exploration, network)
        moves_probs.append(move_probs)
        move = pick_action(move_probs)
        game.applymove(move)
        if printing:
            print(game.tostring())
    # game_states.append(game.clone())

    return game_states, moves_probs, game.getboardstate(1)
