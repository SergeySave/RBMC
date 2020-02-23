from rbmc.RBMCNetwork import  *
from rbmc.RBMCNetworkManager import  *

network = Network()
network.compile()
NetworkManager().save_recent_network(network)
