from collections import Counter
import math
import random
from RandomPossibleGameGenerator import generate_next_states
from Chess import Chess


# beliefs is the set of all of my beliefs at each time step
# info_list is the set of all of my informations
# fraction is the fraction of beliefs that should be generated at this step
# n_total is the total amount of beliefs that should be generated
# belief_index is the most recent belief for which we are trying to compute
# info_index is the most recent info for which we are trying to compute
# max_attempts is the maximum number of attempts we have to generate enough beliefs
#
# This method expects the beliefs at belief_index to be beliefs AFTER the latest opponent's move has been estimated
# info_list[info_index] contains any information we have on the opponent's latest move
# info_list[info_index - 1] will be our previous move
# info_list[info_index - 2] is opponent's second to last move
#
# beliefs[belief_index] is a what our beliefs are now (before the current move)
# beliefs[belief_index - 1] is what our beliefs were before our last move
# beliefs[belief_index - 2] is what our beliefs were before our second to last move
def generate_pre_move(beliefs, info_list, fraction, n_total, belief_index, info_index, max_attempts=1):
    if n_total <= 1:
        return Counter()
    if belief_index < 0 or info_index < 0:
        return Counter({Chess(): n_total})

    n_now = math.ceil(n_total * fraction)
    last_beliefs = beliefs[belief_index - 1]

    if len(last_beliefs) == 0:
        n_now = 0

    # At this point belief
    priors = generate_post_move(beliefs, info_list, fraction, n_total - n_now, belief_index - 1, info_index - 1,
                                max_attempts)
    if len(last_beliefs) > 0:
        priors += Counter(random.choices(list(last_beliefs.keys()), weights=list(last_beliefs.values()), k=n_now))

    nows = Counter()
    attempts = 0
    while attempts < max_attempts and sum(nows.values()) < n_total:
        nows += sum((Counter(d) for d in
                     (generate_next_states(state, amount, info_list[info_index]) for state, amount in priors.items())),
                    Counter())
        attempts += 1

    if len(nows) == 0:
        return Counter()
    return Counter(random.choices(list(nows.keys()), weights=list(nows.values()), k=n_total))


# beliefs[belief_index] is a what our beliefs were before the move we just made
# beliefs[belief_index - 1] is what our beliefs were before our second to last move
# beliefs[belief_index - 2] is what our beliefs were before our third to last move
#
# info_list[info_index] is the move we just took
# info_list[info_index - 1] is info about the opponent's last move
# info_list[info_index - 2] is the move we took before that
def generate_post_move(beliefs, info_list, fraction, n_total, belief_index, info_index, max_attempts=1):
    if n_total <= 1:
        return Counter()
    if belief_index < 0 or info_index < 0:
        return Counter({Chess(): n_total})

    my_move = info_list[info_index]
    nows = generate_pre_move(beliefs, info_list, fraction, n_total, belief_index,
                             info_index - 1, max_attempts)
    if my_move is not None:
        nows = Counter({g.clone().applymove(my_move): c for g, c in nows.items()})
    return nows


generate_states_from_priors_pre_move = generate_pre_move
generate_states_from_priors = generate_post_move
