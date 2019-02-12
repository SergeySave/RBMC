import os
from Network import load_network


class NetworkManager:

    def __init__(self, verbose=False):
        self.current_num_networks = 1
        self.verbose = verbose

    def update_state(self):
        if os.path.exists("output/network/current.txt"):
            with open("output/network/current.txt", 'r') as file:
                self.current_num_networks = int(file.readline())

    def save_recent_network(self, network):
        self.update_state()  # Ensure we know how many networks there are
        print("Saving network " + str(self.current_num_networks))
        network.save("output/network/network" + str(self.current_num_networks) + ".h5")
        self.current_num_networks += 1
        with open("output/network/current.txt", 'w') as file:
            file.writelines([str(self.current_num_networks)])

    def load_recent_network(self):
        self.update_state()
        print("Loading network " + str(self.current_num_networks - 1))
        return load_network("output/network/network" + str(self.current_num_networks - 1) + ".h5")
