#!/usr/bin/env python3

"""
File Name:      online_game_player.py
Authors:        Sergey Savelyev
Date:           March 8th, 2019

Description:    Python file used to play a game of recon chess against rbc.jhuapl.edu/challenge
Source:         Adapted from play_game.py
"""

import argparse
import random
import chess

from human_agent import Human
from player import load_player
from game import Game
from datetime import datetime
import time
import requests
import re
import base64


def play_game(white_player, black_player, player_names):
    players = [black_player, white_player]

    game = Game()

    # writing to files
    time = "{}".format(datetime.today()).replace(" ", "_").replace(":", "-").replace(".", "-")
    filename_game = "GameHistory/" + time + "game_boards.txt"
    filename_true = "GameHistory/" + time + "true_boards.txt"
    output = open(filename_game, "w")
    output_true = open(filename_true, "w")
    output.write("Starting Game between {}-WHITE and {}-BLACK\n".format(player_names[0], player_names[1]))
    output_true.write("Starting Game between {}-WHITE and {}-BLACK\n".format(player_names[0], player_names[1]))

    white_player.handle_game_start(chess.WHITE, chess.Board())
    black_player.handle_game_start(chess.BLACK, chess.Board())
    game.start()

    move_number = 1
    while not game.is_over():
        if game.turn:
            output.write("##################################--WHITE's Turn [{}]\n".format(move_number))
            output.write("##################################--Current Board State\n")
            format_write_board(output, game.white_board)
            output_true.write("##################################--WHITE's Turn [{}]\n".format(move_number))

            print("WHITE's Turn [{}]".format(move_number))
            format_print_board(game.white_board)

        else:
            output.write("##################################--BLACK's Turn [{}]\n".format(move_number))
            output.write("##################################--Current Board State \n")
            format_write_board(output, game.black_board)
            output_true.write("##################################--BLACK's Turn [{}]\n".format(move_number))

            print("BLACK's Turn [{}]".format(move_number))
            format_print_board(game.black_board)

        output_true.write("##################################--Current Board State\n")
        format_write_board(output_true, game.truth_board)

        requested_move, taken_move = play_turn(game, players[game.turn], game.turn, move_number, output, output_true)
        print_game(game, move_number, game.turn, requested_move, taken_move)
        move_number += 1

        print("==================================\n")

    winner_color, winner_reason = game.get_winner()

    white_player.handle_game_end(winner_color, winner_reason)
    black_player.handle_game_end(winner_color, winner_reason)

    output.write("Game Over!\n")
    if winner_color is not None:
        output.write(winner_reason)
    else:
        output.write('Draw!')
    return winner_color, winner_reason


def play_turn(game, player, turn, move_number, output, output_true):
    possible_moves = game.get_moves()
    possible_sense = list(chess.SQUARES)

    # notify the player of the previous opponent's move
    captured_square = game.opponent_move_result()
    player.handle_opponent_move_result(captured_square is not None, captured_square)

    # play sense action
    sense = player.choose_sense(possible_sense, possible_moves, game.get_seconds_left())
    sense_result = game.handle_sense(sense)
    player.handle_sense_result(sense_result)
    print_sense(game, turn, sense)

    output.write("##################################--Sense Around Square {}\n".format(chess.SQUARE_NAMES[sense]))
    if turn:
        format_write_board(output, game.white_board)
    else:
        format_write_board(output, game.black_board)

    # play move action
    move = player.choose_move(possible_moves, game.get_seconds_left())
    requested_move, taken_move, captured_square, reason = game.handle_move(move)
    player.handle_move_result(requested_move, taken_move, captured_square is not None,
                              captured_square, reason)

    output.write("##################################--Move requested: {} -- Move taken: {}\n".format(requested_move, taken_move))
    output_true.write("##################################--Move requested: {} -- Move taken: {}\n\n".format(requested_move, taken_move))
    if turn:
        format_write_board(output, game.white_board)
    else:
        format_write_board(output, game.black_board)

    output.write("##################################--Truth Board State\n")
    format_write_board(output, game.truth_board)

    game.end_turn()
    return requested_move, taken_move


def print_game(game, move_number, turn, move_requested, move_taken):
    if not turn:
        print("[WHITE]-- Move requested: {} -- Move taken: {}".format(move_requested, move_taken))
        format_print_board(game.white_board)
    else:
        print("[BLACK]-- Move requested: {} -- Move taken: {}".format(move_requested, move_taken))
        format_print_board(game.black_board)


def print_sense(game, turn, sense):
    if turn:
        print("[WHITE]-- Sense Around Square {} --".format(chess.SQUARE_NAMES[sense]))
        format_print_board(game.white_board)
    else:
        print("[BLACK]-- Sense Around Square {} --".format(chess.SQUARE_NAMES[sense]))
        format_print_board(game.black_board)


def format_print_board(board):
    rows = ['8', '7', '6', '5', '4', '3', '2', '1']
    fen = board.board_fen()

    fb = "   A   B   C   D   E   F   G   H  "
    fb += rows[0]
    ind = 1
    for f in fen:
        if f == '/':
            fb += '|' + rows[ind]
            ind += 1
        elif f.isnumeric():
            for i in range(int(f)):
                fb += '|   '
        else:
            fb += '| ' + f + ' '
    fb += '|'

    ind = 0
    for i in range(9):
        for j in range(34):
            print(fb[ind], end='')
            ind += 1
        print('\n', end='')
    print("")


def format_write_board(out, board):
    rows = ['8', '7', '6', '5', '4', '3', '2', '1']
    fen = board.board_fen()

    fb = "   A   B   C   D   E   F   G   H  "
    fb += rows[0]
    ind = 1
    for f in fen:
        if f == '/':
            fb += '|' + rows[ind]
            ind += 1
        elif f.isnumeric():
            for i in range(int(f)):
                fb += '|   '
        else:
            fb += '| ' + f + ' '
    fb += '|'

    ind = 0
    for i in range(9):
        for j in range(34):
            out.write(fb[ind])
            ind += 1
        out.write('\n')
    out.write('\n')


def wait_for_turn():
    done = False
    while not done:
        is_over = requests.get("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/is_over",
                                headers={
                                    'Content-Type': 'application/json',
                                    'Authorization': 'Basic ' + base64.b64encode(
                                        (username + ":" + password).encode("utf-8")).decode("utf-8"),
                                }).json()["is_over"]
        if is_over:
            raise Exception("Game Over")
        else:
            is_my_turn = requests.get("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/is_my_turn",
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': 'Basic ' + base64.b64encode(
                                               (username + ":" + password).encode("utf-8")).decode("utf-8"),
                                       }).json()["is_my_turn"]
            if is_my_turn:
                done = True


def play():
    done = False
    while not done:
        wait_for_turn()
        opponent_move_results = requests.get("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/opponent_move_results",
                                                headers={
                                                    'Content-Type': 'application/json',
                                                    'Authorization': 'Basic ' + base64.b64encode(
                                                        (username + ":" + password).encode("utf-8")).decode("utf-8"),
                                                }).json()["opponent_move_results"]
        # TODO: handle results
        print(opponent_move_results)
        sense_actions = requests.get("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/sense_actions",
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Authorization': 'Basic ' + base64.b64encode(
                                             (username + ":" + password).encode("utf-8")).decode("utf-8"),
                                     }).json()["sense_actions"]

        # TODO: figure out possible_moves
        sense = player.choose_sense(sense_actions, [], 500)  # We do not use possible moves here
        sense_result = requests.post("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/sense",
                          json={
                              "square": sense,
                          },
                          headers={
                              'Content-Type': 'application/json',
                              'Authorization': 'Basic ' + base64.b64encode((username + ":" + password).encode("utf-8")).decode("utf-8"),
                          }).json()["sense_result"]
        # TODO: handle results
        print(sense_result)
        player.handle_sense_result([(sense_val[0], chess.Piece.from_symbol(sense_val[1]["value"]) if sense_val[1] is not None else None) for sense_val in sense_result])

        # This request is made because the webpage makes it
        move_actions = requests.get("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/move_actions",
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Authorization': 'Basic ' + base64.b64encode(
                                             (username + ":" + password).encode("utf-8")).decode("utf-8"),
                                     }).json()["move_actions"]
        move = player.choose_move([], 500)  # We do not use possible moves here either
        move_result = requests.post("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/move",
                                     data=("{\"requested_move\":{\"type\":\"Move\",\"value\":\"" + move.uci() + "\"}}").encode("utf-8"),
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Authorization': 'Basic ' + base64.b64encode(
                                             (username + ":" + password).encode("utf-8")).decode("utf-8"),
                                     }).json()["move_result"]
        print(move_result)
        player.handle_move_result(chess.Move.from_uci(move_result[0]["value"]),
                                  chess.Move.from_uci(move_result[1]["value"]) if move_result[1] is not None else None,
                                  move_result[2] is not None,
                                  move_result[2])
        requests.post("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/end_turn",
                     json={},
                     headers={
                         'Content-Type': 'application/json',
                         'Authorization': 'Basic ' + base64.b64encode(
                             (username + ":" + password).encode("utf-8")).decode("utf-8"),
                     })
        is_over = requests.get("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/is_over",
                               headers={
                                   'Content-Type': 'application/json',
                                   'Authorization': 'Basic ' + base64.b64encode(
                                       (username + ":" + password).encode("utf-8")).decode("utf-8"),
                               }).json()["is_over"]
        if is_over:
            done = True


if __name__ == '__main__':
    player = Human()
    basic_res = requests.get("https://rbc.jhuapl.edu/play/white/2")
    http_text = basic_res.text
    username = (re.search(r'.*username = "(.*)";.*', http_text).group(1))
    password =(re.search(r'.*password = "(.*)";.*', http_text).group(1))
    opponent = (re.search(r'.*opponent = "(.*)";.*', http_text).group(1))
    color = (re.search(r'.*color = (.*);.*', http_text).group(1)) == "true"
    registration = requests.post("https://rbc.jhuapl.edu/api/users",
                                  json={
                                      "username": username,
                                      "email": "",
                                      "affiliation": "None",
                                      "password": password,
                                  },
                                  headers={
                                      'Content-Type': 'application/json',
                                      'Authorization': 'Basic ' + base64.b64encode((username + ":" + password).encode("utf-8")).decode("utf-8"),
                                  }).json()
    invite = requests.post("https://rbc.jhuapl.edu/api/invitations",
                          json={
                              "opponent": opponent,
                              "color": color,
                          },
                          headers={
                              'Content-Type': 'application/json',
                              'Authorization': 'Basic ' + base64.b64encode((username + ":" + password).encode("utf-8")).decode("utf-8"),
                          }).json()
    game_id = invite["game_id"]
    player_color = requests.get("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/color",
                          headers={
                              'Content-Type': 'application/json',
                              'Authorization': 'Basic ' + base64.b64encode((username + ":" + password).encode("utf-8")).decode("utf-8"),
                          }).json()
    starting_board = requests.get("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/starting_board",
                          headers={
                              'Content-Type': 'application/json',
                              'Authorization': 'Basic ' + base64.b64encode((username + ":" + password).encode("utf-8")).decode("utf-8"),
                          }).json()
    ready = requests.post("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/ready",
                          headers={
                              'Content-Type': 'application/json',
                              'Authorization': 'Basic ' + base64.b64encode((username + ":" + password).encode("utf-8")).decode("utf-8"),
                          }).json()
    play()

    print("https://rbc.jhuapl.edu/games/" + str(game_id))
else:
    parser = argparse.ArgumentParser(description='Allows you to play against an online bot.')
    parser.add_argument('local_path', help='Path to bot source file.')
    parser.add_argument('online_player', help='Online player name.')
    # parser.add_argument('--color', default='white', choices=['white', 'black', 'random'],
    #                     help='The color you want to play as.')
    args = parser.parse_args()

    name, constructor = load_player(args.local_path)
    player = constructor()
    online_name = args.online_player

    player_names = [name, online_name]

    win_color, win_reason = play_game(players[0], players[1], player_names)

    print('Game Over!')
    if win_color is not None:
        print(win_reason)
    else:
        print('Draw!')
