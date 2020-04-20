from collections import Counter
from Chess import Chess
import math
from RandomPossibleGameGenerator import generate_next_states
import random
from multiprocessing import Pool


def mp_single_attempt(inp):
    state, amount, opponent_info = inp
    return generate_next_states(state, amount, opponent_info)


# last element in previous_beliefs is the belief we started with before our scan
# last element in info_list is the opponent's move and viewport scan
# element before that is our previous move
def generate_states_from_priors_pre_move(previous_beliefs, info_list, fraction, n_total, belief_index, info_index, max_attempts=1):
    # Return Value: Counter of Tuple( Current Board, Dict( Origin Belief Index, Origin Board ) )
    if n_total <= 1:
        return Counter()
    if belief_index < 0 or info_index < 0:
        return Counter({Chess(): n_total})

    n_now = math.ceil(n_total * fraction)
    belief = previous_beliefs[belief_index]
    opponent_info = info_list[info_index]

    if len(belief) == 0:
        n_now = 0

    priors = generate_states_from_priors(previous_beliefs, info_list, fraction, n_total - n_now, belief_index - 1, info_index - 1, max_attempts)
    if len(belief) > 0:
        priors += Counter(random.choices(list(belief.keys()), weights=list(belief.values()), k=n_now))

    nows = Counter()
    attempts = 0
    with Pool() as pool:
        while attempts < max_attempts and sum(nows.values()) < n_total:
            nows += sum(pool.map(mp_single_attempt, ((state, amount, opponent_info) for
                                                     state, amount in priors.items())), Counter())
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
        return Counter({Chess(): n_total})
    my_move = info_list[info_index]
    nows = generate_states_from_priors_pre_move(previous_beliefs, info_list, fraction, n_total, belief_index, info_index - 1, max_attempts)
    nows = Counter({g.clone().applymove(my_move): c for g, c in nows.items()})
    return nows


def update_prior_beliefs(previous_beliefs, state_gens, max_count):
    return state_gens
