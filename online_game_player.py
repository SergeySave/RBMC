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

from my_agent import MyAgent
from player import load_player
from game import Game
from datetime import datetime
import time
import requests
import re
import base64
from rhc_jhuapl_replay import get_replay
from time import sleep


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
            return True
        else:
            sleep(0.025)
            is_my_turn = requests.get("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/is_my_turn",
                                       headers={
                                           'Content-Type': 'application/json',
                                           'Authorization': 'Basic ' + base64.b64encode(
                                               (username + ":" + password).encode("utf-8")).decode("utf-8"),
                                       }).json()["is_my_turn"]
            if is_my_turn:
                done = True
            else:
                sleep(0.025)
    return False


def play():
    player.handle_game_start(chess.WHITE if color else chess.BLACK, chess.Board())
    done = False
    while not done:
        if wait_for_turn():
            break
        opponent_move_results = requests.get("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/opponent_move_results",
                                                headers={
                                                    'Content-Type': 'application/json',
                                                    'Authorization': 'Basic ' + base64.b64encode(
                                                        (username + ":" + password).encode("utf-8")).decode("utf-8"),
                                                }).json()["opponent_move_results"]
        #print(opponent_move_results)
        player.handle_opponent_move_result(opponent_move_results is not None, opponent_move_results)
        sense_actions = requests.get("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/sense_actions",
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Authorization': 'Basic ' + base64.b64encode(
                                             (username + ":" + password).encode("utf-8")).decode("utf-8"),
                                     }).json()["sense_actions"]

        seconds_left = requests.get("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/seconds_left",
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Authorization': 'Basic ' + base64.b64encode(
                                             (username + ":" + password).encode("utf-8")).decode("utf-8"),
                                     }).json()["seconds_left"]
        sense = player.choose_sense(sense_actions, [], seconds_left)  # We do not use possible moves here
        sense_result = requests.post("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/sense",
                          json={
                              "square": sense,
                          },
                          headers={
                              'Content-Type': 'application/json',
                              'Authorization': 'Basic ' + base64.b64encode((username + ":" + password).encode("utf-8")).decode("utf-8"),
                          }).json()["sense_result"]
        #print(sense_result)
        player.handle_sense_result([(sense_val[0], chess.Piece.from_symbol(sense_val[1]["value"]) if sense_val[1] is not None else None) for sense_val in sense_result])

        # This request is made because the webpage makes it
        move_actions = requests.get("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/move_actions",
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Authorization': 'Basic ' + base64.b64encode(
                                             (username + ":" + password).encode("utf-8")).decode("utf-8"),
                                     }).json()["move_actions"]
        seconds_left = requests.get("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/seconds_left",
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Authorization': 'Basic ' + base64.b64encode(
                                             (username + ":" + password).encode("utf-8")).decode("utf-8"),
                                     }).json()["seconds_left"]
        move = player.choose_move([], float(seconds_left))  # We do not use possible moves here either
        data_str = "{\"requested_move\":" + (("{\"type\":\"Move\",\"value\":" + "\"" + move.uci() + "\"" + "}") if move is not None and move != move.null() else "null") + "}"

        move_respns = requests.post("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/move",
                                     data=data_str.encode("utf-8"),
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Authorization': 'Basic ' + base64.b64encode(
                                             (username + ":" + password).encode("utf-8")).decode("utf-8"),
                                     })
        move_result = move_respns.json()["move_result"]
        player.handle_move_result(chess.Move.from_uci(move_result[0]["value"]) if move_result[0] is not None else chess.Move.null(),
                                  chess.Move.from_uci(move_result[1]["value"]) if move_result[1] is not None else chess.Move.null(),
                                  move_result[2] is not None,
                                  move_result[2], "")
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
    player = MyAgent()
    basic_res = requests.get("https://rbc.jhuapl.edu/play/white/4")
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
    print("https://rbc.jhuapl.edu/games/" + str(game_id))
    play()

    # If this is true, white won
    winner_color = requests.get("https://rbc.jhuapl.edu/api/games/" + str(game_id) + "/winner_color",
                                     headers={
                                         'Content-Type': 'application/json',
                                         'Authorization': 'Basic ' + base64.b64encode(
                                             (username + ":" + password).encode("utf-8")).decode("utf-8"),
                                     }).json()["winner_color"]

    print(winner_color)
    player.handle_game_end(get_replay(game_id, 'white'))
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
