from GameManager import GameManager
from NetworkManager import NetworkManager
from Trainer import *
from Constants import *


def generate_self_play_games(network, num_games, num_iterations, temperature, exploration, game_mangr, verbose=False):
    for i in range(num_games):
        states, moves, result = generate_game(network, network, num_iterations, temperature, exploration,
                                              printing=verbose)
        game_mangr.save_next_game(states, moves, result)


if __name__ == "__main__":
    network_manager = NetworkManager(True)
    game_manager = GameManager(GAME_KEEP_NUM, True)
    while True:
        generate_self_play_games(network_manager.load_recent_network(), GAMES_PER_ITER, EVAL_PER_MOVE, TEMPERATURE,
                                 EXPLORATION, game_manager, True)
