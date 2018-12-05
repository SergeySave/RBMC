from MonteCarloTreeSearch import *
# from TicTacToe import TicTacToe
# from SuperTicTacToe import SuperTicTacToe
from Chess import Chess

state = Chess()

# state.state[30] = 2
# allmoves = state.getallmoves()
# print(len(allmoves))
# for move in allmoves:
#     newmove = state.clone()
#     newmove.applymove(move)
#     print(newmove.tostring())

node = None

while not state.isgameover():
    move, node = perform_search(state, 20, 1.4142135624, pre_node=node)
    print(move)
    print(node.wins, node.visits)
    state.applymove(move)
    print(state.tostring())
