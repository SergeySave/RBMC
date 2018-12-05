import math
import random


class Node:
    def __init__(self, state, move=None, parent=None):
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0.0
        self.visits = 0.0
        self.untried_moves = state.getallmoves()
        self.player = state.currentPlayer


def perform_search(root_state, num_iterations, exploration, pre_node=None):
    if pre_node is None:
        root = Node(root_state)
    else:
        root = pre_node
        root.parent = None  # Prevent backprop from updating stuff we don't care about anymore
    for i in range(num_iterations):  # Repeat numIterations times
        node = root
        state = root_state.clone()

        # Select
        # If we don't have new moves and we have children to go to
        while node.untried_moves == [] and node.children != []:
            # Find the node that has the maximum value for the function given on the wikipedia article for MCTS
            move_node = max(node.children, key=lambda child: child.wins / child.visits +
                            exploration * math.sqrt(math.log(node.visits) / child.visits))
            # Descend down the tree
            node = move_node
            state.applymove(move_node.move)

        # Expand
        if node.untried_moves:
            # Pick a random move
            move = random.choice(node.untried_moves)
            # Remove the node from the list
            node.untried_moves.remove(move)

            # Apply the move
            state.applymove(move)
            # State isn't stored so we don't need to clone it
            new_node = Node(state, move=move, parent=node)
            node.children.append(new_node)
            node = new_node

        # Rollout
        while not state.isgameover:  # Find a terminal state
            state.applymove(random.choice(state.getallmoves()))

        # Backpropagation
        board_states = [state.getboardstate(1), state.getboardstate(2)]
        while node is not None:
            node.visits += 1
            node.wins += board_states[node.player - 1]
            node = node.parent

    best_move = max(root.children, key=lambda child: child.visits)
    return best_move.move, best_move

# Q-learning
# Q(s, a) = r(s,a) + gamma * max of a' (Q(s', a'))