from Environment import Environment, Player
from Model import Model
from Observer import *
import numpy as np
from tqdm import tqdm
from database_log import DatabaseLog

def expected_value_raise(raise_amount, call_amount, p_w, p_t, pot, chips_staked):
    p_l = 1 - (p_w + p_t)
    expected_value_fold = -chips_staked
    expected_value_call =  ((pot) * p_w) + (((pot)/2) * p_t) - ((call_amount + chips_staked)* p_l)
    ev_raise = (
            (pot) + ((pot) * p_w) + (((pot) / 2) * p_t) - ((raise_amount + call_amount + chips_staked) * p_l))
    if pot + raise_amount + call_amount >= 40:
        return ev_raise
    else:
        return 1/3 * (ev_raise + max(expected_value_raise(raise_amount, raise_amount, p_w, p_t, pot + call_amount + raise_amount + raise_amount, chips_staked = chips_staked + raise_amount + call_amount), expected_value_call, expected_value_fold))

def dummy_action():
    return np.random.choice([0, 1, 2], size=1, p=[1/3, 1/3, 1/3])[0]



def model_v_simple_m(simple, experiment_id, **kwargs):


    db = DatabaseLog(experiment_id)
    q_model = Model([0, 1, 2], kwargs["gamma"], kwargs["alpha"], kwargs["epsilon"],
                    kwargs["epsilon_dec"], kwargs["alpha_dec"])
    simple_id = simple[1]
    simple_function = simple[0]
    tot_chips = 20
    players = [Player(simple_id), Player(0)]
    game = Environment(players, db = db)
    t = 0

    for i in tqdm(range(kwargs['T'])):

        val = False
        turn = game.start_game(tot_chips)
        while turn != -1 and turn != -2:
            if turn == simple_id:
                a = simple_function()
                action = process_action(a, game, turn)

            else:
                state = process_state(game, tot_chips, 0)
                if val:
                    get_reward(game, q_model, t, state)
                    t += 1
                a = q_model.get_action(state)
                action = process_action(a, game, turn)
                val = True



            ind = 0 if turn == players[0].id else 1
            db.log_action(turn, game.players[ind].chips, game.players[ind].cards, action)
            turn = game.action_handler(turn, action)
            state = process_state(game, tot_chips, 0)
            if val:
                get_reward(game, q_model, t, state)
                t += 1

        if turn == -1:
            db.log_game(0)
        else:
            db.log_game(simple_id)


        game.start_over(20)
    db.commit()
    db.close()

def dummy_v_simple_m(dummy, simple, trial_time, experiment_id):


    dummy_id = dummy[1]
    dummy_action = dummy[0]

    simple_id = simple[1]
    simple_action = simple[0]
    db = DatabaseLog(experiment_id)

    tot_chips = 20
    players = [Player(dummy_id), Player(simple_id)]
    game = Environment(players, db=db)
    t = 0

    for i in tqdm(range(trial_time)):
        turn = game.start_game(tot_chips)
        while turn != -1 and turn != -2:
            if turn == simple_id:
                action = process_action(dummy_action(), game, turn)
            else:
                action = process_action(simple_action(), game, turn)


            ind = 0 if turn == players[0].id else 1
            db.log_action(turn, game.players[ind].chips, game.players[ind].cards, action)
            turn = game.action_handler(turn, action)

        if turn == -1:
            db.log_game(dummy_id)
        else:
            db.log_game(simple_id)

        game.start_over(20)

    db.commit()
    db.close()



if __name__ == '__main__':
    """
    Experiment ID's:
    Model v Dummy: 0
    Call v Dummy: 1
    Raise v Dummy: 2
    Model v Call: 3
    Model v Raise: 4
    
    Model ID's:
    Q-learn: 0 
    Dummy: 1
    Call: 2
    Raise: 3
    """

    #[model_function(), model_id]
    Raise = [lambda: 2, 3]
    call = [lambda: 1, 2]
    dummy = [dummy_action, 1]


    model_params = {
        'T': 20000,
        'gamma':.987,
        'alpha': .25,
        'epsilon': .9,
        'epsilon_dec': 255000000000,
        'alpha_dec': 655000000000

    }
    DatabaseLog(-1).wipe()
    #Q-model v all models
    model_v_simple_m(dummy, 0, **model_params)


    model_v_simple_m(call, 3, **model_params)


    model_v_simple_m(Raise, 4, **model_params)



    #Simple models v dummy

    dummy_v_simple_m(dummy, call, model_params['T'], 1)

    dummy_v_simple_m(dummy, Raise, model_params['T'], 2)




"""
model_v_ev_winrate = []

for i in range(20000):

    val = False
    turn = game.start_game(tot_chips)
    while turn != -1 and turn != -2:
        if turn == 0:
            a = dummy_action()
            action = process_action(a, game, turn)


        else:
            state = process_state(game, tot_chips)


            expected_value_fold = -game.players[1].chips_staked
            p_w = (599/600) * (state[0]/11) * (24/25)
            p_t = (1797/43125)
            p_l = 1 - (p_w + p_t)
            expected_value_call = ((game.pot) * p_w) + (((game.pot)/2) * p_t) - ((game.call_amount + game.players[1].chips_staked)* p_l)
            ev_raise = expected_value_raise(game.raise_amount, game.call_amount, p_w, p_t, game.pot, expected_value_fold)
            max_expected_action = max({1: expected_value_call, 2: ev_raise, 0 :expected_value_fold})

            action = process_action(max_expected_action, game, turn)




        turn = game.action_handler(turn, action)
        if game.reward.empty():
            pass
        elif not game.reward.empty():
            reward = game.reward.get()
            print(f"Reward: {reward}")
            Q_model.policy_update(reward, state, t)
            t += 1

    if turn == -1:
        model_v_ev_winrate.append(1)
    else:
        model_v_ev_winrate.append(0)

    game.start_over(20)



print(f"Dummy v expected value winrate: {np.average(model_v_ev_winrate)}")

tot_chips = 20
Q_model = Model([0, 1, 2], .99, .4, .8, 999999990)
model_v_call = []
players = [Player(0), Player(1)]
game = Environment(players)
t = 0

for i in range(20000):

    val = False
    turn = game.start_game(tot_chips)
    while turn != -1 and turn != -2:
        if turn == 0:
            a = 1
            action = process_action(a, game, turn)


        else:
            state = process_state(game, tot_chips)
            #print(state)
            if val and game.reward.empty():
                reward = 0
                Q_model.policy_update(0, state, t)
                t += 1
            elif val and not game.reward.empty():
                reward = game.reward.get()
                Q_model.policy_update(reward, state, t)
                t += 1

            a = Q_model.get_action(state)
            action = process_action(a, game, turn)

            val = True


        turn = game.action_handler(turn, action)
        if game.reward.empty():
            pass
        elif not game.reward.empty():
            reward = game.reward.get()
            print(f"Reward: {reward}")
            Q_model.policy_update(reward, state, t)
            t += 1

    if turn == -1:
        model_v_call.append(1)
    else:
        model_v_call.append(0)


    game.start_over(20)
#print(model_v_call)
print(f"Model v Call only strategy last 50 games: {np.average(model_v_call[len(model_v_call) -50:])}")




tot_chips = 20
Q_model = Model([0, 1, 2], .97, .25, .95, 85000000000, 1500000000000)
model_v_raise = []
players = [Player(0), Player(1)]
game = Environment(players)
t = 0


for i in range(20000):

    val = False
    turn = game.start_game(tot_chips)
    while turn != -1 and turn != -2:
        if turn == 0:
            a = 2
            action = process_action(a, game, turn)
        else:
            state = process_state(game, tot_chips)
            #print(state)
            if val and game.reward.empty():
                reward = 0
                Q_model.policy_update(0, state, t)
                t += 1
            elif val and not game.reward.empty():
                reward = game.reward.get()
                print(f"Reward: {reward}")
                Q_model.policy_update(reward, state, t)
                t += 1

            a = Q_model.get_action(state)

            action = process_action(a, game, turn)


            val = True


        turn = game.action_handler(turn, action)

    state = process_state(game, tot_chips)
    if game.reward.empty():
        pass
    elif not game.reward.empty():
        reward = game.reward.get()
        print(f"Reward: {reward}")
        Q_model.policy_update(reward, state, t)
        t += 1

    if turn == -1:
        model_v_raise.append(1)
    else:
        model_v_raise.append(0)


    game.start_over(20)
#print(model_v_call)

print(Q_model.state_actions)
print(Q_model.epsilon, Q_model.alpha)
print(len(model_v_raise))
print(f"Model v Raise only strategy last 200 games: {np.average(model_v_raise[len(model_v_raise) - 200:])}")

"""