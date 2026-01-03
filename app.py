from flask import Flask, render_template, jsonify, request
import pandas as pd
from model import optimal_team

app = Flask(__name__)

# Initialize data
data = pd.read_csv('data.csv')
data['position'] = data['Converted'].str[:2]
data['variable'] = data['position'] + '_' + data['Converted']

# Initialize roster spots and salary cap
roster_spots = {
    'QB': 2,
    'WR': 4,
    'TE': 2,
    'RB': 2,
    'KR': 1,
    'DE': 1
}
salary_cap = 194

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/initial_data')
def get_initial_data():
    # Get all available players sorted by points
    available_players = data.sort_values('Points', ascending=False)
    players_list = []
    for _, player in available_players.iterrows():
        players_list.append({
            'name': player['Player'],
            'position': player['position'],
            'points': round(player['Points'], 1),
            'cost': player['Exp_Cost']
        })
    
    return jsonify({
        'players': players_list,
        'roster_spots': roster_spots,
        'salary_cap': salary_cap
    })

@app.route('/api/optimal_team', methods=['POST'])
def get_optimal_team():
    request_data = request.get_json()
    my_team = request_data.get('my_team', [])
    removed_players = request_data.get('removed_players', [])
    remaining_salary = request_data.get('remaining_salary', salary_cap)
    
    # Create a copy of the data for optimization
    optimization_data = data.copy()
    
    # Remove players that are in my_team or removed_players
    optimization_data = optimization_data[
        (~optimization_data['Player'].isin(my_team)) & 
        (~optimization_data['Player'].isin(removed_players))
    ]
    
    # Calculate remaining roster spots
    remaining_roster_spots = roster_spots.copy()
    for player_name in my_team:
        player_info = data[data['Player'] == player_name].iloc[0]
        remaining_roster_spots[player_info['position']] -= 1
    
    # Get optimal team
    optimal_team_suggestion = optimal_team(optimization_data, remaining_roster_spots, remaining_salary)
    
    # Get details for each player in optimal team
    optimal_team_details = []
    for player in optimal_team_suggestion:
        player_info = data[data['Player'] == player].iloc[0]
        optimal_team_details.append({
            'name': player,
            'position': player_info['position'],
            'points': float(round(player_info['Points'], 1)),
            'cost': int(player_info['Exp_Cost'])
        })
    
    return jsonify({
        'optimal_team': optimal_team_details
    })

if __name__ == '__main__':
    app.run(debug=True) 