import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3

models = {0: "Q-Learning", 1: "Dummy", 2: "Call", 3: "Raise"}
experiments = {0: "Q-Learning v. Dummy", 1: "Dummy v. Call", 2: "Dummy v. Raise", 3: "Model v. Call", 4: "Model v. Raise"}
def winrate(experiment_id, model_id):
    conn = sqlite3.connect('../Game_Log')
    df = pd.read_sql('''
    SELECT winner_id
    FROM Games
    WHERE experiment_id = ?
    ''', conn, params = (experiment_id, ))

    winner = []
    t = -1
    for i in range(200, len(df), 200):
        winner.append(df[i - 200: i].value_counts(normalize=True).get(model_id, 0))
        t = i

    winner.append(df[t:].value_counts(normalize=True).get(model_id, 0))

    plt.plot(winner, marker='o')  # Line plot with markers
    plt.title(f"{experiments[experiment_id]}")  # Add a title
    plt.xlabel(f"Trials in lengths of 200")  # Label for x-axis
    plt.ylabel(f"Winrate of model {models[model_id]}")  # Label for y-axis
    plt.grid(True)  # Add grid for better readability
    plt.savefig(f"./Graphs/{experiments[experiment_id]}.jpg")
    plt.close()



if __name__ == '__main__':
    winrate(0, 0)
    winrate(3, 0)
    winrate(4, 0)
    winrate(1, 2)
    winrate(2, 3)