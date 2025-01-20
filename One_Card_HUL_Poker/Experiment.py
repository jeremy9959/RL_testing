from Environment import Environment, Player
from Model import Model
from Observer import *
import numpy as np

def dummy_action():
    return np.random.choice([0, 1, 2], size=1, p=[1/3, 1/3, 1/3])[0]

tot_chips = 20
players = [Player(0), Player(1)]
Q_model = Model([0, 1, 2], .97, .4, .9, 100)
winner = []

game = Environment(players)

for i in range(1000):
    t = 0
    val = False
    turn = game.start_game(tot_chips)
    while turn != -1 and turn != -2:
        if turn == 0:
            a = dummy_action()
            action = process_action(a, game)

        else:
            state = process_state(game, tot_chips)
            print(state)
            if val and game.reward.empty():
                reward = 0
                Q_model.policy_update(0, state, t)
                t += 1
            elif val and not game.reward.empty():
                reward = game.reward.get()
                Q_model.policy_update(reward, state, t)
                t += 1

            a = Q_model.get_action(state)
            action = process_action(a, game)
            print(a)
            val = True



        turn = game.action_handler(turn, action)


    if turn == -1:
        winner.append(1)
    else:
        winner.append(0)
    game.start_over(20)
print(Q_model.epsilon, Q_model.alpha)
print(np.average(winner[len(winner)-50:]))

