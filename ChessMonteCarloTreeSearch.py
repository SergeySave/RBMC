import math
import random
import chess
from Network import get_move_index, mirror_move


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
    return probs[get_move_index(move)]


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
                          get_prob_for_move(move, probs[0])/10, node) for move in moves]
    # At this point the probabilities aren't probabilities but they are just values
    if len(node.children) > 0:
        denominator = sum([math.exp(child.prior) for child in node.children])
        for child in node.children:
            child.prior = math.exp(child.prior)/denominator


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


def pick_action(move_probs):
    rand = random.random()
    total = 0.0
    for (move, prob) in move_probs.items():
        total += prob
        if rand <= total:
            return move
    return None # This shouldn't ever happen unless something goes terribly wrong
