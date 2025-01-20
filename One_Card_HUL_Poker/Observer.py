
def process_state(state, tot_chip):
    card = state.players[1].cards
    card_num = card - 2
    chip_amount = int((20/tot_chip) * state.players[1].chips) - 1
    if chip_amount >= 20:
        chip_amount = 19
    elif chip_amount < 0:
        chip_amount = 0
    opp_action = 1 if state.raise_ else 0
    return card_num, chip_amount, opp_action


def process_action(action, env):
    if action == 0:
        return "FOLD"


    elif action == 1:
        if not env.raise_:
            return "CHECK"
        else:
            return "CALL"
    else:
        return "RAISE"


