from policy_index import policy_index

policy_map = {policy_index[i]: i for i in range(len(policy_index))}

# the default promotion is to a knight
# so I map that policy to the default movement
for base_move in ["a7a8", "a7b8", "b7a8", "b7b8", "b7c8", 
                  "c7b8", "c7c8", "c7d8", "d7c8", "d7d8", 
                  "d7e8", "e7d8", "e7e8", "e7f8", "f7e8", 
                  "f7f8", "f7g8", "g7f8", "g7g8", "g7h8", 
                  "h7g8", "h7h8"]:
    policy_map[base_move + "n"] = policy_map[base_move]

