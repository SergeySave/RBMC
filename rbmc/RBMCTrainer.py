from rbmc.RBMCGameManager import *
from rbmc.RBMCNetworkManager import *


def train_iteration(network, sample):
    inputs, move_outs, result_outs, scan_outs = sample
    network.model.optimizer.lr.assign(LEARNING_RATE)
    network.model.optimizer.momentum.assign(MOMENTUM)
    print("Starting training iteration")
    network.model.fit(x=inputs, y=[move_outs, result_outs, scan_outs], epochs=1, batch_size=BATCH_SIZE)


def main():
    network_manager = NetworkManager(True)
    game_manager = GameManager(GAME_KEEP_NUM, True)
    network = network_manager.load_recent_network()
    while True:
        for i in range(STEPS_PER_ITER):
            train_iteration(network, game_manager.sample_moves(SAMPLE_SIZE))
        network_manager.save_recent_network(network)
