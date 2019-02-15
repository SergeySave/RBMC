from Constants import *
from GameManager import GameManager
from NetworkManager import NetworkManager


def train_network_from_games(training_network, game_mangr, num_steps, verbose=False):
    training_network.model.optimizer.lr.assign(LEARNING_RATE)
    training_network.model.optimizer.momentum.assign(MOMENTUM)
    for i in range(num_steps):
        if verbose:
            print("Starting training iteration " + str(i))
        inputs, move_labels, value_labels = game_mangr.sample_moves(SAMPLE_SIZE)
        training_network.model.fit(x=inputs, y=[move_labels, value_labels], epochs=1, batch_size=BATCH_SIZE)


if __name__ == "__main__":
    network_manager = NetworkManager(True)
    game_manager = GameManager(GAME_KEEP_NUM, True)
    network = network_manager.load_recent_network()
    while True:
        train_network_from_games(network, game_manager, True)
        network_manager.save_recent_network(network)
