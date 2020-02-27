from rbmc.RBMCGameManager import *

manager = GameManager(GAME_KEEP_NUM, True)
s, m_o, r_o, s_o = manager.read_game("output/rbmcgame/9.json")
print("debug")
