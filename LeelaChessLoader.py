
import proto.net_pb2 as net_pb2
import tensorflow as tf
import struct

CPU = True
floatDataType = tf.float32
kInputPlanes = 112


def make_const(values, shape=None, order=None):
    if order is None:
        return tf.constant(values, shape=shape, dtype=floatDataType)
    else:
        return tf.transpose(tf.constant(values, shape=shape, dtype=floatDataType), order)


def make_conv_block(input_layer, channels, input_channels, output_channels, weights, mixin=None):
    data_format = "NHWC" if CPU else "NCHW"

    w_conv = make_const(list(struct.iter_unpack("H", weights.weights.params)),
                        shape=[channels, channels, input_channels, output_channels])

    b_conv = make_const(list(struct.iter_unpack("H", weights.biases.params)), shape=[output_channels])
    conv2d = tf.nn.conv2d(input_layer, w_conv, (1, 1, 1, 1), "SAME",
                          data_format=data_format, dilations=(1, 1, 1, 1))

    bn_means = make_const(list(struct.iter_unpack("H", weights.bn_means.params)), shape=[output_channels])
    means = tf.math.subtract(bn_means, b_conv)

    batch_norm = tf.nn.fused_batch_norm(conv2d,
                                        make_const([1], shape=[output_channels]),
                                        make_const([0], shape=[output_channels]),
                                        means,
                                        make_const(list(struct.iter_unpack("H", weights.bn_stddivs.params)), shape=[output_channels]),
                                        data_format=data_format,
                                        is_training=False,
                                        epsilon=1.0000001e-5)[0]  # .y

    if mixin is not None:
        batch_norm = tf.math.add(batch_norm, mixin)

    return tf.nn.relu(batch_norm)


def make_residual_block(input_layer, channels, weights):
    block1 = make_conv_block(input_layer, 3, channels, channels, weights.conv1)
    block2 = make_conv_block(block1, 3, channels, channels, weights.conv2, input_layer)
    return block2


def make_network(weights, input_layer):
    uint16iter = struct.iter_unpack("H", weights.input.weights.params)
    length = sum(1 for _ in uint16iter)
    filters = length / kInputPlanes / 9

    flow = make_conv_block(input_layer, 3, kInputPlanes, filters, weights.input)

    for block in weights.residual:
        flow = make_residual_block(flow, filters, block)

    conv_pol = make_conv_block(flow, 1, filters, 32, weights.policy)
    conv_pol = tf.reshape(conv_pol, [None, 32 * 8 * 8])
    if CPU:
        ip_pol_w = make_const(weights.ip_pol_w, order=(3, 2, 0, 1))
    else:
        ip_pol_w = make_const(weights.ip_pol_w, order=(3, 0, 1, 2))
    ip_pol_b = make_const(weights.ip_pol_b)
    policy_fc = tf.math.add(tf.linalg.matmul(conv_pol, ip_pol_w), ip_pol_b)

    conv_val = make_conv_block(flow, 1, filters, 32, weights.value)
    conv_val = tf.reshape(conv_val, [None, 32 * 8 * 8])
    if CPU:
        ip1_val_w = make_const(weights.ip1_val_w, order=[3, 2, 0, 1])
    else:
        ip1_val_w = make_const(weights.ip1_val_w, order=[3, 0, 1, 2])
    ip1_val_w = tf.reshape(ip1_val_w, [32 * 8 * 8, 128])
    ip1_val_b = make_const(weights.ip_1_val_b)
    value_flow = tf.keras.layers.ReLU(tf.math.add(tf.linalg.matmul(conv_val, ip1_val_w), ip1_val_b))
    ip2_val_w = make_const(weights.ip2_val_w)
    ip2_val_b = make_const(weights.ip2_val_b)
    value_head = tf.math.tanh(tf.math.add(tf.linalg.matmul(value_flow, ip2_val_w), ip2_val_b))

    return policy_fc, value_head


class LeelaNetwork:
    def __init__(self):
        net = net_pb2.Net()

        with open("weights_run1_42700.pb", "rb") as file:
            net.ParseFromString(file.read())

        # lc0/network_tf.cc#269 - TFNetwork constructor
        legacy_weights_param = net.weights  # this is simply a wrapper in the c code

        if CPU:
            config = tf.ConfigProto(device_count={'GPU': 0})
        else:
            config = tf.ConfigProto()
            config.gpu_options.allow_growth = True

        self.session = tf.Session(config=config)

        if CPU:
            self.input = tf.placeholder(floatDataType, shape=(None, 8, 8, kInputPlanes))
        else:
            self.input = tf.placeholder(floatDataType, shape=(None, kInputPlanes, 8, 8))

        # MakeNetwork
        self.policy_head, self.network_head = make_network(legacy_weights_param, self.input)

        # preheat


if __name__ == "__main__":
    network = LeelaNetwork()
    print(network)
