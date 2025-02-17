import numpy as np
import random
from Environment import KhunEnv
from enum import Enum


class Deck:
    def __init__(self):
        self.cards = ['J', 'Q', 'K']
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)
    def deal_card(self):
        return self.cards.pop()
    def reset(self):
        self.shuffle()
        self.cards = ['J', 'Q', 'K']


class Dict(dict):
    def __init__(self):
        super().__init__()

    def __setitem__(self, key, value):

        if key not in self:
            value2 = KhunEnv.possible_actions(key)
            super().__setitem__(key, value2)
        super().__setitem__(key, value)

    def __getitem__(self, key):
        if key not in self:
            value = KhunEnv.possible_actions(key)
            super().__setitem__(key, value)



        return super().__getitem__(key)


class Chance:
    def __init__(self):
        self.i = 'c'
        self.deck = Deck()


    def sample(self):
        self.deck.shuffle()
        return self.deck.deal_card()

    def reset(self):
        self.deck.reset()



class Player:
    def __init__(self, i, epsilon = .6):
        self.i = i
        self.c_Regret = Dict()
        self.chips = 0
        self.stake = 0
        self.I = None
        self.epsilon = epsilon
        self.count = 0


    def update(self, I, a, r):
        self.c_Regret[I][a] += r
        self.count += 1

    def get_distribution(self, I):
        R = sum(value for value in self.c_Regret[I].values() if value > 0)
        if R == 0:
            return self.get_random_distribution(I)
        else:
            return [action/R if action > 0 else 0 for action in self.c_Regret[I].values()]

    def get_actions(self, I):
        return [x for x in self.c_Regret[I].keys()]
    def sample(self, I):
        return np.random.choice(self.get_actions(I), p = self.get_distribution(I), size = 1)[0]
    def get_random_distribution(self, I):
        return [1/len(self.c_Regret[I]) for i in range(len(self.c_Regret[I]))]

    def get_action_probability(self, I, a):
        R = sum(value for value in self.c_Regret[I].values() if value > 0)
        if R == 0:
            return 1/len(self.c_Regret[I])
        elif self.c_Regret[I][a] < 0: return 0
        else:
            return self.c_Regret[I][a]/R

