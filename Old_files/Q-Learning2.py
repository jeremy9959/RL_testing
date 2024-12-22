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
    [p(x = 0), p(x = 1), p(x = 2), .... , p(x = k)]
    enter at a given episode. K is sampled using a poisson distribution.
    """

    def __init__(self, lam, n):
        self.max_inventory = n
        self.inventory = 3
        self.actions = self.customers  = [x for x in range(n)]
        self.lam = lam
        self.distribution = [(1/(math.e ** self.lam))*(1/(math.factorial(k))) * (self.lam ** k) for k in self.customers]

    """Function that simulates buyig stock. The amount we want to buy is determined by the model. I return the reward
    for buying x inventory. Each item costs 1 reward, so the total reward is - amount of stock purchased."""
    def buy_inventory(self, amount):
        if self.inventory + amount > self.max_inventory:
            self.inventory = self.max_inventory
        else:
            self.inventory += amount
        return -amount

    """function that randomly samples a poisson distribution and returns the number of customers at a given step"""
    def get_customer(self):
        return np.random.choice(self.customers, p = self.distribution, size=1)[0]

    """Function that simulates customers buying inventory. Returns the reward received for x amount of customers buying 
    inventory. If there is not enough inventory for all customers, the reward reflects how much potential money is 
    missed
    """
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

    """This function takes the action from the model and returns the reward from that action."""
    def send_action(self, action):
        num_customers = self.get_customer()
        reward = self.buy_inventory(action) + self.order(num_customers)
        self.num_customer = num_customers

        return (reward, num_customers)


class Model:
    """
    self.actions: A list of possible actions the model can take
    self.actions: A dictionary that maps states to another dictionary that maps actions to the expected value of that
    action in the given state
    self.gamma: Hyperparameter that controls how much weight the future has on the expected value of actions
    self.alpha: Pretty sure this hyperparameter is useless. It is supposed to control the rate of learning. Did not
    notice any differences in the model performance when this hyperparameter was changed.
    self.state_action_distribution: Dictionary that maps states to another dictionary that maps actions to the
    probability that that action will occur given the current state.

    In other words, this dictionary maps states to a probability distribution of actions.

    Every step the probablity distribution is updated to increase the probability of optimaal actions, and decrease
    the probability of sub optimal actions.

    self.epsilon: Hyperparameter that controls the rate in which the model updates its action distribution.
    self.action_log: Logs down the actions the model takes at a given time step.

    """
    def __init__(self, actions, gamma, alpha, epsilon):
        self.actions = actions
        self.state_actions =  dict()
        self.state_action_distribution = dict()
        self.alpha = alpha
        self.action_log = []
        self.gamma = gamma
        self.epsilon = epsilon

    """Function that takes a state and returns an action to take at that state based on the policy at the current step.
    The model also uses information about the reward received from that action to update its policy."""
    def learn(self, state):
        """Checking to see if the state has been seen before. If it has not been seen before, we initialize the state
        and store its action distribution and its expected value in our dictionaries."""
        if state not in self.state_actions:
            self.state_actions[state] = dict()
            self.state_action_distribution[state] = dict()
            for i in self.actions:
                self.state_actions[state][i] = 0
                self.state_action_distribution[state][i] = 1/len(self.actions)

        """Get the action for the current state"""
        current_action = self.get_action(state)
        self.action_log.append(current_action)

        unbinerized_state = pickle.loads(state)

        """Get the reward for the current action in our state"""
        reward = unbinerized_state.action_outcome(current_action)[0]
        print(f"Action: {current_action}, Reward: {reward}")

        """Store the future state"""
        future_state = pickle.dumps(unbinerized_state)

        """If the future state has not been seen before, we initialize it in our dictionaries"""
        if future_state not in self.state_actions:
            self.state_actions[future_state] = dict()
            self.state_action_distribution[future_state] = dict()
            for i in self.actions:
                self.state_actions[future_state][i] = 0
                self.state_action_distribution[future_state][i] = 1 / len(self.actions)

        """Use our current policy and get the expected reward from the optimal action in the future state"""
        optimal_future_action = self.get_max_value(future_state)

        """Check textbook equation 3.5"""
        self.state_actions[state][current_action] += (self.alpha *
                                                      (reward + (self.gamma *
                                                                 self.state_actions[future_state][
                                                                     optimal_future_action]) -
                                                       self.state_actions[state][current_action]))
        """Update the action distribution for the current state"""
        self.update_distribution(state)
        return current_action

    def get_action(self, state):
        #print( self.state_action_distribution[state])
        return np.random.choice(self.actions, size=1, p=[x for x in self.state_action_distribution[state].values()])[0]

    """Updates the distribution of the current state. I increase the probability of the best action in this state
    using epsilon, and decrease the probability of all other actions using epsilon"""
    def update_distribution(self, state):
        best_action = self.get_max_value(state)
        for x,y in self.state_action_distribution[state].items():
            if x == best_action:
                self.state_action_distribution[state][x] += (1 - y) * self.epsilon
            else:
                self.state_action_distribution[state][x] -= y * self.epsilon

    def get_max_value(self, state):
        return max(self.state_actions[state], key = self.state_actions[state].get)


if __name__ == "__main__":
    """Create environment"""
    env1 = Environment(20, 50)

    """Create Model"""
    model = Model(env1.actions, .9, 1, .03)

    """Track the amount of customers received at each step"""
    customer_l = []

    """execute the loop until terminal state"""
    count2 = 0
    trial = 200000
    for i in range(trial):
        binerized_env = pickle.dumps(env1)
        next_action = model.learn(binerized_env)
        _ , t= env1.send_action(next_action)

        customer_l.append(t)
    """To see the actions the model took"""
    # print(model.action_log)
    count = 0
    customer_rate = count2 / trial
    for i in model.action_log:
        if i == 1:
            count += 1


    #print(customer_l)
    count = 0
    for i in customer_l:
        count += i

    """Get the average number of customers received at each step"""
    print(f"Average customer per step: {count/len(customer_l)} with lambda: {env1.lam}")


    count2 = 0
    half = len(model.action_log)//4
    for i in range(len(model.action_log) - 30, len(model.action_log)):
        count2 += model.action_log[i]
    print(customer_l[len(model.action_log) - 30:])
    print(max(customer_l, key = lambda i: customer_l[i]))
    print(model.action_log[len(model.action_log) - 30:])
    average = count2/30

    """Print the average amount of stock purchased at each step. Should roughly match the average number of customers
    revieved at each step"""
    print(f"Average inventory restock per step: {average}")

