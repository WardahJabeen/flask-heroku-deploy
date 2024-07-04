from flask import Flask, render_template
import requests
import json
import plotly.graph_objs as go
from plotly.subplots import make_subplots

app = Flask(__name__)

# URL to fetch data
url = "https://portkey-2a1ae-default-rtdb.firebaseio.com/playtesting1_analytics.json"

# Fetch data from Firebase
def fetch_data(url):
    response = requests.get(url)
    data = response.json()
    return data

# Parse and use the data
def parse_data(data, metric_left, metric_right):
    level_data = {}
    for player in data.values():
        level = int(player['level'])
        value_left = player[metric_left]
        value_right = player[metric_right]

        if level not in level_data:
            level_data[level] = {'left': 0, 'right': 0, 'count': 0}

        level_data[level]['left'] += value_left
        level_data[level]['right'] += value_right
        level_data[level]['count'] += 1

    # Calculate the averages
    levels = sorted(level_data.keys())
    average_left = [level_data[level]['left'] / level_data[level]['count'] for level in levels]
    average_right = [level_data[level]['right'] / level_data[level]['count'] for level in levels]

    return levels, average_left, average_right

# Fetch and parse the data
data = fetch_data(url)
levels, average_scores_left, average_scores_right = parse_data(data, 'scoreLeft', 'scoreRight')
levels, average_props_left, average_props_right = parse_data(data, 'totalCtrlSwitchPropCollectedLeft', 'totalCtrlSwitchPropCollectedRight')
levels, average_collisions_left, average_collisions_right = parse_data(data, 'collisionDueToCtrlFlipLeft', 'collisionDueToCtrlFlipRight')

# Create the plots
def create_plot(levels, average_left, average_right, title, left_label, right_label):
    fig = make_subplots()

    fig.add_trace(go.Bar(x=levels, y=average_left, name=left_label))
    fig.add_trace(go.Bar(x=levels, y=average_right, name=right_label))

    fig.update_layout(title=title, barmode='stack', xaxis_title='Levels', yaxis_title='Average Value')
    return fig

@app.route('/')
def index():
    fig1 = create_plot(levels, average_scores_left, average_scores_right, 'Scores Collected per Level', 'Left Screen', 'Right Screen')
    fig2 = create_plot(levels, average_props_left, average_props_right, 'Usage of Control-Flipping Props', 'Props Left', 'Props Right')
    fig3 = create_plot(levels, average_collisions_left, average_collisions_right, 'Collisions after Control-Flip per Level', 'Collisions Left', 'Collisions Right')

    plots = [fig1.to_html(full_html=False), fig2.to_html(full_html=False), fig3.to_html(full_html=False)]
    return render_template('index.html', plots=plots)

if __name__ == '__main__':
    app.run(debug=True)
