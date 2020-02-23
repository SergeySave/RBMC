from rbmc.RBMCNetwork import  *
from rbmc.RBMCNetworkManager import  *

def main():
    network = Network()
    network.compile()
    NetworkManager().save_recent_network(network)
