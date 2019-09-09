from collections import Counter
from Chess import Chess
import math
from RandomPossibleGameGenerator import generate_next_states
import random


# last element in previous_beliefs is the belief we started with before our scan
# last element in info_list is the opponent's move and viewport scan
# element before that is our previous move
def generate_states_from_priors_pre_move(previous_beliefs, info_list, fraction, n_total, belief_index, info_index, max_attempts=1):
    # Return Value: Counter of Tuple( Current Board, Dict( Origin Belief Index, Origin Board ) )
    if n_total <= 1:
        return Counter()
    if belief_index < 0 or info_index < 0:
        return Counter({(Chess(), ((belief_index, Chess()),)): n_total})

    n_now = math.ceil(n_total * fraction)
    belief = previous_beliefs[belief_index]
    opponent_info = info_list[info_index]

    if len(belief) == 0:
        n_now = 0

    priors = generate_states_from_priors(previous_beliefs, info_list, fraction, n_total - n_now, belief_index - 1, info_index - 1, max_attempts)
    joining = Counter({(game, ((belief_index, game),)): count for game, count in belief.items()})
    if len(joining) > 0:
        priors += Counter(random.choices(list(joining.keys()), weights=list(joining.values()), k=n_now))

    nows = Counter()
    attempts = 0
    while attempts < max_attempts and sum(nows.values()) < n_total:
        nows += sum((Counter({(new_game, state[1]): count
                              for new_game, count in generate_next_states(state[0], amount, opponent_info).items()})
                     for state, amount in priors.items()), Counter())
        attempts += 1
    if len(nows) == 0:
        return Counter()
    return Counter(random.choices(list(nows.keys()), weights=list(nows.values()), k=n_total))


# last element in previous_beliefs is the belief we started with before our scan
# last element in info_list is the opponent's move and viewport scan
# element before that is our previous move
def generate_states_from_priors(previous_beliefs, info_list, fraction, n_total, belief_index, info_index, max_attempts=1):
    if n_total <= 1:
        return Counter()
    if belief_index < 0 or info_index < 0:
        return Counter({(Chess(), ((belief_index, Chess()),)): n_total})
    my_move = info_list[info_index]
    nows = generate_states_from_priors_pre_move(previous_beliefs, info_list, fraction, n_total, belief_index, info_index - 1, max_attempts)
    if my_move is not None:
        inner_generator = ((g[0].applymove(my_move), g[1], c) for g, c in nows.items())
        nows = Counter({(new_game, states + ((belief_index, new_game),)): counts for new_game, states, counts in inner_generator})
    return nows


def update_prior_beliefs(previous_beliefs, state_gens, max_count):
    # state_gens is a Counter of Tuple( Current Board, Dict( Origin Belief Index, Origin Board ) )
    # origins is a Dict( Origin Belief Index, Counter( Origin Board ) )
    origins = {}
    result = Counter()
    for data_tuple, count in state_gens.items():
        result[data_tuple[0]] += count
        for inner_tuple in data_tuple[1]:
            origin_index, origin_board = inner_tuple
            if origin_index > 0:
                if origin_index not in origins:
                    origins[origin_index] = Counter()
                origins[origin_index][origin_board] += 1
    for origin_index, origin_board_counter in origins.items():
        previous_beliefs[origin_index] += Counter(random.choices(list(origin_board_counter.keys()), weights=list(origin_board_counter.values()), k=int(max_count * 0.6)))
        # previous_beliefs[origin_index] += origin_board_counter # Add the counters together
        # if sum(previous_beliefs[origin_index].values()) > max_count:
        previous_beliefs[origin_index] = Counter(random.choices(list(previous_beliefs[origin_index].keys()), weights=list(previous_beliefs[origin_index].values()), k=max_count))
    return result
