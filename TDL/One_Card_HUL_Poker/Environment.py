import random
import queue
class Player:
    def __init__(self, id):
        self.id = id
        self.chips = None
        self.cards = None
        self.chips_won = 0
        self.chips_staked = 0

class Turn_Tracker:
    def __init__(self, start_id, player_ids):
        self._switch = [0, 0]
        self.dealer = start_id
        self.p_ids = player_ids

    def set(self, id):
        s_id = 0 if id == self.p_ids[0] else 1
        self._switch[s_id] = 1

    def check(self):
        if self._switch[0] == 1 and self._switch[1] == 1:
            return True
        else:
            return False

    def reset(self):
        self._switch = [0, 0]

    def raise_reset(self, id):
        ind = 0 if id == self.p_ids[0] else 1
        opp_ind = 0 if ind == 1 else 1
        self._switch[ind] = 1
        self._switch[opp_ind] = 0

    def set_dealer(self):
        self.dealer = self.p_ids[0] if self.dealer == self.p_ids[1] else self.p_ids[1]
        return self.dealer

    def is_dealer(self, id):
        return 0 if id != self.dealer else 1

class Deck:
    def __init__(self):
        self._deck = []
        for i in range(2):
            for j in range(2, 14):
                """
                if j == 10:
                    self._deck.append(f"T")
                elif j == 11:
                    self._deck.append(f"J")
                elif j == 12:
                    self._deck.append(f"Q")
                elif j == 13:
                    self._deck.append(f"K")
                elif j == 14:
                    self._deck.append(f"A")
                else:
                """
                self._deck.append(j)

        self._dealt_cards = []

    def shuffle(self):

        while len(self._dealt_cards) > 0:
            self._deck.append(self._dealt_cards.pop())
        assert len(self._dealt_cards) == 0
        random.shuffle(self._deck)

    def deal_card(self):
        card = self._deck.pop()
        self._dealt_cards.append(card)
        return card

class Environment:
    def __init__(self, players, raise_amount = 2, blinds = 1, db = None):
        self.pot = 0
        self.board = None
        self.players = players
        self.raise_amount = raise_amount
        self.call_amount = 0
        self.blinds = blinds
        self.turn_tracker = Turn_Tracker(players[0].id, [players[0].id, players[1].id])
        self.deck = Deck()
        self.raise_ = False
        self.reward = queue.Queue()
        self.db = db



    def start_game(self, stack_size):
        for player in self.players:
            player.chips = stack_size
            player.chips -= self.blinds
            self.pot += self.blinds
            player.cards = self.deck.deal_card()
        self.turn_tracker.reset()
        return self.turn_tracker.dealer

    def next_round(self):

        #print("\n\n\n------NEXT ROUND-----")
        self.deck.shuffle()
        self.reward.put(self.players[1].chips_won - self.players[1].chips_staked)
        if self.players[0].chips <= 0:
            return -1
        elif self.players[1].chips <= 0:
            return -2
        self.raise_ = False
        self.pot = 0
        self.call_amount = 0
        for player in self.players:
            player.chips -= self.blinds
            self.pot += self.blinds
            player.cards = self.deck.deal_card()

            player.chips_won = 0
            player.chips_staked = 1
        if self.players[0].chips <= 0 or self.players[1].chips <= 0:
            #print("Going all in preflop")
            self.winner()
            return self.next_round()
        self.turn_tracker.reset()
        return self.turn_tracker.set_dealer()

    def action_handler(self, p_id, action):
        #print(f"Pot: {self.pot} P1 chips: {self.players[0].chips} P2 chips: {self.players[1].chips}")
        assert self.pot + self.players[0].chips + self.players[1].chips == 40
        assert self.players[0].chips >=  0 and self.players[1].chips >= 0
        o_id = self.players[1].id if p_id == self.players[0].id else self.players[0].id
        p_ind = 0 if p_id == self.players[0].id else 1
        o_ind = 0 if p_ind == 1 else 1
        #print(p_id, p_ind, o_id, o_ind)
        #print(f"Player ID: {p_id} Action: {action} Card: {self.players[p_id].cards}")

        match action:
            case "FOLD":
                self.players[o_ind].chips += self.pot
                self.db.log_round(o_id, self.pot, None)
                return self.next_round()

            case "CHECK":
                self.turn_tracker.set(p_id)
                if self.turn_tracker.check():
                    self.winner()
                    return self.next_round()
                else:
                    return o_id

            case "CALL":
                self.players[p_ind].chips -= self.call_amount
                self.pot += self.call_amount
                self.players[p_ind].chips_staked += self.call_amount
                self.turn_tracker.set(p_id)
                self.winner()
                return self.next_round()

            case "RAISE":

                self.raise_ = True
                curr_raise = min(self.raise_amount, self.players[p_ind].chips - self.call_amount, self.players[o_ind].chips)
                self.turn_tracker.raise_reset(p_id)
                self.pot += curr_raise + self.call_amount
                self.players[p_ind].chips_staked += curr_raise + self.call_amount

                self.players[p_ind].chips -= curr_raise + self.call_amount
                self.call_amount = curr_raise

                #print(f"Chips After: {self.players[p_id].chips}")
                return o_id

    def winner(self):
        self.board = self.deck.deal_card()
        winner = self.evaluate()
        ind = 0 if winner == self.players[0].id else 1
        if winner != -1:
            self.players[ind].chips += self.pot
            self.players[ind].chips_won += self.pot

        else:

            half = self.pot //2
            self.players[0].chips += half
            self.players[1].chips += half

            self.players[1].chips_won += half

        self.db.log_round(winner, self.pot, self.board)





    def evaluate(self):
        if self.players[0].cards == self.board:
            return self.players[0].id
        elif self.players[1].cards == self.board:
            return self.players[1].id
        elif self.players[0].cards == self.players[1].cards:
            return -1
        else:
            return self.players[0].id if self.players[1].cards < self.players[0].cards else self.players[1].id


    def start_over(self, stack_size):
        for player in self.players:
            player.chips = stack_size
            player.cards = None
            player.chips_won = 0
            player.chips_staked = 0
        self.pot = 0
        self.turn_tracker.reset()
        self.deck.shuffle()
        self.raise_ = False
        self.reward = queue.Queue()
        self.call_amount = 0
        self.board = None
