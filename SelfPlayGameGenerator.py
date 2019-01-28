import json

import chess.pgn

from Network import load_network
from Trainer import *
import os.path

state = Chess()
white_network = load_network("output/network1.h5")
black_network = load_network("output/network2.h5")

exporter = chess.pgn.StringExporter(headers=False, comments=False, variations=False)

for i in range(4096):
    if os.path.exists("output/" + str(i) + ".json"):
        print("Skipping iteration " + str(i) + " output file already exists")
    else:
        print("Starting self-play iteration " + str(i))
        states, moves, result = generate_game(white_network, black_network, 1000, 1, printing=False)
        with open("output/" + str(i) + ".json", 'w') as file:
            json.dump({"game": chess.pgn.Game.from_board(states[-1].board).accept(exporter),
                       "move_probs": [{move.uci(): prob for (move, prob) in probs.items()} for probs in moves],
                       "result": result}, file, indent=4)

