from copy import deepcopy
from attr import *
from Environment import *
from tqdm import tqdm
def traverse(a, env, i, players):
    env = deepcopy(env)
    r = dict()
    g = 0
    if env.is_terminal(): return env.utility()[i.i]
    if a is not None: env.sample_action(i.i, a)
    if env.is_terminal(): return env.utility()[i.i]

    t = env.get_next_turn()
    while t != i.i:

        if env.is_terminal(): return env.utility()[i.i]
        if t != 'c':
            a = players[t].sample(env.N[t].I)
            prob = players[t].get_action_probability(env.N[t].I, a)
            players[t].accum_pol(env.N[t].I, a, prob)
        else: a = env.N['c'].sample()

        env.sample_action(t, a)
        if env.is_terminal(): return env.utility()[i.i]
        t = env.get_next_turn()

    for a in i.c_Regret[env.N[i.i].I].keys():
        r[a] = traverse(a, env, i, players)
        g += r[a] * (i.get_action_probability(env.N[i.i].I, a))

    for a in i.c_Regret[env.N[i.i].I].keys():
        reg = r[a] - g
        i.update(env.N[i.i].I, a, reg)

    return g



if __name__ == '__main__':
    players = {1: Player(1), 2: Player(2), 'c': Chance()}
    env = KhunEnv(players)
    for t in tqdm(range(100000)):
        for j in range(1, 3, 1):
            traverse(None, env, players[j], players)
    print(players[1].get_average_strategy())
    print(players[1].count)
    print(players[2].get_average_strategy())
    print(players[2].count)



