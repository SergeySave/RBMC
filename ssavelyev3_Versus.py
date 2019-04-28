from collections import Counter
from ssavelyev3_ChessHeuristicMonteCarloTreeSearch import perform_search, pick_action


def heuristic_move_selector(states, heuristic, num_iter, temp, explore):
    move_prob_sums = sum((Counter({n[0]: p*c for n, p in
                                   perform_search(s, num_iter, temp, explore, heuristic, None).items()})
                          for s, c in states.most_common(15)), Counter())
    prob_sum = 0.0
    power = 1.0 / temp
    probs = {}
    for m, p in move_prob_sums.items():
        if bool(m):  # Don't actually consider null moves
            prob = p ** power
            prob_sum += prob
            probs[m] = prob
    return pick_action({m: p/prob_sum for m, p in probs.items()})

