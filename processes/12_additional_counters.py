import pandas as pd
from config import LOG_FOLDER, PROCESSED_DATA_FOLDER, RAW_DATA_FOLDER

# Create summary dataframes for each round
input_path = f'{PROCESSED_DATA_FOLDER}/ignore_suicides.csv'  # path
output_path = f'{PROCESSED_DATA_FOLDER}/player_performance.csv'  # path

# Load the input CSV file
df = pd.read_csv(input_path)

# Drop unnecessary columns, but keep 'killer_id' and 'victim_id'
drop = {'log_line', 'event', 'weapon_id', 'weapon', 'score', 'points', 'log_score'}
df.drop(columns=drop, inplace=True)

# Adding the new columns with initial values set to 0
df['suicide_count'] = 0
df['deaths_total'] = 0

# Get unique player IDs from the data
players = df['player_id'].unique()

for player in players:
    df[f'killed_by_Player_{player}'] = 0
    df[f'killed_Player_{player}'] = 0

# Function to calculate the counts for each round
def calculate(group):
    group = group.reset_index(drop=True)  # Reset index without adding columns
    # Mark suicides
    group['is_suicide'] = group['killer_id'] == group['player_id']
    
    # Calculate cumulative suicides
    group['suicide_count'] = group.groupby('player_id')['is_suicide'].cumsum()
    
    # Check and update killed_Player counters
    for player in players:
        killed_mask = group['victim_id'] == player
        group[f'killed_Player_{player}'] = killed_mask.cumsum()

    return group

def calculate_killed_by(group):
    # Reset index without adding columns
    group = group.reset_index(drop=True)
    for player in players:
        killed_by_mask = group['killer_id'] == player
        group[f'killed_by_Player_{player}'] = killed_by_mask.cumsum()
        
    return group

def calculate_total_deaths(group):
    # Calculate deaths total
    group['deaths_total'] = group.groupby('victim_id').cumcount() + 1
    return group

# Applying the functions to each game round
df = df.groupby(['game_round', 'player_id']).apply(calculate).reset_index(drop=True)
df = df.groupby(['game_round', 'victim_id']).apply(calculate_killed_by).reset_index(drop=True)
df = df.groupby('game_round').apply(calculate_total_deaths).reset_index(drop=True)

# Drop the 'is_suicide' column as it's no longer needed
df.drop(columns=['is_suicide'], inplace=True)

# Saving the updated and filtered dataframe to the output CSV file
df.to_csv(output_path, index=False)

print(f"Suicide counts, total deaths and deaths from each player_id by round have been recorded in {output_path}")