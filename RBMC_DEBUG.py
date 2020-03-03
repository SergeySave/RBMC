import chess
import random

game = chess.Board()

while len(list(game.legal_moves)) > 0:
    print(game.fen())
    game.push(random.choice(list(game.legal_moves)))
print(game.fen())
