from ChessMonteCarloTreeSearch import *
# from TicTacToe import TicTacToe
# from SuperTicTacToe import SuperTicTacToe
from Chess import Chess
# from ChessUtils import *
# from chess import Move
# import cmd
from Network import Network
from Trainer import *

state = Chess()
white_network = Network()
white_network.compile()
black_network = Network()
black_network.compile()

states, moves, result = generate_game(white_network, black_network, 100, 1, printing=True)

print(states)
print(moves)
print(result)

# allmoves = state.getallmoves()
# for move in allmoves:
#     newmove = state.clone()
#     newmove.applymove(move)
#     print(newmove.tostring())
# print(allmoves.count())

#
# node = None
# print(state.tostring())
#
# states = [state]
#
# move_probs = perform_search(states, 1000, 1.0, network)
#
# print(move_probs)
# print(pick_action(move_probs))

# while not state.isgameover():
    # move, node = perform_search(state, 10000, 1.4142135624, pre_node=node)
    # move = Move.from_uci(input("input"))
    # print(move)
    # print(node.wins, node.visits)
    # state.applymove(move)
    # print(get_current_repetition_count(state))
    # print(state.tostring())

# print(state.getboardstate(1))
