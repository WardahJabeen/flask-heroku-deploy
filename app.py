from flask import Flask, render_template
import requests
import json
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from io import BytesIO
import base64

app = Flask(__name__)

# URL to fetch data
url = "https://portkey-2a1ae-default-rtdb.firebaseio.com/playtesting1_analytics.json"

# Fetch the data from the Firebase
def fetch_data(url):
    response = requests.get(url)
    data = response.json()
    return data

# Fetch the data
data = fetch_data(url)
print("Fetched Data:", data)  # Debug statement to print fetched data

# Parse and use the data
def parse_data(data, metric_left, metric_right):
    level_data = {}
    for player in data.values():
        try:
            level = int(player['level'])   # int
            value_left = player[metric_left]
            value_right = player[metric_right]
        
            if level not in level_data:
                level_data[level] = {'left': 0, 'right': 0, 'count': 0}
        
            level_data[level]['left'] += value_left
            level_data[level]['right'] += value_right
            level_data[level]['count'] += 1
        except KeyError as e:
            print(f"KeyError: {e} - This player data is missing expected keys.")
        except Exception as e:
            print(f"Unexpected error: {e}")

    # Calculate the averages
    levels = sorted(level_data.keys())
    average_left = [level_data[level]['left'] / level_data[level]['count'] for level in levels]
    average_right = [level_data[level]['right'] / level_data[level]['count'] for level in levels]

    return levels, average_left, average_right

# Plot
def create_plot(levels, average_left, average_right, xlabel, ylabel, title, left_label, right_label):
    fig, ax = plt.subplots()
    bar_width = 0.3
    # Stack
    p1 = ax.bar(levels, average_left, bar_width, label=left_label)
    p2 = ax.bar(levels, average_right, bar_width, bottom=average_left, label=right_label)

    # Labels and titles for axis and graph
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(levels)
    ax.legend()

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))  # int

    # Text annotations
    for level, left, right in zip(levels, average_left, average_right):
        if left > 0:
            ax.text(level, left / 2, f'{left:.2f}', ha='center', va='center', color='white')
        if right > 0:
            ax.text(level, left + right / 2, f'{right:.2f}', ha='center', va='center', color='white')

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close(fig)
    return plot_url

# Metric 2 - Level Completion Reason
# Function to fetch and parse data for the first plot
def fetch_and_parse_data_2():
    # Parse the data
    level_data = {}
    for player in data.values():
        try:
            level = int(player['level'])
            reason = player['reasonforFinshingLevel']

            if level not in level_data:
                level_data[level] = {'collision': 0, 'time_up': 0}

            if reason == 1:
                level_data[level]['collision'] += 1
            elif reason == 2:
                level_data[level]['time_up'] += 1
        except KeyError as e:
            print(f"KeyError: {e} - This player data is missing expected keys.")
        except Exception as e:
            print(f"Unexpected error: {e}")

    # Helper variables
    levels = sorted(level_data.keys())
    collisions = [level_data[level]['collision'] for level in levels]
    time_ups = [level_data[level]['time_up'] for level in levels]

    return levels, collisions, time_ups

# Function to create the first plot
def create_plot_2(levels, collisions, time_ups):
    fig, ax = plt.subplots()
    bar_width = 0.3
    p1 = ax.bar(levels, collisions, bar_width, label='Collision')
    p2 = ax.bar(levels, time_ups, bar_width, bottom=collisions, label='Time Up')

    # Labels and title on the graph
    ax.set_xlabel('Levels')
    ax.set_ylabel('Total Number of Game Completions')
    ax.set_title('Level Completion Reason')
    ax.set_xticks(levels)
    ax.legend()
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    for level, coll, time in zip(levels, collisions, time_ups):
        if coll > 0:
            ax.text(level, coll / 2, str(coll), ha='center', va='center', color='white')
        if time > 0:
            ax.text(level, coll + time / 2, str(time), ha='center', va='center', color='white')

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close(fig)
    return plot_url

@app.route('/')
def index():
    plots = []

    # Metric 1: Scores Collected per Level
    levels, average_scores_left, average_scores_right = parse_data(data, 'scoreLeft', 'scoreRight')
    plot_url = create_plot(levels, average_scores_left, average_scores_right, 'Levels', 'Average Score Props Collected', 'Scores Collected per Level', 'Left Screen', 'Right Screen')
    plots.append(f'data:image/png;base64,{plot_url}')

    # Metric 2: Level Completion Reason
    levels_1, collisions, time_ups = fetch_and_parse_data_2()
    plot_url = create_plot_2(levels_1, collisions, time_ups)
    plots.append(f'data:image/png;base64,{plot_url}')

    # Metric 3: Usage of Control-Flipping Props
    levels, average_props_left, average_props_right = parse_data(data, 'totalCtrlSwitchPropCollectedLeft', 'totalCtrlSwitchPropCollectedRight')
    plot_url = create_plot(levels, average_props_left, average_props_right, 'Levels', 'Average Control-Flipping Props', 'Usage of Control-Flipping Props', 'Props Left', 'Props Right')
    plots.append(f'data:image/png;base64,{plot_url}')

    # Metric 4: Collisions after Control-Flip per Level
    levels, average_collisions_left, average_collisions_right = parse_data(data, 'collisionDueToCtrlFlipLeft', 'collisionDueToCtrlFlipRight')
    plot_url = create_plot(levels, average_collisions_left, average_collisions_right, 'Levels', 'Average Number of Obstacle Collisions', 'Collisions after Control-Flip per Level', 'Collisions Left', 'Collisions Right')
    plots.append(f'data:image/png;base64,{plot_url}')

    return render_template('index.html', plots=plots)

if __name__ == '__main__':
    app.run(debug=True)
