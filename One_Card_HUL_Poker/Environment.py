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
    def __init__(self, start_id):
        self._switch = [0, 0]
        self.dealer = start_id

    def set(self, id):
        self._switch[id] = 1

    def check(self):
        if self._switch[0] == 1 and self._switch[1] == 1:
            return True
        else:
            return False

    def reset(self):
        self._switch = [0, 0]

    def raise_reset(self, id):
        opp_id = 0 if id == 1 else 1
        self._switch[id] = 1
        self._switch[opp_id] = 0

    def set_dealer(self):
        self.dealer = 0 if self.dealer == 1 else 1
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
        random.shuffle(self._deck)

    def deal_card(self):
        card = self._deck.pop()
        self._dealt_cards.append(card)
        return card

class Environment:
    def __init__(self, players, raise_amount = 2, blinds = 1):
        self.pot = 0
        self.board = None
        self.players = players
        self.raise_amount = raise_amount
        self.call_amount = 0
        self.blinds = blinds
        self.turn_tracker = Turn_Tracker(0)
        self.deck = Deck()
        self.raise_ = False
        self.reward = queue.Queue()


    def start_game(self, stack_size):
        for player in self.players:
            player.chips = stack_size
            player.chips -= self.blinds
            self.pot += self.blinds
            player.cards = self.deck.deal_card()

        return self.turn_tracker.dealer

    def next_round(self):
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
            player.chips_staked = 0

        self.turn_tracker.reset()
        return self.turn_tracker.set_dealer()

    def action_handler(self, p_id, action):
        o_id = 1 if p_id == 0 else 0
        print(f"Player ID: {p_id} Action: {action} Chips Before: {self.players[p_id].chips} Card: {self.players[p_id].cards} Chips: {self.players[p_id].chips}")

        match action:
            case "FOLD":
                self.players[o_id].chips += self.pot
                return self.next_round()

            case "CHECK":
                self.turn_tracker.set(p_id)
                if self.turn_tracker.check():
                    self.winner()
                    return self.next_round()
                else:
                    return o_id

            case "CALL":
                self.players[p_id].chips -= self.call_amount
                self.pot += self.call_amount
                self.players[p_id].chips_staked += self.call_amount
                self.turn_tracker.set(p_id)
                self.winner()
                return self.next_round()

            case "RAISE":

                self.raise_ = True

                self.turn_tracker.raise_reset(p_id)
                self.pot += min(self.raise_amount, self.players[p_id].chips) + self.call_amount
                self.players[p_id].chips_staked += min(self.raise_amount, self.players[p_id].chips) + self.call_amount
                self.players[p_id].chips -= min(self.raise_amount, self.players[p_id].chips) + self.call_amount


                self.call_amount = min(self.raise_amount, self.players[p_id].chips)
                print(f"Chips After: {self.players[p_id].chips}")
                return o_id

    def winner(self):
        self.board = self.deck.deal_card()
        winner = self.evaluate()
        if winner != 2:
            self.players[winner].chips += self.pot
            self.players[winner].chips_won += self.pot

            print(f"Board card: {self.board}, Winner ID: {winner}, Winner Chips: {self.players[winner].chips}, Pot: {self.pot}")
        else:
            half = self.pot //2
            self.players[0].chips += half
            self.players[1].chips += half

            self.players[1].chips_won += half





    def evaluate(self):
        if self.players[0].cards == self.board:
            return 0
        elif self.players[1].cards == self.board:
            return 1
        elif self.players[0].cards == self.players[1].cards:
            return 2
        else:
            return 0 if self.players[1].cards < self.players[0].cards else 1


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
