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


# region_selector is a function from a list of previous possible board configurations to a ViewportInformation
# move_selector is a function from a list of possible board configurations to a move
def do_turn(previous, info_list, region_selector, move_selector, game, max_attempts=1):
    desired_size = sum(previous.values())
    opponent_move = info_list[-1]

    now_states = sum((Counter(d) for d in (generate_next_states(state, amount, opponent_move) for state, amount in
                                           previous.items())), Counter())

    scan_viewport_info = region_selector(now_states)
    opponent_move.append(scan_viewport_info)

    now_states = Counter({state: amount for state, amount in now_states.items() if
                          scan_viewport_info.consistent_with(state, None)})

    now_states += generate_possible_states(desired_size - sum(now_states.values()), info_list,
                                           max_attempts=max_attempts)

    move = move_selector(now_states)

    move_success = game.try_apply_move(move)

    if move_success:
        # We made this move
        info_list.append(move)

        next_states = Counter({g.clone().applymove(move): c for g, c in now_states.items() if
                               (move in g.board.legal_moves)})
    else:
        # We made no move (turn skipped)
        info_list.append(None)
        opponent_move.append(IllegalMove(move))

        next_states = Counter({g: c for g, c in now_states.items() if (move not in g.board.legal_moves)})

    next_states += generate_possible_states(desired_size - sum(now_states.values()), info_list,
                                            max_attempts=max_attempts)
    return next_states


if __name__ == "__main__":
    from Chess import Chess
    true_state = Chess()
    true_state.applymove(chess.Move.from_uci("b1c3"))
    belief = generate_possible_states(1000, [], max_attempts=1)
    info = [[]]
    belief2 = do_turn(belief, info, lambda x: ViewportInformation({chess.D3: None, chess.D4: None, chess.D5: None,
                                                                   chess.E3: None, chess.E4: None, chess.E5: None,
                                                                   chess.F3: None, chess.F4: None, chess.F5: None}),
                      lambda x: chess.Move.from_uci("g8f6"),
                      true_state)
    true_state.applymove(chess.Move.from_uci("g1f3"))
    info.append([])
    belief3 = do_turn(belief2, info, lambda x: ViewportInformation({chess.D3: None, chess.D4: None, chess.D5: None,
                                                                    chess.E3: None, chess.E4: None, chess.E5: None,
                                                                    chess.F3: chess.Piece(chess.KNIGHT, chess.WHITE),
                                                                    chess.F4: None, chess.F5: None}),
                      lambda x: chess.Move.from_uci("f6e4"),
                      true_state)
    true_state.applymove(chess.Move.from_uci("c3e4"))
    info.append([SomethingMovedTo(chess.E4)])
    belief4 = do_turn(belief3, info, lambda x: ViewportInformation({chess.D3: None, chess.D4: None, chess.D5: None,
                                                                    chess.E3: None,
                                                                    chess.E4: chess.Piece(chess.KNIGHT, chess.WHITE),
                                                                    chess.E5: None,
                                                                    chess.F3: chess.Piece(chess.KNIGHT, chess.WHITE),
                                                                    chess.F4: None, chess.F5: None}),
                      lambda x: chess.Move.from_uci("b8a6"),
                      true_state, max_attempts=100)
    print(belief)
    print("--------------")
    for board, count in belief2.items():
        print(count)
        print(board.tostring())
        print()
    print("--------------")
    for board, count in belief3.items():
        print(count)
        print(board.tostring())
        print()
    print("--------------")
    for board, count in belief4.items():
        print(count)
        print(board.tostring())
        print()
