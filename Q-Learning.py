import pickle
import numpy as np
class Environment:
    """
    self.T = Terminal State number
    self.p_s = Probability of customer
    self.max_inventory = total inventory the model can hold
    self.inventory = current inventory size
    self.actions: 1 to restock, 0 to not restock
    self.customer: for each episode, 1 if there is a customer, 0 if not
    """
    def __init__(self, T, p_s):
        self.T = T
        self.p_s = p_s
        self.max_inventory = 2
        self.inventory = self.max_inventory
        self.actions = [0, 1]
        self.customer = None


    def buy_inventory(self):


        if self.inventory == self.max_inventory:
            pass
        else:
            self.inventory += 1


    def sale(self):
        if self.inventory == 0:
            return -2
        else:
            self.inventory -= 1
            return 2

    """Return 1 if customer, 0 if not customer"""
    def get_customer(self):
        self.customer = np.random.binomial(1, self.p_s, size = 1)

    def get_state(self):
        return pickle.dumps(self)
    def send_action(self, action):
        reward = 0
        b = False
        if action == 1:
            b = True
            self.buy_inventory()
            reward -= 1
        else:
            pass

        self.get_customer()
        if self.customer == 1:
            reward += self.sale()

        return reward


class Model:
    def __init__(self, actions,  gamma, alpha, epsilon):
        self.actions = actions
        self.state_actions = dict()
        #self.state_action_distribution = dict()
        self.action = None
        self.alpha = alpha
        self.action_log = []
        self.gamma = gamma
        self.epsilon = epsilon

    def learn(self, state):
        if state not in self.state_actions:
            self.state_actions[state] = dict()
            #self.state_action_distribution[state] = dict()
            for i in self.actions:
                self.state_actions[state][i] = 0
                #self.state_action_distribution[state][i] = 1/len(self.actions)

        current_action = self.get_action(state)

        #print(f"CURRENT ACTIO: {current_action}")
        self.action_log.append(current_action)

        unbinerized_state = pickle.loads(state)
        reward = unbinerized_state.send_action(current_action)
        future_state = pickle.dumps(unbinerized_state)
        if future_state not in self.state_actions:
            self.state_actions[future_state] = dict()
            #self.state_action_distribution[state] = dict()
            for i in self.actions:
                self.state_actions[future_state][i] = 0
                #self.state_action_distribution[state][i] = 1 / len(self.actions)


        #future_action  = self.get_action(future_state)
        optimal_future_action = self.get_max_value(future_state)
        #print(f"Optimal future action: {optimal_future_action}")


        self.state_actions[state][current_action] += (self.alpha *
                                                        (reward + (self.gamma *
                                                       self.state_actions[future_state][optimal_future_action]) -
                                                        self.state_actions[state][current_action]))
        return current_action

    """Implemented using an epsilon-greedy action selection"""
    """Poor implementation: hard coded actions in"""
    def get_action(self, state):
        if self.get_max_value(state) == 0:
            distribution =  [1 - self.epsilon , self.epsilon]
        elif self.get_max_value(state) == 1:
            distribution = [self.epsilon, 1 - self.epsilon]
        else:
            distribution = [.5, .5]

        return np.random.choice(self.actions, size = 1, p = distribution)[0]


    def get_max_value(self, state):
        return max(self.state_actions[state])



if __name__ == "__main__":
    env1 = Environment(10000, .8)
    """Model which takes in actions and a gamma hyperparameter"""

    model = Model(env1.actions, .6, .01, 0)

    """execute the loop until terminal state"""
    count2 = 0
    trial = 10000
    for i in range(trial):
        binerized_env = pickle.dumps(env1)
        next_action = model.learn(binerized_env)
        env1.send_action(next_action)
        if env1.customer == 1:
            count2 += 1

            #print(f"Customer recieved, Bank Value:, Action: {next_action}, Inventory: {env1.inventory}")
        else:
            #print(f"No customer recieved, Bank Value:, Action: {next_action}, Inventory: {env1.inventory}")
            pass
    #print(model.action_log)
    count = 0
    customer_rate = count2 / trial
    for i in model.action_log:
        if i == 1:
            count += 1
    """How accurate the models strategy is, the close it is to p_s the more optimal the strategy"""
    model_performance = count / trial
    print(f"Our model is: {(abs(model_performance - customer_rate) * 100):.3f}% away from the optimal policy")

    print(len(model.state_actions))




    """
    Notes: Q-learning method uses more hyperparameters than MC policy generation. Although, Q-learning is much more
    computationally cheap. Q-learning is not as accurate, approaching an optimal pick rate of around 90 percent.
    
    Q-Learning is not going to be an affective algorithm for this problem. Q-Learning takes the next state
    reward as a factor for the current policies performance. Because the policy has no affect on what the next state
    is going to be, there is no point in considering the value of the next state when training the model.
    Furthermore, our algorithm will never choose THE optimal strategy due to the epsilon greedy implementation. 
    """
