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
    def __init__(self, actions, gamma):
        """
        state_actions = dictionary of all states, inside holds another dictionary of all possible actions. Each action
        key has a list for a value, where a reward at that state is stored. Actions are chosen by maximum
        average actions.
        state: Too lazy to change, this is not needed, but it is used to check to see if the state is reached
        (could just use state_actions instead)
        action: Action the model should take at a given episode
        action_log: Logs all the actions the model took in the experiment

        :param actions: set of actions possible
        :param gamma: hyperparameter for consequence of prior actions on future actions, 0 <= gamma <= 1
        """
        self.state_actions =dict()
        self.states = set()
        self.action = None
        self.actions = actions
        self.gamma = gamma
        self.action_log = list()

    def action_decision(self, state, t):


        if state not in self.states:
            self.states.add(state)
            self.state_actions[state] = dict()
            for i in self.actions:
                self.state_actions[state][i] = [0]






        future_state = pickle.loads(state)
        self.action = self.best_action(state)
        action = self.action
        self.action_log.append(self.action)

        G = 0
        episodes = future_state.T - t

        """Generate a series from now to the terminal state based off of our current action"""
        for i in range(episodes):
            """Capture the current state"""
            current_state = future_state
            binerized_curr_state = pickle.dumps(current_state)

            """Set the future state and get the reward of the current episode"""
            reward = future_state.action_outcome(self.action)

            """Calculating G, our reward for episode i"""
            G = (G * (self.gamma ** (i))) + (reward)

            binerized_future_state = pickle.dumps(future_state)

            """If the future state has not been seen before"""
            if binerized_future_state not in self.states:
                self.states.add(binerized_future_state)
                self.state_actions[binerized_future_state] = dict()
                for i in self.actions:
                    self.state_actions[binerized_future_state][i] = [0]
            
            """For this current state, the action we took, the reward we recieved"""
            self.state_actions[binerized_curr_state][self.action].append(G)

            """Get the next action for the future state"""
            self.action = self.best_action(binerized_future_state)



        return action

    def best_action(self, state):


        return max(self.state_actions[state], key = lambda action: np.average(self.state_actions[state][action]))




if __name__ == "__main__":
    """Environemnt with terminal state at episode 200 and bernoulli distribution 
    of a customer at p_s"""
    env1 = Environment(20, .8)
    """Model which takes in actions and a gamma hyperparameter"""
    #FIXME Gamma set at 0 builds optimal model, anything else is not optimizing properly
    model = Model(env1.actions, .9 )


    """execute the loop until terminal state"""
    count2 = 0
    trial = 20
    for i in range(trial):
        binerized_env = pickle.dumps(env1)
        next_action = model.action_decision(binerized_env, i)
        env1.send_action(next_action)
        if env1.customer == 1:
            count2 += 1

            print(f"Customer recieved, Bank Value:, Action: {next_action}, Inventory: {env1.inventory}")
        else:
            print(f"No customer recieved, Bank Value:, Action: {next_action}, Inventory: {env1.inventory}")
    print(model.action_log)
    count = 0
    customer_rate = count2/trial
    for i in model.action_log:
        if i == 1:
            count += 1
    """How accurate the models strategy is, the close it is to p_s the more optimal the strategy"""
    model_performance = count/trial
    print(f"Our model is: {(abs(model_performance - customer_rate) * 100):.3f}% away from the optimal policy")

    print(len(model.state_actions))
    print(model.state_actions)
