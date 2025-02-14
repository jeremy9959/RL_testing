import numpy as np
import random
from Environment import *
from enum import Enum

class turn(Enum):
    p1 = 1
    p2 = 2
    c = 3

class Deck():
    def __init__(self):
        self.cards = [1, 2, 3]
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
            value = KhunEnv.possible_actions(key)
        super().__setitem__(key, value)

class Chance:
    def __init__(self):
        self.deck = Deck()


    def sample(self):
        self.deck.shuffle()
        return self.deck.deal_card()

    def reset(self):
        self.deck.reset()



class Player:
    def __init__(self, chips):
        self.c_Regret = Dict()
        self.chips = chips
        self.stake = 0


    def update(self, I, a, r):
        self.c_Regret[I][a] += r

    def get_distribution(self, I):
        if sum(self.c_Regret[I].values()) == 0:
            return [1/3, 1/3, 1/3]
        else:
            return [x/sum(self.c_Regret[I].values()) for x in self.c_Regret[I].values()]

    def get_actions(self, I):
        return [x for x in self.c_Regret[I].keys()]
    def sample(self, I):
        return np.random.choice(self.get_actions(I), p = self.get_distribution(I), size = 1)[0]
