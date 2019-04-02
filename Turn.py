# first take in any information that we gained from the opponents move (from them possibly taking a piece)
# then update our previous possible board configurations to the next move according with that information that we may
# have gained
# next we want to select a region to scan that will reduce the possible board configurations by the greatest amount
# using the output of the scanning agent
# then we refill the possible board configurations back to its original size using random games that agree with all of
# the informations that we have collected (during training of the scanning agent we may want to sometimes forcibly
# include the true configuration in here)
# finally we make our move and we reduce the possible board configurations using any information we got from the move
# and then refill the set of configurations


from RandomPossibleGameGenerator import generate_possible_states, generate_next_states
from collections import Counter
from Information import *
import math
import random
from Chess import Chess


# last element in previous_beliefs is the belief we started with before our scan
# last element in info_list is the opponent's move and viewport scan
# element before that is our previous move
def generate_states_from_priors_pre_move(previous_beliefs, info_list, fraction, n_total, max_attempts=1):
    if n_total <= 1:
        return Counter()
    if len(previous_beliefs) == 0 or len(info_list) == 0:
        return Counter({Chess(): n_total})
    n_now = math.ceil(n_total * fraction)
    belief = previous_beliefs[-1]
    opponent_info = info_list[-1]
    if len(belief) == 0:
        n_now = 0
    priors = generate_states_from_priors(previous_beliefs[:-1], info_list[:-1], fraction, n_total - n_now, max_attempts)
    priors += belief  # Counter(random.choices(list(belief.keys()), k=n_total-sum(priors.values())))
    # Propogate according to opponent_info
    nows = Counter()
    attempts = 0
    while attempts < max_attempts and sum(nows.values()) < n_total:
        nows += sum((Counter(d) for d in (generate_next_states(state, amount, opponent_info) for state, amount in priors.items())), Counter())
        attempts += 1
    if len(nows) == 0:
        return Counter()
    nows = Counter(random.choices(list(nows.keys()), weights=list(nows.values()), k=n_total))
    return nows


# last element in previous_beliefs is the belief we started with before our scan
# last element in info_list is the opponent's move and viewport scan
# element before that is our previous move
def generate_states_from_priors(previous_beliefs, info_list, fraction, n_total, max_attempts=1):
    if n_total <= 1:
        return Counter()
    if len(previous_beliefs) == 0 or len(info_list) == 0:
        return Counter({Chess(): n_total})
    my_move = info_list[-1]
    nows = generate_states_from_priors_pre_move(previous_beliefs, info_list[:-1], fraction, n_total, max_attempts=max_attempts)
    if my_move is not None:
        nows = Counter({g.applymove(my_move): c for g, c in nows.items()})
    return nows


def material_heuristic(state):
    white_points = len(state.board.pieces(chess.PAWN, chess.WHITE)) + \
                   3 * len(state.board.pieces(chess.KNIGHT, chess.WHITE)) + \
                   3 * len(state.board.pieces(chess.BISHOP, chess.WHITE)) + \
                   6 * len(state.board.pieces(chess.ROOK, chess.WHITE)) + \
                   9 * len(state.board.pieces(chess.QUEEN, chess.WHITE))
    black_points = len(state.board.pieces(chess.PAWN, chess.BLACK)) + \
                   3 * len(state.board.pieces(chess.KNIGHT, chess.BLACK)) + \
                   3 * len(state.board.pieces(chess.BISHOP, chess.BLACK)) + \
                   6 * len(state.board.pieces(chess.ROOK, chess.BLACK)) + \
                   9 * len(state.board.pieces(chess.QUEEN, chess.BLACK))
    return white_points / (white_points + black_points)


def get_probability_distribution(state, heuristic, temperature=1.0):
    power = 1.0 / temperature
    result = {}
    for m in state.board.legal_moves:
        state.board.push(m)
        result[m] = heuristic(state) ** power
        state.board.pop()
    return result


def generate_next_states_probs(game, counter, info_list):
    # pick legal moves from the probability distribution
    # apply them
    # ngen is the next game generator
    prob_distr = get_probability_distribution(game, material_heuristic, 0.5)
    ngen = ((game.clone().applymove(move), c, move) for move, c in
            Counter(random.choices(list(prob_distr.keys()), weights=list(prob_distr.values()), k=counter)).items())
    # for each of those next games make sure it is consistent with the information we have available for this move
    return {new_game: c for new_game, c, move in ngen if consistent_with_all(new_game, move, info_list)}


# region_selector is a function from a list of previous possible board configurations to a ViewportInformation
# move_selector is a function from a list of possible board configurations to a move
def do_turn(previous_beliefs, info_list, region_selector, move_selector, game, desired_size, gen_fraction, max_attempts=1):
    opponent_move = info_list[-1]
    previous = previous_beliefs[-1]

    # Propagate moves 1 step forward
    now_states = sum((Counter(d) for d in (generate_next_states_probs(state, amount, opponent_move) for state, amount in
                                           previous.items())), Counter())

    now_states += generate_states_from_priors_pre_move(previous_beliefs, info_list, gen_fraction, desired_size - sum(now_states.values()),
                                                       max_attempts=max_attempts)

    # Select a region
    scan_viewport_info = region_selector(now_states, game)
    # print(scan_viewport_info)
    # Add the information to our information list
    opponent_move.append(scan_viewport_info)

    # Remove illegal states
    now_states = Counter({state: amount for state, amount in now_states.items() if
                          scan_viewport_info.consistent_with(state, None)})

    # Repopulate with legal states
    # now_states += generate_possible_states(desired_size - sum(now_states.values()), info_list,
    #                                        max_attempts=max_attempts)
    now_states += generate_states_from_priors_pre_move(previous_beliefs, info_list, gen_fraction, desired_size - sum(now_states.values()),
                                                       max_attempts=max_attempts)

    # Pick a move
    move = move_selector(now_states)
    # Do the move
    move_success = game.try_apply_move(move)

    # Apply move (if needed and possible) and apply information
    if move_success:
        # We made this move
        info_list.append(move)
        opponent_move.append(LegalMove(move))

        next_states = Counter({g.clone().applymove(move): c for g, c in now_states.items() if
                               (move in g.board.legal_moves)})
    else:
        # We made no move (turn skipped)
        info_list.append(None)
        opponent_move.append(IllegalMove(move))

        next_states = Counter({g: c for g, c in now_states.items() if (move not in g.board.legal_moves)})

    # next_states += generate_possible_states(desired_size - sum(next_states.values()), info_list,
    #                                         max_attempts=max_attempts)
    next_states += generate_states_from_priors(previous_beliefs, info_list, gen_fraction, desired_size - sum(next_states.values()),
                                               max_attempts=max_attempts)

    return next_states


if __name__ == "__main__":
    from Chess import Chess
    from ScanningChooser import heuristic_scan3x3
    true_state = Chess()
    belief_size = 2500
    retries = 10
    now_fraction = 3/5
    all_belief_states = []
    belief = generate_possible_states(belief_size, [], max_attempts=1)
    all_belief_states.append(belief)
    info = []

    is_ai_move = False

    for move in ["d4", "Nf6", "Bg5", "e6", "e4", "Be7", "Nd2", "d5", "e5", "Nfd7", "Be3", "b6", "Nh3", "Bb7", "Qg4",
                 "g6", "Ng5", "Nf8", "h4", "h6", "Ngf3", "Na6", "c3", "Qd7", "a4", "O-O-O", "b4", "c5", "Bb5", "Qc7",
                 "dxc5", "bxc5", "O-O", "f5", "exf6", "Bxf6", "Rac1", "h5", "Qh3", "Kb8", "Rfe1", "Bc8", "Bxa6",
                 "Bxa6", "Bxc5", "Bc8", "c4", "Be7", "Bxe7", "Qxe7", "Qg3+", "Qd6", "Ne5", "Rd7", "Nxd7+", "Kc7",
                 "Ne5", "Kb7", "c5", "Qc7", "c6+", "Ka8", "b5", "Rh7", "Qf4", "Rh8", "Ndf3", "a6", "Nd4", "Nh7",
                 "bxa6", "Rf8", "Qe3", "Bxa6", "Nb5", "Bxb5", "axb5", "Kb8", "b6", "Qe7", "Ra1", "Qd6", "Nd7+",
                 "Kc8", "Ra8+"]:
        if is_ai_move:
            print(true_state.tostring())
            belief = do_turn(all_belief_states, info, heuristic_scan3x3,
                             lambda x: true_state.board.parse_san(move),
                             true_state, belief_size, now_fraction, max_attempts=retries)
            all_belief_states.append(belief)
            print(len(belief), true_state in belief.keys(), max(belief.values()) == belief[true_state])
            print()
            print()
        else:
            move = true_state.board.parse_san(move)
            did_capture = true_state.apply_move_did_capture(move)
            info.append([SomethingMovedTo(move.to_square)] if did_capture else [])

        is_ai_move = not is_ai_move

    # did_capture = true_state.apply_move_did_capture(chess.Move.from_uci("b1c3"))
    #
    # belief2 = do_turn(belief, info, heuristic_scan3x3,
    #                   lambda x: chess.Move.from_uci("g8f6"),
    #                   true_state, belief_size, max_attempts=retries)
    #
    # true_state.apply_move_did_capture(chess.Move.from_uci("g1f3"))
    # info.append([])
    # belief3 = do_turn(belief2, info, heuristic_scan3x3,
    #                   lambda x: chess.Move.from_uci("f6e4"),
    #                   true_state, belief_size, max_attempts=retries)
    #
    # true_state.applymove(chess.Move.from_uci("c3e4"))
    # info.append([SomethingMovedTo(chess.E4)])
    # belief4 = do_turn(belief3, info, heuristic_scan3x3,
    #                   lambda x: chess.Move.from_uci("b8a6"),
    #                   true_state, belief_size, max_attempts=retries)

    # print(belief)
    # print("--------------")
    # print(len(belief2))
    # for board, count in belief2.items():
    #     print(count)
    #     print(board.tostring())
    #     print()
    # print("--------------")
    # print(len(belief3))
    # for board, count in belief3.items():
    #     print(count)
    #     print(board.tostring())
    #     print()
    # print("--------------")
    # print(len(belief4))
    # for board, count in belief4.items():
    #     print(count)
    #     print(board.tostring())
    #     print()

"""
1. d4 Nf6 2. Bg5 e6 3. e4 Be7 4. Nd2 d5 5. e5 Nfd7 6. Be3 b6 7. Nh3 Bb7 8. Qg4
g6 9. Ng5 Nf8 10. h4 h6 11. Ngf3 Na6 12. c3 Qd7 13. a4 O-O-O 14. b4 c5 15. Bb5
Qc7 16. dxc5 bxc5 17. O-O f5 18. exf6 Bxf6 19. Rac1 h5 20. Qh3 Kb8 21. Rfe1 Bc8
22. Bxa6 Bxa6 23. Bxc5 Bc8 24. c4 Be7 25. Bxe7 Qxe7 26. Qg3+ Qd6 27. Ne5 Rd7
28. Nxd7+ Kc7 29. Ne5 Kb7 30. c5 Qc7 31. c6+ Ka8 32. b5 Rh7 33. Qf4 Rh8 34.
Ndf3 a6 35. Nd4 Nh7 36. bxa6 Rf8 37. Qe3 Bxa6 38. Nb5 Bxb5 39. axb5 Kb8 40. b6
Qe7 41. Ra1 Qd6 42. Nd7+ Kc8 43. Ra8+ 1-0


"""
