
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
    y, z = network.evaluate([Chess()])

    for i in range(len(policy_index)):
        print(policy_index[i] + " : " + y[i])

    for i in z:
        print(i)
