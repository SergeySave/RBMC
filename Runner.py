from MonteCarloTreeSearch import *
from TicTacToe import TicTacToe
from SuperTicTacToe import SuperTicTacToe

state = SuperTicTacToe()

print(state.tostring())

node = None

while not state.isgameover():
    move, node = perform_search(state, 500, 1.4142135624, pre_node=node)
    print(move)
    print(node.wins, node.visits)
    state.applymove(move)
    print(state.tostring())
