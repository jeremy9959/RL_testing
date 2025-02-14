import numpy as np
class Model:
    def __init__(self, actions, gamma, alpha, epsilon, dec_r, dec_ra, Q_learn = False):
        self.actions = actions
        self.state_actions = np.zeros((12, 20, 20, 3))
        self.state_action_distribution = np.zeros((12, 20, 20, 3))
        self.state_action_distribution.fill(1 / 3)
        self.state_actions_count = np.zeros((12, 20, 20, 3))
        self.current_SA = None
        self.alpha = [alpha, alpha]
        self.action_log = []
        self.gamma = gamma
        self.epsilon = [epsilon, epsilon]
        self.decay_rate_e = dec_r
        self.decay_rate_a = dec_ra
        self.Q_learn = Q_learn
    def get_action(self, state):
        current_action = self.choose_action(state)
        self.action_log.append(current_action)
        self.current_SA = state, current_action
        return current_action

    def policy_update(self, reward, next_state, t):


        if self.Q_learn:
            optimal_future_action = self.get_max_value(next_state)
            self.state_actions[self.current_SA[0]][self.current_SA[1]] += (self.alpha[0] *
                                                    (reward + (self.gamma *
                                                               self.state_actions[next_state][
                                                                   optimal_future_action]) -
                                                        self.state_actions[self.current_SA[0]][self.current_SA[1]]))
        else:
            future_action = self.choose_action(next_state)
            self.state_actions[self.current_SA[0]][self.current_SA[1]] += (self.alpha[0] *
                                                                           (reward + (self.gamma *
                                                                                      self.state_actions[next_state][
                                                                                          future_action]) -
                                                                            self.state_actions[self.current_SA[0]][
                                                                                self.current_SA[1]]))
        self.state_actions_count[self.current_SA[0]][self.current_SA[1]] += 1
        self.decay(t)
        #self.update_distribution(self.current_SA[0])

    def choose_action(self, state):
        choice = np.random.choice([0, 1], size=1, p=[self.epsilon[0], 1 - self.epsilon[0]])[0]
        if choice == 1:
            return self.get_max_value(state)
        else:
            return np.random.choice(self.actions, size=1, p=self.state_action_distribution[state])[0]
        #print(self.state_action_distribution[state])

    def get_max_value(self, state):
        return np.argmax(self.state_actions[state])


    def decay(self, t):
        y = (t ** 2) / (self.decay_rate_e + t)
        z = (t ** 2) / (self.decay_rate_a + t)
        self.alpha[0] = self.alpha[1] / (1 + z)
        self.epsilon[0] = self.epsilon[1] / (1 + y)
"""
    def update_distribution(self, state):
        #print(state)
        best_action = self.get_max_value(state)
        #print(f"BEST ACTION: {best_action}")
        #print(f"STATE:{state}")

        for x in range(len(self.state_action_distribution[state])):
            if x == best_action:
                self.state_action_distribution[state][x] += (1 - self.state_action_distribution[state][x]) * self.epsilon

            else:
                self.state_action_distribution[state][x] -= self.state_action_distribution[state][x] * self.epsilon
"""


