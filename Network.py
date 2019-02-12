import chess
import numpy as np
from keras.layers import Input, Conv2D, BatchNormalization, ReLU, add, Dense, Activation, Flatten
from keras.models import Model
from keras.models import load_model
from keras.optimizers import SGD
from keras.regularizers import l2

from Constants import *


def residual_block(previous):
    # A convolution of 256 filters of kernel size 3 × 3 with stride 1
    conv1 = Conv2D(256, kernel_size=3, strides=1, activation='relu', kernel_regularizer=l2(REG_PARAM), padding="same")(previous)
    norm1 = BatchNormalization()(conv1)  # Batch normalisation
    rnln1 = ReLU()(norm1)  # A rectifier non-linearity
    # A convolution of 256 filters of kernel size 3 × 3 with stride 1
    conv2 = Conv2D(256, kernel_size=3, strides=1, activation='relu', kernel_regularizer=l2(REG_PARAM), padding="same")(rnln1)
    norm2 = BatchNormalization()(conv2)  # Batch normalisation
    skip = add([norm2, previous])  # A skip connection that adds the input to the block
    rnln2 = ReLU()(skip)  # A rectifier non-linearity
    return rnln2


class Network:
    def __init__(self, model=None):
        self.input = Input(shape=(N, N, M*T + L))
        if model is None:
            # A convolution of 256 filters of kernel size 3 × 3 with stride 1
            conv = Conv2D(256, kernel_size=3, strides=1, activation='relu', kernel_regularizer=l2(REG_PARAM), padding="same", input_shape=(N, N, M*T + L))(self.input)
            norm = BatchNormalization()(conv)  # Batch normalisation
            rnln = ReLU()(norm)  # A rectifier non-linearity

            tower = rnln
            for i in range(RESIDUAL_BLOCKS):
                tower = residual_block(tower)

            # A convolution of 2 filters of kernel size 1 × 1 with stride 1
            policy_conv = Conv2D(2, kernel_size=1, strides=1, activation='relu', kernel_regularizer=l2(REG_PARAM), padding="same")(tower)
            policy_norm = BatchNormalization()(policy_conv)  # Batch normalisation
            policy_rnln = ReLU()(policy_norm)  # A rectifier non-linearity
            # Make sure the output size is correct
            policy_flat = Flatten()(policy_rnln)
            # A fully connected linear layer that outputs a vector of size 192 + 1 = 362 corresponding to logit
            # probabilities for all intersections and the pass move
            policy_dout = Activation(activation='tanh')(Dense(73 * N * N, kernel_regularizer=l2(REG_PARAM))(policy_flat))

            # A convolution of 1 filter of kernel size 1 × 1 with stride 1
            value_conv = Conv2D(1, kernel_size=1, strides=1, activation='relu', kernel_regularizer=l2(REG_PARAM), padding="same")(tower)
            value_norm = BatchNormalization()(value_conv)  # Batch normalisation
            value_rnln1 = ReLU()(value_norm)  # A rectifier non-linearity
            # Make sure the output size is correct
            value_flat = Flatten()(value_rnln1)
            # A fully connected linear layer to a hidden layer of size 256
            value_dense = Dense(256, kernel_regularizer=l2(REG_PARAM))(value_flat)
            value_rnln2 = ReLU()(value_dense)  # A rectifier non-linearity
            # A fully connected linear layer to a scalar
            value_scalar = Dense(1, kernel_regularizer=l2(REG_PARAM))(value_rnln2)
            # A tanh non-linearity outputting a scalar in the range [−1, 1]
            value_out = Activation(activation='tanh')(value_scalar)

            self.model = Model(inputs=self.input, outputs=[policy_dout, value_out])
        else:
            self.model = model

    def compile(self):
        opt = SGD(lr=LEARNING_RATE, momentum=MOMENTUM)
        self.model.compile(optimizer=opt, loss=['categorical_crossentropy', 'mean_squared_error'], metrics=['accuracy'])

    def evaluate(self, states):
        return self.model.predict(np.array([convert_states(states)]), batch_size=1)

    def save(self, file_name):
        self.model.save(file_name)


def load_network(file_name):
    return Network(load_model(file_name))


def convert_states(states):
    input_planes = np.empty((N, N, M*T + L))

    current_board = states[-1].board
    if states[-1].currentPlayer == 2:
        current_board = current_board.mirror()

    # no_progress = get_current_repetition_count(current_board)
    castling = current_board.castling_rights

    # fill current_board input planes
    for i in range(T):
        if len(states) > i:
            # This plane exists we must fill it
            # Get the piece planes
            input_planes[:, :, (-L - M*(i + 1)):(-L - M*i)] = get_piece_planes(states[-i].board, states[-1].currentPlayer == 2)

            # No repetition planes: not really sure how to create them
            # Get the repetition
            # input_planes[(-L - M * i - 2):(-L - M * i)] = get_piece_planes(states[-i])
        else:
            # Before the game started: empty planes
            input_planes[:, :, (-L - M*(i + 1)):(-L - M*i)] = 0

    # Player 1 = 0, Player 2 = 1
    input_planes[:, :, -7] = np.repeat(states[-1].currentPlayer - 1, N*N).reshape((N, N))  # Player color
    input_planes[:, :, -6] = np.repeat(states[-1].board.fullmove_number, N*N).reshape((N, N))  # Total move count
    input_planes[:, :, -5] = np.repeat(int(bool(castling & chess.BB_A1)), N*N).reshape((N, N))  # Player 1 castling
    input_planes[:, :, -4] = np.repeat(int(bool(castling & chess.BB_A8)), N*N).reshape((N, N))  # Player 8 castling
    input_planes[:, :, -3] = np.repeat(int(bool(castling & chess.BB_H1)), N*N).reshape((N, N))  # Opponent 1 castling
    input_planes[:, :, -2] = np.repeat(int(bool(castling & chess.BB_H8)), N*N).reshape((N, N))  # Opponent 8 castling
    input_planes[:, :, -1] = np.repeat(current_board.halfmove_clock, N*N).reshape((N, N))  # No progress count
    return input_planes


def convert_move_probs(move_probs, do_mirror_move):
    network_values = np.zeros((73*N*N))
    if do_mirror_move:
        for move, prob in move_probs.items():
            network_values[get_move_index(mirror_move(move))] = prob
    else:
        for move, prob in move_probs.items():
            network_values[get_move_index(move)] = prob
    return network_values


def get_move_index(move):
    in_plane_index = move.from_square
    origin_file = chess.square_file(in_plane_index)
    origin_rank = chess.square_rank(in_plane_index)
    dest_file = chess.square_file(move.to_square)
    dest_rank = chess.square_rank(move.to_square)
    plane = -1 # should error if this stays -1
    if move.promotion is not None and move.promotion != chess.QUEEN:
        # Underpromotion planes
        promotions = [chess.ROOK, chess.KNIGHT, chess.BISHOP]
        promotion = 0
        for i in range(len(promotions)):
            if move.promotion == promotions[i]:
                promotion = i
        direction = dest_file - origin_file + 1  # left = 0, center = 1, right = 2
        plane = promotion * 3 + direction + 64  # 64 = Offset for being an underpromotion move
    elif (origin_file - dest_file)**2 + (origin_rank - dest_rank)**2 == 5:
        # Knight moves
        directions = [(2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2)]
        direction = 0
        for i in range(len(directions)):
            # If this is the correct direction
            if dest_file == origin_file + directions[i][1] and dest_rank == origin_rank + directions[i][0]:
                direction = i
        plane = direction + 56  # 56 = Offset for being a knight move
    else:
        # Queen moves
        directions = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
        magnitude = max(abs(origin_file - dest_file), abs(origin_rank - dest_rank))
        direction = 0
        for i in range(len(directions)):
            # If this is the correct direction
            if dest_file == origin_file + magnitude * directions[i][1] and dest_rank == origin_rank + magnitude * directions[i][0]:
                direction = i
        plane = direction * 7 + magnitude
    return 8*8*plane + in_plane_index


def get_piece_planes(board, mirror):
    fen_order = "KQRBNPkqrbnp"  # Possible optimization: Make this a dictionary
    state = fix_fen(board.fen())
    result = np.zeros((N, N, 12))
    if mirror:
        for rank in range(N):
            for file in range(N):
                piece = state[rank * N + file]
                if piece.isalpha():
                    result[7 - rank][file][fen_order.find(piece)] = 1
    else:
        for rank in range(N):
            for file in range(N):
                piece = state[rank * N + file]
                if piece.isalpha():
                    result[rank][file][fen_order.find(piece)] = 1
    return result


def mirror_move(move):
    return chess.Move(chess.square_mirror(move.from_square), chess.square_mirror(move.to_square), promotion=move.promotion, drop=move.drop)


def fix_fen(fen):
    fen = fen.split(" ")[0]
    fen = fen.replace("2", "11")
    fen = fen.replace("3", "111")
    fen = fen.replace("4", "1111")
    fen = fen.replace("5", "11111")
    fen = fen.replace("6", "111111")
    fen = fen.replace("7", "1111111")
    fen = fen.replace("8", "11111111")
    return fen.replace("/", "")
