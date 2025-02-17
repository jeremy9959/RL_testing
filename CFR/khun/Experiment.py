from copy import deepcopy
from attr import *
from Environment import *
from tqdm import tqdm
def traverse(a, env, i, players):
    env = deepcopy(env)

    g = 0
    if env.is_terminal(): return env.utility()[i.i]
    if a is not None: env.sample_action(i.i, a)
    if env.is_terminal(): return env.utility()[i.i]



    t = env.get_next_turn()
    while t != i.i:

        if env.is_terminal(): return env.utility()[i.i]
        if t != 'c': a = players[t].sample(env.N[t].I)
        else: a = env.N['c'].sample()
        env.sample_action(t, a)
        if env.is_terminal(): return env.utility()[i.i]
        t = env.get_next_turn()

    for a in i.c_Regret[env.N[i.i].I].keys():

        v = traverse(a, env, i, players)
        g += v * (i.get_action_probability(env.N[i.i].I, a))
        r = (1 - i.get_action_probability(env.N[i.i].I, a))*v
        i.update(env.N[i.i].I, a, r)
    return g



if __name__ == '__main__':
    players = {1: Player(1), 2: Player(2), 'c': Chance()}
    env = KhunEnv(players)
    for t in tqdm(range(10000000)):
        for j in range(1, 3, 1):
            traverse(None, env, players[j], players)
    print(players[1].c_Regret)
    print(players[1].count)
    print(players[2].c_Regret)
    print(players[2].count)



