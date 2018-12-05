from MonteCarloTreeSearch import *
# from TicTacToe import TicTacToe
# from SuperTicTacToe import SuperTicTacToe
from Chess import Chess

state = Chess()

# allmoves = state.getallmoves()
# for move in allmoves:
#     newmove = state.clone()
#     newmove.applymove(move)
#     print(newmove.tostring())
# print(allmoves.count())


node = None

while not state.isgameover():
    move, node = perform_search(state, 10000, 1.4142135624, pre_node=node)
    print(move)
    print(node.wins, node.visits)
    state.applymove(move)
    print(state.tostring())

print(state.getboardstate(1))
