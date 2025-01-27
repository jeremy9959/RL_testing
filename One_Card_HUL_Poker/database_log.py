import sqlite3
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


    def log_action(self, player_id, chips, card, action):

        self.conn.execute('''
        INSERT INTO Actions
        (experiment_id, game_id, round_id, player_id, chips, card, action, turn_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                          (self.experiment_id, self.game_id, self.round_id,
                           player_id, chips, card, action, self.turn_id))

        self.turn_id += 1


    def wipe(self):
        self.conn.execute('DELETE FROM Games')
        self.conn.execute('DELETE FROM Rounds')
        self.conn.execute('DELETE FROM Actions')
        self.conn.commit()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
