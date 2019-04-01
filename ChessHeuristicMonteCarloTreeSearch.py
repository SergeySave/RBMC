import math
import random
import chess


def mirror_move(move):
    return chess.Move(chess.square_mirror(move.from_square), chess.square_mirror(move.to_square), promotion=move.promotion, drop=move.drop)


class Node:
    def __init__(self, action, parent, state=None):
        self.action = action  # How did we get here? (only None for root)
        self.visits = 0.0  # visit count N(state, action)
        self.avalue = 0.0  # action-value Q(state, action)

        # Q(s, a) = total_value / N(s,a)
        self.total_value = 0.0  # sum of all reachable values

        self.parent = parent
        self.children = []
        if self.parent is not None:
            self.player = 3 - parent.player
        else:
            self.player = state.currentPlayer
        self.value = 0.0  # NN evaluation of the current.txt state V(state)


def expand_and_eval(node, state, heuristic):
    value = heuristic(state)
    node.value = value
    if node.player == 2:
        node.value = 1 - value
    # if node.player == 2:  # If it is black's turn flip the board
    # base_state = base_state.mirror()
    # else:
    #     base_state = base_state
    moves = state.getallmoves()
    node.children = [Node(move, node) for move in moves]
    # At this point the probabilities aren't probabilities but they are just values
    # if len(node.children) > 0:
    #     denominator = sum([math.exp(child.prior) for child in node.children])
    #     for child in node.children:
    #         child.prior = math.exp(child.prior)/denominator


def perform_search(s, num_iterations, temperature, exploration, heuristic, base_root=None):
    # root node (no action taken to get there, 100% prior probability, no parent)
    if base_root is None:
        root = Node(None, None, state=s)
    else:
        root = base_root
        root.parent = None

    for i in range(num_iterations):
        node = root

        state = s.clone()

        # Select
        # Find a leaf node acording to the upper confidence bound
        while node.children:
            # Find the node that has the maximum upper confidence bound Q(s,a) + U(s,a) where
            # U(s,a) = c * P(s,a) * (sum over all b N(s,b))/(1+N(s,a))
            move_node = max(node.children, key=lambda child: child.avalue + exploration * math.sqrt(node.visits - 1)/(1+child.visits))
            # Descend down the tree
            node = move_node
            state.applymove(node.action)

        expand_and_eval(node, state, heuristic)
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
        probs[child] = p
    return {(node.action, node): prob/prob_sum for (node, prob) in probs.items()}


def pick_action(move_probs):
    rand = random.random()
    total = 0.0
    for (move, prob) in move_probs.items():
        total += prob
        if rand <= total:
            return move
    return None  # This shouldn't ever happen unless something goes terribly wrong


if __name__ == "__main__":
    from Chess import Chess
    from Turn import material_heuristic
    game = Chess()
    print(game.tostring())

    game_states = []

    base_node = None

    while not game.isgameover():
        game_states.append(game.clone())
        move_probs = perform_search(game_states, 5000, 1.0, 1.4142135624, material_heuristic, base_node)
        move, node = pick_action(move_probs)
        base_node = node
        game.applymove(move)
        print(game.tostring())
