
def process_state(state, tot_chip, p_id):
    p_ind = 0 if p_id == state.players[0].id else 1
    card = state.players[p_ind].cards
    card_num = card - 2
    chip_amount = int((20/tot_chip) * state.players[p_ind].chips) - 1
    if chip_amount >= 20:
        chip_amount = 19
    elif chip_amount < 0:
        chip_amount = 0
    opp_action = 1 if state.raise_ else 0
    return card_num, chip_amount, opp_action



def process_action(action, env, p_id):
    o_id = env.players[0].id if p_id == env.players[1].id else env.players[1].id
    p_ind = 0 if p_id == env.players[0].id else 1
    o_ind = 0 if p_ind == 1 else 1

    if action == 0:
        return "FOLD"


    elif action == 1:
        if not env.raise_:
            return "CHECK"
        else:
            return "CALL"
    else:

        if env.players[o_ind].chips == 0 and env.raise_:
            return "CALL"
        elif env.players[p_ind].chips == 0 and not env.raise_:
            return "CHECK"
        elif env.players[p_ind].chips - env.call_amount <= 0:
            return "CALL"
        return "RAISE"


def get_reward(game, model, t, state):
    if game.reward.empty():
        model.policy_update(0, state, t)
    else:

        reward = game.reward.get()
        model.policy_update(reward, state, t)
