import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3

models = {0: "SARSA", 1: "Dummy", 2: "Call", 3: "Raise", 4: "Q-Learning"}
experiments = {0: "SARSA v. Dummy", 1: "Dummy v. Call", 2: "Dummy v. Raise", 3: "SARSA v. Call", 4: "SARSA v. Raise",
               5: "Q-Learning v. Dummy", 6: "Q-Learning v. Call", 7: "Q-Learning v. Raise" }
actions = {0: "FOLD", 1: "CALL", 2: "RAISE"}
def winrate(experiment_id, model_id):
    conn = sqlite3.connect('../Game_Log')
    df = pd.read_sql('''
    SELECT winner_id
    FROM Games
    WHERE experiment_id = ?
    ''', conn, params = (experiment_id, ))

    winner = []
    t = -1
    for i in range(2000, len(df), 2000):
        winner.append(df[i - 2000: i].value_counts(normalize=True).get(model_id, 0))
        t = i

    winner.append(df[t:].value_counts(normalize=True).get(model_id, 0))

    plt.plot(winner, marker='o')  # Line plot with markers
    plt.title(f"{experiments[experiment_id]}")  # Add a title
    plt.xlabel(f"Trials in lengths of 200")  # Label for x-axis
    plt.ylabel(f"Winrate of model {models[model_id]}")  # Label for y-axis
    plt.grid(True)  # Add grid for better readability
    plt.savefig(f"./Graphs/{experiments[experiment_id]}.jpg")
    plt.close()

def average_reward_v_cards(model_id, action_id):
    conn = sqlite3.connect('../Q_matrix')
    df = pd.read_sql('''SELECT card, AVG(expected_reward)
                        FROM QSA
                        WHERE model_id = ? and action = ? and count >= 3000
                        GROUP BY card''', conn, params = (model_id, action_id, ))
    plt.plot(df.iloc[:, 0], df.iloc[:, 1], marker='o', linestyle='-')
    plt.title(f"{models[model_id]} graph of card v. expected reward with action {actions[action_id]}")
    plt.xlabel(f"Card number (-2)")  # Label for x-axis
    plt.ylabel(f"Average reward for action {actions[action_id]}")  # Label for y-axis
    plt.grid(True)  # Add grid for better readability
    plt.savefig(f"./Graphs/{models[model_id]}Q_{actions[action_id]}.jpg")
    plt.close()

def average_reward_v_pot_size(model_id, action_id, card):
    conn = sqlite3.connect('../Q_matrix')
    df = pd.read_sql('''SELECT pot_size, AVG(expected_reward)
                        FROM QSA
                        WHERE model_id = ? and action = ? and card = ? and count >= 2000
                        GROUP BY pot_size, card, action''', conn, params = (model_id, action_id, card, ))
    plt.plot(df.iloc[:, 0], df.iloc[:, 1], marker='o', linestyle='-')
    plt.title(f"{models[model_id]} graph of pot_size v. expected reward with action {actions[action_id]} and card {card}")  # Add a title
    plt.xlabel(f"pot size")  # Label for x-axis
    plt.ylabel(f"Average reward for action {actions[action_id]} and card {card}")  # Label for y-axis
    plt.grid(True)  # Add grid for better readability
    plt.savefig(f"./Graphs/action_card/{models[model_id]}{actions[action_id]}{card}.jpg")
    plt.close()
    pass
if __name__ == '__main__':
    """
    winrate(0, 0)
    winrate(3, 0)
    
    winrate(1, 2)
    winrate(2, 3)
    winrate(5, 4)
    winrate(6, 4)
    winrate(7, 4)

    """
    average_reward_v_cards(0, 0)
    average_reward_v_cards(0, 1)
    average_reward_v_cards(0, 2)
    for i in range(12):
        for j in range(3):
            average_reward_v_pot_size(0, j, i)
    winrate(4, 0)

