
import tensorflow as tf
from net import Net
import tfprocess
import yaml

if __name__ == "__main__":
    with open("leela_config.yml", "rb") as file:
        cfg = yaml.safe_load(file.read())

    net = Net()
    net.parse_proto("weights_run1_42700.pb.gz")

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
    print(tfp)
