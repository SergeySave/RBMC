import numpy as np
import chess
from Constants import *


class LeelaNetwork:
    def __init__(self, tfprocess, x):
        self.tfp = tfprocess
        self.x = x

    def evaluate(self, states):
        return self.tfp.session.run([self.tfp.y_conv, self.tfp.z_conv], {
            self.x: np.array([convert_states(states)]),
            "Training:0": False
        })

    def get_move_index(self, move):
        return None


def convert_states(states):
    kMoveHIstory = 8
    kPlanesPerBoard = 13
    kAuxPlaneBase = kPlanesPerBoard * kMoveHIstory
    input_planes = np.empty((kAuxPlaneBase+8, N*N))

    current_board = states[-1].board
    we_are_black = False
    if states[-1].currentPlayer == 2:
        current_board = current_board.mirror()
        we_are_black = True

    # no_progress = get_current_repetition_count(current_board)
    castling = current_board.castling_rights

    # Our Queenside
    if bool(castling & chess.BB_A1):
        input_planes[kAuxPlaneBase + 0] = np.repeat(1, N*N)
    # Our Kingside
    if bool(castling & chess.BB_H1):
        input_planes[kAuxPlaneBase + 1] = np.repeat(1, N*N)
    # Them Queenside
    if bool(castling & chess.BB_A8):
        input_planes[kAuxPlaneBase + 2] = np.repeat(1, N*N)
    # Them Kingside
    if bool(castling & chess.BB_H8):
        input_planes[kAuxPlaneBase + 3] = np.repeat(1, N*N)
    # Are we black
    if bool(we_are_black):
        input_planes[kAuxPlaneBase + 4] = np.repeat(1, N*N)
    # No Capture Ply
    input_planes[kAuxPlaneBase + 5] = np.repeat(states[-1].no_capture_ply, N*N)
    # 6 is all zeros
    input_planes[kAuxPlaneBase + 6] = np.repeat(0, N*N)
    # 7 is all ones
    input_planes[kAuxPlaneBase + 7] = np.repeat(1, N*N)

    flip = False
    history_index = len(states) - 1
    for i in range(8):
        board = states[max(history_index, 0)]
        our_color = chess.WHITE if board.currentPlayer == 1 else chess.BLACK
        their_color = chess.BLACK if board.currentPlayer == 1 else chess.WHITE

        base = i * kPlanesPerBoard
        input_planes[base + 0] = np.unpackbits(np.array([board.board.pieces_mask(chess.PAWN, our_color)], ">u8")
                                               .view(np.uint8)).reshape((8, 8)).T.reshape((-1))[::-1]
        input_planes[base + 1] = np.unpackbits(np.array([board.board.pieces_mask(chess.KNIGHT, our_color)], ">u8")
                                               .view(np.uint8)).reshape((8, 8)).T.reshape((-1))[::-1]
        input_planes[base + 2] = np.unpackbits(np.array([board.board.pieces_mask(chess.BISHOP, our_color)], ">u8")
                                               .view(np.uint8)).reshape((8, 8)).T.reshape((-1))[::-1]
        input_planes[base + 3] = np.unpackbits(np.array([board.board.pieces_mask(chess.ROOK, our_color)], ">u8")
                                               .view(np.uint8)).reshape((8, 8)).T.reshape((-1))[::-1]
        input_planes[base + 4] = np.unpackbits(np.array([board.board.pieces_mask(chess.QUEEN, our_color)], ">u8")
                                               .view(np.uint8)).reshape((8, 8)).T.reshape((-1))[::-1]
        input_planes[base + 5] = np.unpackbits(np.array([board.board.pieces_mask(chess.KING, our_color)], ">u8")
                                               .view(np.uint8)).reshape((8, 8)).T.reshape((-1))[::-1]

        input_planes[base + 6] = np.unpackbits(np.array([board.board.pieces_mask(chess.PAWN, their_color)], ">u8")
                                               .view(np.uint8)).reshape((8, 8)).T.reshape((-1))[::-1]
        input_planes[base + 7] = np.unpackbits(np.array([board.board.pieces_mask(chess.KNIGHT, their_color)], ">u8")
                                               .view(np.uint8)).reshape((8, 8)).T.reshape((-1))[::-1]
        input_planes[base + 8] = np.unpackbits(np.array([board.board.pieces_mask(chess.BISHOP, their_color)], ">u8")
                                               .view(np.uint8)).reshape((8, 8)).T.reshape((-1))[::-1]
        input_planes[base + 9] = np.unpackbits(np.array([board.board.pieces_mask(chess.ROOK, their_color)], ">u8")
                                               .view(np.uint8)).reshape((8, 8)).T.reshape((-1))[::-1]
        input_planes[base + 10] = np.unpackbits(np.array([board.board.pieces_mask(chess.QUEEN, their_color)], ">u8")
                                               .view(np.uint8)).reshape((8, 8)).T.reshape((-1))[::-1]
        input_planes[base + 11] = np.unpackbits(np.array([board.board.pieces_mask(chess.KING, their_color)], ">u8")
                                               .view(np.uint8)).reshape((8, 8)).T.reshape((-1))[::-1]

        # As we don't really care about repetitions I will ignore them for now
        input_planes[base + 12] = np.repeat(0, N*N)

        if history_index < 0 and board.board.ep_square is not None:
            idx = 1 << board.board.ep_square
            if idx < 8:
                input_planes[base + 0] += np.unpackbits(np.array([
                    ((0x0000000000000100 - 0x0000000001000000) << idx)
                ], ">u8").view(np.uint8)).reshape((8, 8)).T.reshape((-1))[::-1]
            else:
                input_planes[base + 0] += np.unpackbits(np.array([
                    ((0x0001000000000000 - 0x0000000100000000) << (idx - 56))
                ], ">u8").view(np.uint8)).reshape((8, 8)).T.reshape((-1))[::-1]

        if history_index > 0:
            flip = not flip
        history_index -= 1

    return input_planes
