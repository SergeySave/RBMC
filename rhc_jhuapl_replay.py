import requests
import re
import chess
from Chess import Chess


def chess_from_fen(fen):
    #state = Chess()
    #state.board = chess.Board(fen=fen)
    return fen


def get_replay(game_id, team):
    replay_result = requests.get("https://rbc.jhuapl.edu/games/" + str(game_id)).text
    regex_parts = re.findall(r'{\s*phase:\s*"move",\s*turn_number:\s*([\d]*),[\s\S]*?color:\s*"([a-zA-Z]*)",[\s\S]*?fen:\s*"([^"]*)",\s*}', replay_result)
    post_black_moves = filter(lambda tup: tup[1] == team, regex_parts)
    chess_boards = map(lambda tup: chess_from_fen(tup[2]), post_black_moves)
    if team == 'white':
        return [Chess().board.fen()] + list(chess_boards)
    else:
        return list(chess_boards)


if __name__ == "__main__":
    print(get_replay(57144, 'white'))
