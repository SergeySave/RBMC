
import tensorflow as tf

from Chess import Chess
from LeelaNetwork import LeelaNetwork
from net import Net
import tfprocess
import yaml

from policy_index import policy_index

if __name__ == "__main__":
    with open("leela_config.yml", "rb") as file:
        cfg = yaml.safe_load(file.read())

    net = Net()
    # net.parse_proto("weights_run1_42700.pb.gz")  # 2019-07-02 15:13:26 +00:00
    net.parse_proto("weights_run3_42872.pb.gz")  # 2019-09-09 03:25:41 +00:00

    filters, blocks = net.filters(), net.blocks()
    weights = net.get_weights()

    x = [
        tf.placeholder(tf.float32, [None, 112, 8 * 8]),
        tf.placeholder(tf.float32, [None, 1858]),
        tf.placeholder(tf.float32, [None, 3]),
        tf.placeholder(tf.float32, [None, 3]),
    ]

    tfp = tfprocess.TFProcess(cfg)
    tfp.init_net(x)
    tfp.replace_weights(weights)

    network = LeelaNetwork(tfp, x[0])
    board = Chess()
    y, z = network.evaluate([board])

    for move in board.getallmoves():
        if move is not None:
            i = policy_index.index(move.uci())
            print(board.board.san(move) + " : " + str(y[0, i]))

    for i in z:
        print(str(i))
