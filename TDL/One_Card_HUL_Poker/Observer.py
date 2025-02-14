
def process_state(state, tot_chip, p_id):
    p_ind = 0 if p_id == state.players[0].id else 1
    card = state.players[p_ind].cards
    card_num = card - 2
    chip_amount = int((20/tot_chip) * state.players[p_ind].chips)
    if chip_amount >= 20:
        chip_amount = 19
    pot_size = int((20/tot_chip) * state.pot)
    if pot_size >= 20:
        pot_size = 19

    return card_num, chip_amount, pot_size



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


def get_reward(game, model, t, state, db):
    reward = 0
    n = max(game.reward.qsize(), 1)
    while not game.reward.empty():
        reward += game.reward.get()
    model.policy_update(reward/n, state, t)

    db.log_reward(0, state[0], state[1], state[2], model.current_SA[1], reward/n)

