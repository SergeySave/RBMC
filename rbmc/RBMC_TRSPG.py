from rbmc.RBMCTrackingRandomAgent import *
from rbmc.game import Game


def play_turn(game, player):
    possible_moves = game.get_moves()
    possible_sense = list(chess.SQUARES)

    captured_square = game.opponent_move_result()
    player.handle_opponent_move_result(captured_square is not None, captured_square)

    sense = player.choose_sense(possible_sense, possible_moves, game.get_seconds_left())
    sense_result = game.handle_sense(sense)
    player.handle_sense_result(sense_result)

    move = player.choose_move(possible_moves, game.get_seconds_left())
    requested_move, taken_move, captured_square, reason = game.handle_move(move)
    player.handle_move_result(requested_move, taken_move, captured_square is not None, captured_square, reason)

    game.end_turn()
    return requested_move, taken_move


def generate_game():

    white_player = RBMCTrackingRandomAgent()
    black_player = RBMCTrackingRandomAgent()

    players = [black_player, white_player]

    game = Game()

    white_player.handle_game_start(chess.WHITE, chess.Board())
    black_player.handle_game_start(chess.BLACK, chess.Board())
    game.start()

    move_number = 1
    while not game.is_over():
        requested_move, taken_move = play_turn(game, players[game.turn])
        move_number += 1

    winner_color, winner_reason = game.get_winner()

    result_value = 1.0 if winner_color == chess.WHITE else (0.0 if winner_color == chess.BLACK else 0.5)

    white_data = white_player.handle_game_end()
    black_data = black_player.handle_game_end()

    return white_data, black_data, result_value


def generate_self_play_games(num_games):
    for i in range(num_games):
        white_data, black_data, result = generate_game()
        # game_mangr.save_game(white_data[0], white_data[1], result, white_data[2], 1) # Save White Things
        # game_mangr.save_game(black_data[0], black_data[1], 1-result, black_data[2], 2) # Save Black Things


def main():
    while True:
        generate_self_play_games(1)
