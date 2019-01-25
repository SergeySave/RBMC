import collections


# This is a slightly modified can_claim_threefold_repetition from python-chess
# the original is available here: https://github.com/niklasf/python-chess/blob/master/chess/__init__.py#L1838
# This does not check if there is a possible move that causes a repetition, that can be handled elsewhere
def get_current_repetition_count(board_state):
    """
    Draw by threefold repetition can be claimed if the position on the
    board occured for the third time or if such a repetition is reached
    with one of the possible legal moves.
    Note that checking this can be slow: In the worst case
    scenario every legal move has to be tested and the entire game has to
    be replayed because there is no incremental transposition table.
    """
    transposition_key = board_state._transposition_key()
    transpositions = collections.Counter()
    transpositions.update((transposition_key,))

    # Count positions.
    switchyard = []
    while board_state.move_stack:
        move = board_state.pop()
        switchyard.append(move)

        if board_state.is_irreversible(move):
            break

        transpositions.update((board_state._transposition_key(),))

    while switchyard:
        board_state.push(switchyard.pop())

    # Return the number of repetitions and the last move (which would have caused that repetition number)
    return transpositions[transposition_key] - 1, board_state.peek()
