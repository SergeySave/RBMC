import itertools
import chess
from Information import ViewportInformation
from collections import Counter
import random


def perform_scan(start_file, start_rank, num_files, num_ranks, game):
    all_pairs = itertools.product(range(start_file, start_file + num_files),
                                  range(start_rank, start_rank + num_ranks))
    return ViewportInformation({square: game.board.piece_at(square) for square in
                                (chess.square(file, rank) for file, rank in all_pairs)})


# 36 possible viewports
# n states
# 36*n checks
#
# How can you check all viewports at the same time
# 9*4 bits can be used to represent any viewport (36 bits so it needs to be a long (or 2 ints or 3 shorts))
# this creates an injective mapping from 3x3 to a 36 bit string
# if this big string is stored as 3 shorts it can be created for each row by bit shifting each tile from the last one
# and then bit masking it, makes each row take only 8 computations
# then by combining the rows by combining the shorts on adjacent tiles of adjacent rows
# total 64 computations vs 324 computations if you just did a "brute force" mapping
# perform these computations for each state
# now combining all of the viewports that resulted from each state, will take n amount of time
# The heuristic can be done at this point
#
# so if the heuristic is the viewport with the most different possible configurations given the states

def most_configuration_heuristic(viewports):
    max_size = max(len(counter) for loc, counter in viewports.items())
    return random.choice([loc for loc, counter in viewports.items() if len(counter) == max_size])


def biggest_same_heuristic(viewports):
    max_size = max(len(counter.most_common(1)) for loc, counter in viewports.items())
    return random.choice([loc for loc, counter in viewports.items() if len(counter) == max_size])


def get_piece_code(piece):
    if piece is None:
        return 6
    return piece.piece_type * (1 if piece.color == chess.WHITE else -1) + 6


def heuristic_scan3x3(now_states, game):
    viewports = {}
    for board, count in now_states.items():
        result = {}
        # Original for loop code
        for file, rank in itertools.product(range(8), range(8)):
            this = get_piece_code(board.board.piece_at(chess.square(file, rank)))
            up = (0, 0, 0) if file == 0 else result[(file - 1, rank)]
            left = (0 if rank == 0 else result[(file, rank - 1)][2])
            encoding = (up[1], up[2], this | ((left << 4) & 4095))
            result[(file, rank)] = encoding
            if file >= 2 and rank >= 2:
                viewport_location = (file - 2, rank - 2)
                if viewport_location not in viewports.keys():
                    viewports[viewport_location] = Counter()
                viewports[viewport_location][encoding] += count

        # Reduced python generator comprehension code
        # adj_generator = ((file, rank, get_piece_code(board.board.piece_at(chess.square(file, rank))),
        #                  (0, 0, 0) if file == 0 else result[(file - 1, rank)],
        #                  (0 if rank == 0 else result[(file, rank - 1)][2])) for file, rank in
        #                  itertools.product(range(8), range(8)))
        # for file, rank, this, up, left in adj_generator:
        #     result[(file, rank)] = (up[1], up[2], this | ((left << 4) & 4095))
        # for file, rank in itertools.product(range(2, 8), range(2, 8)):
        #     viewport_location = (file - 2, rank - 2)
        #     if viewport_location not in viewports.keys():
        #         viewports[viewport_location] = Counter()
        #     viewports[viewport_location][result[(file, rank)]] += count

    location = most_configuration_heuristic(viewports)

    # start_file and start_rank must be in the range [0, 5] because the scan is 3x3
    return perform_scan(location[0], location[1], 3, 3, game)
