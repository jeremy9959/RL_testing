
class KhunEnv:
    def __init__(self, players):
        self.N = players  # Players including chance, dictionary of id's that map onto player objects
        self.H = tuple()
        self.sequence = ['c', 'c', 1, 2, 1]
        self.seq_id = 0
        self.pot = 0

    def get_next_turn(self):

        return self.sequence[self.seq_id]


    def sample_action(self, i, a):
        ### Update information sets for each player
        if i == 'c':
            if len(self.H) == 0:
                self.N[1].card = a
                self.pot += 1
                self.N[1].stake += 1
                self.N[1].I = (a,)
            else:
                self.N[2].card = a
                self.pot += 1
                self.N[2].stake += 1
                self.N[2].I = (a,)

        else:
            if a == 'B':
                self.N[i].stake += 1
                self.pot += 1
            elif a == 'C':
                self.N[i].stake += 1
                self.pot += 1
            self.N[1].I += (a,)
            self.N[2].I += (a,)
        self.H += (a,)
        self.seq_id += 1


    def is_terminal(self) -> bool:

        if self.H is None or len(self.H) <= 3:
            return False
        elif len(self.H) == 4:
            if self.H[3] == 'P' or self.H[3] == 'C' or self.H[3] == 'F':
                return True
            else:
                return False
        else:
            return True



    def utility(self) -> dict:
        u = dict()
        winner, looser = self.winner()

        if self.H[3] == 'P' or self.H[3] == 'C':

            u[winner] = self.pot - self.N[1].stake
            u[looser] = -self.N[2].stake
        elif self.H[3] == 'F':
            u[1] = self.pot - self.N[1].stake
            u[2] = -self.N[2].stake

        elif self.H[4] == 'C':
            u[winner] = self.pot - self.N[1].stake
            u[looser] = -self.N[2].stake
        else:
            u[2] = self.pot - self.N[2].stake
            u[1] = -self.N[1].stake
        return u

    def winner(self):
        if self.N[1].card == 'K': return 1, 2
        elif self.N[2].card == 'K': return 2, 1
        elif self.N[1].card == 'Q': return 1, 2
        elif self.N[2].card == 'Q': return 2, 1
    @staticmethod
    def possible_actions(I) -> dict:
        """
        :param I:
        :return dictionary that maps a|I to R(I,a) set to  0 initially:
        """
        if len(I) == 1:
            return {'P': 0, 'B': 0}
        elif len(I) == 2:
            if I[1] == 'B':
                return {'F': 0, 'C': 0}

            elif I[1] == 'P':
                return {'P': 0, 'B': 0}
        elif len(I) == 3:
            return {'F': 0, 'C': 0}


