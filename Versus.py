from collections import Counter
from ChessHeuristicMonteCarloTreeSearch import perform_search, pick_action


def heuristic_move_selector(states, heuristic, num_iter, temp, explore):
    move_prob_sums = sum((Counter({n[0]: p*c for n, p in
                                   perform_search(s, num_iter, temp, explore, heuristic, None).items()})
                          for s, c in states.items() if c > 1), Counter())
    prob_sum = 0.0
    power = 1.0 / temp
    probs = {}
    for m, p in move_prob_sums.items():
        if m is not None:  # Don't actually consider None moves
            prob = p ** power
            prob_sum += prob
            probs[m] = prob
    return pick_action({m: p/prob_sum for m, p in probs.items()})


if __name__ == "__main__":
    from Chess import Chess
    import chess
    from ScanningChooser import heuristic_scan3x3
    from RandomPossibleGameGenerator import generate_possible_states
    from Information import SomethingMovedTo
    from Turn import do_turn, material_heuristic

    state = Chess()

    player_blind = True
    player_turn = True

    belief_size = 2500
    retries = 10
    now_fraction = 3/5
    belief_states = []
    belief = generate_possible_states(belief_size, [], max_attempts=1)
    belief_states.append(belief)
    info = []
    iterations = 1000
    temperature = 1.0
    exploration = 1.4142135624

    while not state.isgameover():
        print("-----------")
        if player_turn:
            print("Your turn!")
            if player_blind:
                print(state.blind_boundary_string(-100, -100))
                tile = None
                while tile is None:
                    try:
                        t_str = input("Enter a tile to scan around (must be one of the 36 center tiles)")
                        letter = ord(t_str[0]) - ord('a')
                        number = ord(t_str[1]) - ord('1')
                        if 1 <= letter <= 6 and 1 <= number <= 6:
                            tile = letter, number
                    except:
                        print("Error bad tile")

                print(state.blind_boundary_string(tile[0], tile[1]))
            else:
                print(state.boundary_string())
            move = None
            try:
                move = chess.Move.from_uci(input("Enter your move to look like the following format: c2c4"))
            except ValueError:
                print("")
            while move is None:
                try:
                    move = chess.Move.from_uci(input("Invalid move string. Try again."))
                except ValueError:
                    print("")
            move_success, capture = state.try_apply_move_did_capture(move)
            if move_success:
                print("Move successfully executed")
            else:
                print("Move illegal")
            # Bookkeeping for AI move (this could be manually detected in the AI code,
            # but it is easier to do this)
            info.append([SomethingMovedTo(move.to_square)] if capture else [])
        else:
            print("AI turn!")
            belief = do_turn(belief_states, info, heuristic_scan3x3,
                             lambda x: heuristic_move_selector(x, material_heuristic, iterations, temperature,
                                                               exploration),
                             state, belief_size, now_fraction, max_attempts=retries)
            belief_states.append(belief)
        player_turn = not player_turn
