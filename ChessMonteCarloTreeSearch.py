import math
import random
import chess


class Node:
    def __init__(self, state, action, prior, parent):
        self.state = state  # Board state
        self.action = action  # How did we get here? (only None for root)
        self.prior = prior  # prior probability P(state, action)
        self.visits = 0.0  # visit count N(state, action)
        self.avalue = 0.0  # action-value Q(state, action)

        # Q(s, a) = total_value / N(s,a)
        self.total_value = 0.0  # sum of all reachable values

        self.parent = parent
        self.children = []
        self.player = state.currentPlayer
        self.value = 0.0  # NN evaluation of the current state V(state)


def get_prob_for_move(move, probs):
    in_plane_index = move.from_square
    origin_file = chess.square_file(in_plane_index)
    origin_rank = chess.square_rank(in_plane_index)
    dest_file = chess.square_file(move.to_square)
    dest_rank = chess.square_rank(move.to_square)
    plane = -1 # should error if this stays -1
    if move.promotion is not None and move.promotion != chess.QUEEN:
        # Underpromotion planes
        promotions = [chess.ROOK, chess.KNIGHT, chess.BISHOP]
        promotion = 0
        for i in range(len(promotions)):
            if move.promotion == promotions[i]:
                promotion = i
        direction = dest_file - origin_file + 1  # left = 0, center = 1, right = 2
        plane = promotion * 3 + direction + 64  # 64 = Offset for being an underpromotion move
    elif (origin_file - dest_file)**2 + (origin_rank - dest_rank)**2 == 5:
        # Knight moves
        directions = [(2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2)]
        direction = 0
        for i in range(len(directions)):
            # If this is the correct direction
            if dest_file == origin_file + directions[i][1] and dest_rank == origin_rank + directions[i][0]:
                direction = i
        plane = direction + 56  # 56 = Offset for being a knight move
    else:
        # Queen moves
        directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        magnitude = max(abs(origin_file - dest_file), abs(origin_rank - dest_rank))
        direction = 0
        for i in range(len(directions)):
            # If this is the correct direction
            if dest_file == origin_file + magnitude * directions[i][1] and dest_rank == origin_rank + magnitude * directions[i][0]:
                direction = i
        plane = direction * 7 + magnitude
    return probs[8*8*plane + in_plane_index]


def smart_apply_move(state, move, player):
    state.applymove(move)
    if player == 2:
        return state.mirror()
    else:
        return state


def expand_and_eval(node, states, network):
    probs, value = network.evaluate(states)
    node.value = value[0][0]
    base_state = node.state
    if node.player == 2:  # If it is black's turn flip the board
        base_state = base_state.mirror()
    else:
        base_state = base_state.clone()
    moves = base_state.getallmoves()
    node.children = [Node(smart_apply_move(base_state, move, node.player), move,
                          get_prob_for_move(move, probs[0]), node) for move in moves]
    # At this point the probabilities aren't probabilities but they are just values


def perform_search(game_states, num_iterations, temperature, network):
    # root node (no action taken to get there, 100% prior probability, no parent)
    root = Node(game_states[-1], None, 1.0, None)

    for i in range(num_iterations):
        node = root
        # state = game_states[-1].clone()
        states = game_states.copy()

        # Select
        # Find a leaf node acording to the upper confidence bound
        while node.children:
            # Find the node that has the maximum upper confidence bound Q(s,a) + U(s,a) where
            # U(s,a) proportional to P(s,a)/(1+N(s,a))
            move_node = max(node.children, key=lambda child: child.avalue + child.prior/(1+child.visits))
            # Descend down the tree
            node = move_node
            # state.applymove(move_node.move)
            states.append(move_node.state.clone())

        expand_and_eval(node, states, network)
        value = node.value

        # Backup step
        while node is not None:
            node.visits += 1
            node.total_value += value
            node.avalue = node.total_value / node.visits
            node = node.parent

    #pick best return value
    prob_sum = 0.0
    power = 1.0 / temperature
    probs = {}
    for child in root.children:
        p = child.visits ** power
        prob_sum += p
        probs[child.action] = p
    if root.player == 2:
        return {mirror_move(move): prob / prob_sum for (move, prob) in probs.items()}
    return {move: prob/prob_sum for (move, prob) in probs.items()}


def mirror_move(move):
    return chess.Move(chess.square_mirror(move.from_square), chess.square_mirror(move.to_square), promotion=move.promotion, drop=move.drop)


def pick_action(move_probs):
    rand = random.random()
    total = 0.0
    for (move, prob) in move_probs.items():
        total += prob
        if rand <= total:
            return move
    return None # This shouldn't ever happen unless something goes terribly wrong
