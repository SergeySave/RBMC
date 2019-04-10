

class Agent:
    def choose_move(self, states):
        pass


class RandomAgent(Agent):
    def choose_move(self, states):
        import random
        return random.choice(list(states[-1].board.legal_moves))


class NetworkAgent(Agent):

    def __init__(self, network, iterations):
        self.network = network
        self.iterations = iterations

    def choose_move(self, states):
        from ChessMonteCarloTreeSearch import  perform_search, pick_action
        from Constants import EXPLORATION
        from Network import mirror_move
        probs = perform_search(states, self.iterations, 0.01, EXPLORATION, self.network)
        move, _ = pick_action(probs)
        if (states[-1].currentPlayer == 1):
            return move
        else:
            return mirror_move(move)


def evaluate(white_agent, black_agent):
    from Chess import Chess

    game = Chess()

    game_states = []

    while not game.isgameover():
        game_states.append(game.clone())
        agent = white_agent if (game.currentPlayer == 1) else black_agent
        move = agent.choose_move(game_states)
        game.applymove(move)
        print(game.tostring())

    return game.getboardstate(1)


if __name__ == "__main__":
    from Network import load_network
    from Constants import EVAL_PER_MOVE as ITERATIONS

    EVALUATIONS = 100
    COMPARISON_AGENT = RandomAgent()
    NETWORK_NUMS = [5521, 6500, 7500, 8500, 9500, 10500, 11500]
    NETWORKS = [load_network("input/network_weights" + str(network_num) + ".h5") for network_num in NETWORK_NUMS]

    network_agent = NetworkAgent(None, ITERATIONS)
    for i in range(EVALUATIONS):
        print("Starting evaluation " + str(i))
        for j in range(len(NETWORK_NUMS)):
            print("Evaluating network " + str(j))
            network_agent.network = NETWORKS[j]
            if i % 2 == 0:
                result = 1 - evaluate(COMPARISON_AGENT, network_agent)
            else:
                result = evaluate(network_agent, COMPARISON_AGENT)
            with open("output/eval/" + str(NETWORK_NUMS[j]) + "/" + str(i) + ".txt", 'w') as file:
                file.writelines([str(result)])

