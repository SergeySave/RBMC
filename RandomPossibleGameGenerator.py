

# Can't do better than O(nm)
# n = number of desired random possible games
# m = game depth
#
# O(n) could be achieved if the entire possible game tree from the previous move was known
# but that would take O(b^m) space where b is the branching factor (chess ~35)
# impractical solution
#
# Stochastic approach:
# start from the beginning each time with n moves
# pick a random move for each of the n moves (do something if it does not follow known information)
# repeat m times
#
# possible things to do if a move fails:
# regenerate a move from the start (ok if fails are unlikely)
#     could end up higher than O(nm)
#     if there are k total misses then it becomes O((n+k)m)
#     with a lot of known information k ends up higher
#     but good distribution
# pick a random move that did follow the known information in this set of n for this move (forces it to stick to O(nm))
#     if all of the moves happened to be misses then we get stuck (have to regenerate all O(nm))
#     all misses less likely with big n
#     has less distribution than fully random (but less of a penalty for misses)
# undo the previous illegal move and pick again
#     with a lot of known information in certain paths, paths become very linear
#     possible that all children of a move are illegal (what do?)
#         go up another move? - could get really expensive really quickly
#             and we need to remember where that move came from (lots of edge cases)
#         pick one of the other options? regenerate?
#             reduces to the other problems
#
#
# Chose to do thing 2 (take a move that succeeded)
# Bonuses:
#   Speed bonus in first couple steps or while many possible games share the same state
#
#
#
#
#
#
#
#
#
#


from Chess import Chess
import random
from collections import Counter
from Information import *


def generate_next_states(game, counter, info_list):
    # get the set of next possible games
    # pick the right number of moves
    next_games = [new_game for (new_game, move) in ((game.clone().applymove(move), move) for move in game.getallmoves()) if consistent_with_all(new_game, move, info_list)]
    if len(next_games) == 0:
        return Counter()
    return Counter(random.choices(next_games, k=counter))

    #ngen = ((game.clone().applymove(move), c, move) for move, c in
    #        Counter(random.choices(game.getallmoves(), k=counter)).items())
    #ngen = list(ngen)
    #print(ngen)
    # for each of those next games make sure it is consistent with the information we have available for this move
    #return {new_game: c for new_game, c, move in ngen if consistent_with_all(new_game, move, info_list)}


# TODO: Implement some way to account for the opponent failing to move/skipping a turn
def generate_possible_states(n, information, max_attempts=5):
    if n == 0:
        return Counter()
    states = Counter({Chess(): n})
    for info in information:
        if info is None:
            # No move was made (using None to represent a missed/skipped move)
            new_states = states
        elif type(info) is chess.Move:

            # Try applying the move
            new_states = Counter({g.clone().applymove(info): c for g, c in states.items() if
                                  (info in g.board.legal_moves)})
        else:
            # this is the next possible states
            new_states = sum((Counter(d) for d in [generate_next_states(g, c, info) for g, c in states.items()]),
                             Counter())
        if len(new_states) == 0:
            # we completely failed: try again
            if max_attempts > 1:
                return generate_possible_states(n, information, max_attempts=max_attempts-1)
            else:
                return Counter()
        misses = n - sum(new_states.values())
        states = Counter(random.choices(list(new_states.keys()), k=misses)) + new_states
    return states


if __name__ == "__main__":
    for stat, count in generate_possible_states(1000, [chess.Move.from_uci('b1c3'),
                                                       [NothingInSix()],
                                                       [MovedKnight(), BlackMissingPawn()],
                                                       [],
                                                       [],
                                                       [],
                                                       []], max_attempts=1).items():
        print(count)
        print(stat.tostring())
        print()
