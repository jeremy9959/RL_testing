import numpy as np


class Environment:
    def __init__(self, lam, n,seed=101):
        self.max_inventory = n
        self.inventory = 3
        self.actions = [x for x in range(n)]
        #self.actions = self.customers = [x for x in range(n)]
        self.lam = lam
        self.rng = np.random.default_rng(seed)

    def buy_inventory(self, amount):
        self.inventory =  self.max_inventory if self.inventory + amount > self.max_inventory else self.inventory + amount
        return -amount

    def get_customer(self):
        return min(self.rng.poisson(self.lam), self.max_inventory)

    def order(self, num_customers):
        orders_sold = self.inventory if self.inventory < num_customers else num_customers
        orders_missed = num_customers - orders_sold
        self.inventory = 0 if self.inventory < num_customers else self.inventory - orders_sold
        return 2 * (orders_sold  - orders_missed)

    def action_outcome(self, action):
        num_customers = self.get_customer()
        reward = self.buy_inventory(action) + self.order(num_customers)
        return reward, num_customers


class Model:
    def __init__(self, actions, gamma, alpha, epsilon):
        self.actions = actions
        self.state_actions = np.zeros((len(actions), len(actions)))
        self.state_action_distribution = np.zeros((len(actions), len(actions)))
        self.state_action_distribution.fill(1/len(self.actions))
        self.current_SA = None
        self.alpha = alpha
        self.action_log = []
        self.gamma = gamma
        self.epsilon = epsilon

    def get_action(self, state):
        current_action = self.choose_action(state.inventory)
        self.action_log.append(current_action)
        self.current_SA = (state.inventory, current_action)
        return current_action

    def policy_update(self, reward, next_state):
        future_state = next_state.inventory

        optimal_future_action = self.get_max_value(future_state)

        self.state_actions[self.current_SA] += (self.alpha *
                                                              (reward + (self.gamma *
                                                                         self.state_actions[future_state][
                                                                             optimal_future_action]) -
                                                               self.state_actions[self.current_SA]))
        self.update_distribution(self.current_SA[0])

    def choose_action(self, state):
        return np.random.choice(self.actions, size=1, p=self.state_action_distribution[state])[0]

    def update_distribution(self, state):
        best_action = self.get_max_value(state)
        self.state_action_distribution[state] -= (self.state_action_distribution[state] * self.epsilon)
        self.state_action_distribution[state][best_action] += self.epsilon

    def get_max_value(self, state):

        return np.argmax(self.state_actions[state])

if __name__ == "__main__":
    env1 = Environment(1000, 40000)

    model = Model(env1.actions, 1, 1, .00009)

    customer_l = []

    trial = 140000

    for i in range(trial):
        next_action = model.get_action(env1)
        reward , t= env1.action_outcome(next_action)
        model.policy_update(reward, env1)
        customer_l.append(t)

    print(customer_l[- 30:])
    print(model.action_log[ - 30:])
    average_customer = np.average(customer_l[- 30:])
    average_action = np.average(model.action_log[ - 30:])
    print(f"Average customer per step: {average_customer} with lambda: {env1.lam}")
    print(f"Average inventory restock per step: {average_action}")