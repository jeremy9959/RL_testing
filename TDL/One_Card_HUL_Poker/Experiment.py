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



def model_v_simple_m(simple, experiment_id, m_id, **kwargs):


    db = DatabaseLog(experiment_id)
    q_model = Model([0, 1, 2], kwargs["gamma"], kwargs["alpha"], kwargs["epsilon"],
                    kwargs["epsilon_dec"], kwargs["alpha_dec"], Q_learn = kwargs["Q-learn"])
    simple_id = simple[1]
    simple_function = simple[0]
    tot_chips = 20
    players = [Player(simple_id), Player(m_id)]
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
                state = process_state(game, tot_chips + 20, m_id)
                if val:
                    get_reward(game, q_model, t, state, db)
                    t += 1
                a = q_model.get_action(state)
                action = process_action(a, game, turn)
                val = True



            ind = 0 if turn == players[0].id else 1
            db.log_action(turn, game.players[ind].chips, game.players[ind].cards, action, game.pot)
            turn = game.action_handler(turn, action)
            """
            state = process_state(game, tot_chips + 20, m_id)
            if val:
                get_reward(game, q_model, t, state)
                t += 1
            """
        if turn == -1:
            db.log_game(m_id)
        else:
            db.log_game(simple_id)


        game.start_over(20)
    print(q_model.epsilon, q_model.alpha)
    db.save_Q(m_id, q_model.state_actions, q_model.state_actions_count)
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
    SARSA v Dummy: 0
    Call v Dummy: 1
    Raise v Dummy: 2
    SARSA v Call: 3
    SARSA v Raise: 4
    Q-Learn v Dummy: 5
    Q-Learn v Call: 6
    Q-Learn v Raise: 7
    
    Model ID's:
    SARSA: 0 
    Dummy: 1
    Call: 2
    Raise: 3
    Q-Learn: 4
    """

    #[model_function(), model_id]
    Raise = [lambda: 2, 3]
    call = [lambda: 1, 2]
    dummy = [dummy_action, 1]


    model_params = {
        'T': 4000000,
        'gamma':.987,
        'alpha': .25,
        'epsilon': .9,
        'epsilon_dec': 10555000000000,
        'alpha_dec': 13355000000000,
        'Q-learn': False
    }
    #DatabaseLog(-1).wipe(0)
    #DatabaseLog(-1).wipe(3)
    DatabaseLog(-1).wipe(4)



    #Q-model v all models
    #model_v_simple_m(dummy, 0, 0, **model_params)


    #model_v_simple_m(call, 3, 0, **model_params)


    model_v_simple_m(Raise, 4, 0, **model_params)

    model_params['Q-learn'] = True
    #model_v_simple_m(dummy, 5, 4, **model_params)

    #model_v_simple_m(call, 6, 4, **model_params)

    #model_v_simple_m(Raise, 7, 4, **model_params)


    #Simple models v dummy

    #dummy_v_simple_m(dummy, call, model_params['T'], 1)

    #dummy_v_simple_m(dummy, Raise, model_params['T'], 2)


