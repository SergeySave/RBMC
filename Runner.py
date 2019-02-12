from ChessMonteCarloTreeSearch import *
# from TicTacToe import TicTacToe
# from SuperTicTacToe import SuperTicTacToe
from Chess import Chess
# from ChessUtils import *
# from chess import Move
# import cmd
from Network import Network, load_network
from Trainer import *
import json
import chess.pgn
import io

state = Chess()
white_network = Network()
white_network.compile()
# black_network = Network()
# black_network.compile()
black_network = white_network  # They are both the same network

states, moves, result = generate_game(white_network, black_network, 10, 1, 1, printing=False)

print(states)
print(moves)
print(result)

exporter = chess.pgn.StringExporter(headers=False, comments=False, variations=False)
with open("1.json", 'w') as file:
    json.dump({"game": chess.pgn.Game.from_board(states[-1].board).accept(exporter),
               "move_probs": [{move.uci(): prob for (move, prob) in probs.items()} for probs in moves],
               "result": result}, file, indent=4)
white_network.save("1.h5")
del white_network

with open('1.json', 'r') as file:
    game_read = json.load(file)
white_network = load_network("1.h5")

game = chess.pgn.read_game(io.StringIO(game_read['game']))
new_state = Chess()
new_states = []
for move in game.mainline_moves():
    new_states.append(new_state.clone())
    new_state.applymove(move)
new_states.append(new_state)
new_moves = [{chess.Move.from_uci(uci): prob for (uci, prob) in probs.items()} for probs in game_read['move_probs']]
new_result = game_read['result']

print(new_states)
print(new_moves)
print(new_result)

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
