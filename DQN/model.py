import numpy as np

class NN:
    def __init__(self):
        pass

class Model:
    def __init__(self, actions, gamma, alpha, epsilon, dec_r, dec_ra):
        self.actions = actions
        self.current_SA = None
        self.alpha = [alpha, alpha]
        self.action_log = []
        self.gamma = gamma
        self.epsilon = [epsilon, epsilon]
        self.decay_rate_e = dec_r
        self.decay_rate_a = dec_ra



    def choose_action(self, state):
        choice = np.random.choice([0, 1], size=1, p=[self.epsilon[0], 1 - self.epsilon[0]])[0]
        if choice == 1:
            return self.get_max_Q(state)
        else:
            return np.random.choice(self.actions, size=1, p=self.state_action_distribution[state])[0]


    def get_max_Q(self):
        pass