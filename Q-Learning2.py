import pickle
import numpy as np
import math

class Environment:
    """
    self.T = Terminal State number
    self.max_inventory = total inventory the model can hold (proportional to the total amount of customers that can come enter at a given time)
    self.inventory = current inventory size
    self.actions: List from 1 to 2 * n representing the amount of stock the model wants to purchase
    self.customers: list of a number from 1 to n. Meaning, at most 10 customers can enter the store at a given step
    self.lam: Parameter representing lambda, the constant variable in a poisson model
    self.distribution: Used for computing the probability of that X = k. More specifically, the probability that k amount of customers
    enter at a given episode. K is sampled using a poisson distribution.
    """

    def __init__(self, T, lam, n):
        self.T = T

        self.max_inventory = n
        self.inventory = 3
        self.actions = [x for x in range(n)]

        self.lam = lam

        self.customers = [x for x in range(n)]
        self.distribution = [(1/(math.e ** self.lam))*(1/(math.factorial(k))) * (self.lam ** k) for k in self.customers]
        count = 0
        for i in self.distribution:
            count += i
        print(count)

    def buy_inventory(self, amount):

        if self.inventory + amount > self.max_inventory:
            self.inventory = self.max_inventory
            return -amount
        else:
            self.inventory += amount
            return -amount

    def sale(self):
        if self.inventory == 0:
            return -2
        else:
            self.inventory -= 1
            return 2

    """Return 1 if customer, 0 if not customer"""

    def get_customer(self):
        #print(self.distribution)
        return np.random.choice(self.customers, p = self.distribution, size=1)[0]

    def order(self, num_customers):
        if self.inventory < num_customers:
            orders_missed = num_customers - self.inventory
            orders_sold = self.inventory - orders_missed
            self.inventory = 0
            return 2 * (orders_sold  - orders_missed)
        else:
            orders_sold = num_customers
            self.inventory -= num_customers
            return 2 * orders_sold


    def get_state(self):
        return pickle.dumps(self)

    def send_action(self, action):
        reward = 0

        reward += self.buy_inventory(action)
        #print("Reward", reward)

        num_customers = self.get_customer()
        self.num_customer = num_customers

        reward += self.order(num_customers)
        #print(f"Reward: {reward}, Action: {action}, Customers: {num_customers}")
        return (reward, num_customers)


class Model:
    def __init__(self, actions, gamma, alpha, epsilon):
        self.actions = actions

        self.state_actions = dict()
        self.state_action_distribution = dict()
        self.action = None
        self.alpha = alpha
        self.action_log = []
        self.gamma = gamma
        self.epsilon = epsilon

    def learn(self, state):
        if state not in self.state_actions:
            self.state_actions[state] = dict()
            self.state_action_distribution[state] = dict()
            for i in self.actions:
                self.state_actions[state][i] = 0
                self.state_action_distribution[state][i] = 1/len(self.actions)

        current_action = self.get_action(state)

        # print(f"CURRENT ACTIO: {current_action}")
        self.action_log.append(current_action)

        unbinerized_state = pickle.loads(state)
        reward = unbinerized_state.send_action(current_action)[0]
        print(f"Action: {current_action}, Reward: {reward}")
        future_state = pickle.dumps(unbinerized_state)
        if future_state not in self.state_actions:
            self.state_actions[future_state] = dict()
            self.state_action_distribution[future_state] = dict()
            for i in self.actions:
                self.state_actions[future_state][i] = 0
                self.state_action_distribution[future_state][i] = 1 / len(self.actions)

        # future_action  = self.get_action(future_state)
        optimal_future_action = self.get_max_value(future_state)
        # print(f"Optimal future action: {optimal_future_action}")

        self.state_actions[state][current_action] += (self.alpha *
                                                      (reward + (self.gamma *
                                                                 self.state_actions[future_state][
                                                                     optimal_future_action]) -
                                                       self.state_actions[state][current_action]))
        self.update_distribution(state)
        return current_action




    def get_action(self, state):
        #print( self.state_action_distribution[state])
        return np.random.choice(self.actions, size=1, p=[x for x in self.state_action_distribution[state].values()])[0]
    def update_distribution(self, state):
        best_action = self.get_max_value(state)
        print(f"Actions:{self.state_actions[state]}")
        print(f"Best action:{best_action}")
        for x,y in self.state_action_distribution[state].items():
            if x == best_action:
                self.state_action_distribution[state][x] += (1 - y) * self.epsilon
            else:
                self.state_action_distribution[state][x] -= y * self.epsilon


    def get_max_value(self, state):
        return max(self.state_actions[state], key = self.state_actions[state].get)


if __name__ == "__main__":
    env1 = Environment(20000, 5, 50)
    bank = 5
    """Model which takes in actions and a gamma hyperparameter"""

    model = Model(env1.actions, .9, 1, .01)
    customer_l = []
    """execute the loop until terminal state"""
    count2 = 0
    trial = 20000
    for i in range(trial):
        binerized_env = pickle.dumps(env1)
        next_action = model.learn(binerized_env)
        _ , t= env1.send_action(next_action)

        customer_l.append(t)




    # print(model.action_log)
    count = 0
    customer_rate = count2 / trial
    for i in model.action_log:
        if i == 1:
            count += 1
    """How accurate the models strategy is, the close it is to p_s the more optimal the strategy"""
    model_performance = count / trial
    print(customer_l)
    count = 0
    for i in customer_l:
        count += i

    print(f"Average customer per step: {count/len(customer_l)} with lambda: {env1.lam}")

    print(model.action_log)
    count2 = 0
    half = len(model.action_log)//2
    for i in range(half, len(model.action_log)):
        count2 += model.action_log[i]

    average = count2/(len(model.action_log)-half)
    print(f"Average inventory restock per step: {average}")
    assert(len(customer_l) == len(model.action_log))


"""
Because of the number of states and actions, this model needs a lot of samples to train properly. Using an epsilon (training rate) of .01, 
which in my opinion is a little high with 50 different actions to choose from. Although, despite increasing the states ad actions, the model was still
able to approach an optimal buy rate. 

Things I would like to try are the bank values of the bot at the end of each trial. Adding bank values to the 
environemnt would exponentially increase the amount of different states.
"""