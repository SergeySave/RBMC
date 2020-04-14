import sys
sys.path.insert(0, "../reconchess-strangefish/")

import chess
from reconchess import LocalGame, play_local_game
from strangefish import StrangeFish
from strangefish.strategies import multiprocessing_strategies

from rbmc.RBMCNetworkManager import *
from rbmc.RBMCPlayer import *

def main():
    game = LocalGame(seconds_per_player=1e10)

    network = NetworkManager().load_recent_network()

    our_agent = RBMCAgent(network)

    try:
        winner_color, win_reason, history = play_local_game(
            our_agent,
            StrangeFish(*multiprocessing_strategies.create_strategy()),
            game=game
        )

        winner = 'Draw' if winner_color is None else chess.COLOR_NAMES[winner_color]
    except:
        traceback.print_exc()
        game.end()

        winner = 'ERROR'
        history = game.get_game_history()

    print('Game Over!')
    print('Winner: {}!'.format(winner))

    timestamp = datetime.now().strftime('%Y_%m_%d-%H_%M_%S')

    replay_path = '{}-{}-{}-{}.json'.format(white_bot_name, black_bot_name, winner, timestamp)
    print('Saving replay to {}...'.format(replay_path))
    history.save(replay_path)


if __name__ == '__main__':
    main()
