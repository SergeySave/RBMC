from Chess import Chess
from ChessMonteCarloTreeSearch import *


def generate_game(white_network, black_network, iterations, temperature, exploration, printing=False):
    game = Chess()
    if printing:
        print(game.tostring())

    game_states = []
    moves_probs = []

    base_node = None

    while not game.isgameover():
        game_states.append(game.clone())
        network = white_network if (game.currentPlayer == 1) else black_network
        move_probs = perform_search(game_states, iterations, temperature, exploration, network, base_node)
        moves_probs.append({pair[0]: prob for (pair, prob) in move_probs.items()})
        move, node = pick_action(move_probs)
        base_node = node
        game.applymove(move)
        if printing:
            print(game.tostring())

    return game_states, moves_probs, game.getboardstate(1)
