
# Self-Play Variables
GAMES_PER_ITER = 25000  # These values came from AGZ paper
EVAL_PER_MOVE = 800  # Number of NN evals per move from AZ paper
TEMPERATURE = 1  # TODO: Change temperature to do the thing from AGZ pg 24 Self-Play
EXPLORATION = 1.4142135624

# Training/Optimization Variables
SAMPLE_SIZE = int(2048)  # Mini-batch size from AGZ paper
BATCH_SIZE = 32  # batch-size per worker from AGZ paper
MOMENTUM = 0.9
STEPS_PER_ITER = 1000
LEARNING_RATE = 10E-4  # TODO: Replace with smart thing

# Game Manager Variables
GAME_KEEP_NUM = 500000  # How many games should it keep

# Neural Network Variables
N = 8
T = 8
M = 12
L = 7
RESIDUAL_BLOCKS = 19  # This is not counting the starting block
REG_PARAM = 0.0001  # 10^-4
