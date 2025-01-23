from Environment import Environment, Player
from Model import Model
from Observer import *
import numpy as np


def dummy_action():
    return np.random.choice([0, 1, 2], size=1, p=[1/3, 1/3, 1/3])[0]

tot_chips = 20
players = [Player(0), Player(1)]
Q_model = Model([0, 1, 2], .97, .4, .8, 999999000)
winner = []

game = Environment(players)
t = 0
for i in range(2000):

    val = False
    turn = game.start_game(tot_chips)
    while turn != -1 and turn != -2:
        if turn == 0:
            a = dummy_action()
            action = process_action(a, game)

        else:
            state = process_state(game, tot_chips)
            #print(state)
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
           #print(a)
            val = True

        turn = game.action_handler(turn, action)


    if turn == -1:
        winner.append(1)
        print("GAME OVER MODEL WINS")
    else:
        winner.append(0)
        print("GAME OVER DUMMY WINS")

    game.start_over(20)


print(winner)
print(Q_model.epsilon, Q_model.alpha)
print(np.average(winner[len(winner)-50:]))

