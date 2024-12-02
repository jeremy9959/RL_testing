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
            reward = future_state.send_action(self.action)

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

    """(brief) Results of experiment: 
        Model does seem to be tuning itself to an optimal strategy. Questions/observations 
        are noted as followed:
            1. Figure out why and how changing the hyperparameter gamma, has such an impact 
                on the performance of the model. Why is the most optimal gamma 0?
            
            2. Try to change the environment such as, increasing storage amount, adding more items
                S.T customer purchase is a distribution where each item is a differnet price
                
                a. try to create a model that does not need to be changed with the environment
            
            3. How much of an affect does the terminal state number have on the model.
                a. Experiment with changing T and not changing the trial amount
                b. Experiment with not changing T and changing the trial amount
                c. If T is relatively low, and we run the experiment a bunch of time,
                    can the model still find an optimal policy?
            
            4. Why does the experiment sometimes vary so much in its results? Running this  
                experiment numerous times sometimes results in the model having a -.2 accuracy 
                from the optimal policy. Why doesnt the model train consistently given a large T?
                
                a. p_s represent prob of customer, meaning, in some experiments, the actual customer 
                    expectancy will vary with each trial. The lower the sample size, the more variation
                        
                        aa. If this is the case, check to see if our model optimally follows a normal
                            distrubution around our probability of customer p_s.
                            
                            aaa. Idea was tested, it seems model is still pretty consistent, although,
                                on few trials the policy created is +-(.5) from the optimal policy (with max +-1 and min 0)
                            
                            bbb. Seems when T is greater, variability is lower, still, model should be consistently improving 
                                to optimal policy every time.
                                
            
            5. Training this model is very computationally expensive. For larger trial sizes T, our function
                grows approx. o(T^3), is there a way to train the model more effeciently?
             
            6. The textbook emphasizes starting the episode generation from T and ending at t0, get clarification...
            
            7. Total amount of states is 6. Although, should the amount of money in the bank be considered as a change
             in the state? This was tried, does not seem to be a good idea, although I do need to factor in when the model has
             no more money, as if there isnt any more money than the shop can not order more inventory.
             
                a. What is an optimal way to express an environemnt. I feel as though this experiment doesnt exactly match 
                the experiment im trying to replicate.
             
                b.  Do the rewards match the intended experiment. Changing the rewards drastically impacts how the model learns.
            
            8. If I dont punish the model for not purchasing any items, then it learns to never purchase anything as it doesnt 
                have anything to lose if it doesnt take any risk. How can I optimize the model to try and maximize the expected
                value?
                a. Because Im choosing the policy with the highest reward, if not buying anything starts off as an optimal policy,
                    my model will always choose that policy unless it ends up being worse than another strategy. Essentially, this model
                    is unable to explore different possibilites.
                    
                    aaa. To get the model to explore possibilites, its choices need to lie on a distribution, such that the model will by chance,
                        try another strategy to see if it is optimal.
                        
            
                """
