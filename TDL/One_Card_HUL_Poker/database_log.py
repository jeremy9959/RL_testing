import sqlite3
import numpy as np
class DatabaseLog:
    def __init__(self, experiment_id):
        self.experiment_id = experiment_id
        self.conn = sqlite3.connect('../Game_Log')
        self.cursor = self.conn.cursor()
        self.game_id = 0
        self.round_id = 0
        self.turn_id = 0


    def log_game(self, winner_id):
        self.conn.execute('''
        INSERT INTO Games (experiment_id, game_id, winner_id) VALUES (?, ?, ?)
        ''', (self.experiment_id, self.game_id, winner_id))

        self.game_id += 1
        self.round_id = 0
        self.turn_id = 0


    def log_round(self, winner_id, amount_won, table_card):
        self.conn.execute('''
        INSERT INTO Rounds (experiment_id, game_id, round_id, winner_id, amount_won, table_card)
        VALUES (?, ?, ?, ?, ?, ?)''', (self.experiment_id, self.game_id, self.round_id, winner_id, amount_won, table_card))

        self.round_id += 1
        self.turn_id = 0


    def log_action(self, player_id, chips, card, action, pot_size):

        self.conn.execute('''
        INSERT INTO Actions
        (experiment_id, game_id, round_id, player_id, chips, card, action, turn_id, pot_size)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (self.experiment_id, self.game_id, self.round_id,
                           player_id, chips, card, action, self.turn_id, pot_size))

        self.turn_id += 1

    def log_reward(self, model_id, card, stack_size, pot_size, action, reward):
        self.conn.execute('''
                INSERT INTO Rewards
                (experiment_id, model_id ,game_id, round_id, turn_id, card, stack_size, pot_size, action, reward)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (self.experiment_id, model_id, self.game_id, self.round_id,
                        self.turn_id, card, stack_size, pot_size, action, reward))


    def wipe(self, experiment_id):
        self.conn.execute('DELETE FROM Games WHERE experiment_id = ?', (experiment_id,))
        self.conn.execute('DELETE FROM Rounds WHERE experiment_id = ?', (experiment_id,))
        self.conn.execute('DELETE FROM Actions WHERE experiment_id = ?', (experiment_id,))
        self.conn.execute('DELETE FROM Rewards WHERE experiment_id = ?', (experiment_id,))
        self.conn.commit()
        conn = sqlite3.connect("../Q_matrix")
        conn.execute('DELETE FROM QSA WHERE experiment_id = ?', (experiment_id,))
        conn.commit()
        conn.close()


    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def save_Q(self, model_id, Q_table, count_table):
        conn = sqlite3.connect("../Q_matrix")
        it = np.nditer(Q_table, flags=['multi_index'])
        for reward in it:
            cards = it.multi_index[0]
            stack_size = it.multi_index[1]
            pot_size = it.multi_index[2]
            action = it.multi_index[3]
            #print(reward, type(reward.item()), type(.23445))


            conn.execute('''
             INSERT INTO QSA (experiment_id, model_id, card, stack_size, pot_size, action, count, expected_reward) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)
             ''', (self.experiment_id, model_id, cards, stack_size, pot_size, action, count_table[it.multi_index], reward.item()
                   ))

        conn.commit()
        conn.close()
