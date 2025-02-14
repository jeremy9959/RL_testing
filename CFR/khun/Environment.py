from attr import *
class KhunEnv:
    def __init__(self, players):
        self.deck = Deck()
        self.N = players  # Players including chance, dictionary of id's that map onto player objects
        self.H = None
        self.sequence = ['c', 'c', 1, 2, 1]
        self.seq_id = 0
        self.pot = 0


    def get_next_turn(self):
        pass

    def sample_action(self, i, a):
        ### Process action
        ### Update information sets for each player
        ### Update the history
        if i == 'c':
            if self.H is None:
                self.N[1].card = a
                self.pot += 1
                self.N[1].stake += 1
            else:
                self.N[2].card = a
                self.pot += 1
                self.N[2].stake += 1
        else:
            if a == 'B':
                self.N[i].stake += 1
                self.pot += 1
            elif a == 'C':
                self.N[i].stake += 1
                self.pot += 1
            self.H += (a, )

    def is_terminal(self) -> bool:
        if self.H is None or len(self.H) <= 3:
            return False
        elif len(self.H) == 4:
            if self.H[3] == 'P' or self.H[3] == 'C':
                return True
            else:
                return False
        else:
            return True



    def utility(self, i) -> int:
        pass


    @staticmethod
    def possible_actions(I) -> dict:
        """
        :param I:
        :return dictionary that maps a|I to R(I,a) set to  0 initially:
        """
        if len(I) == 1:
            return {'P': 0, 'B': 0}

        elif I[1] == 'B':
            return {'F': 0, 'C': 0}

        elif I[1] == 'P':
            return {'P': 0, 'B': 0}

        else:
            return {'F': 0, 'C': 0}


