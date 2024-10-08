import pandas as pd
from config import LOG_FOLDER, PROCESSED_DATA_FOLDER, RAW_DATA_FOLDER

input_path = f'{PROCESSED_DATA_FOLDER}/remove_break_rounds.csv'
output_path = f'{PROCESSED_DATA_FOLDER}/no_blanks.csv'

# Read the CSV file
df = pd.read_csv(input_path)

# Function to fill missing values for a row
def fill_missing_values(row, previous_rows):
    if pd.isna(row['player_id']):
        previous_kills = previous_rows[(previous_rows['killer_ip'] == row['killer_ip']) & (previous_rows['killer_id'] == row['killer_id'])]
        if not previous_kills.empty:
            previous_kill = previous_kills.iloc[-1]
            return pd.Series({
                'player_id': previous_kill['player_id'],
                'score': previous_kill['score'] + 1,
                'player_ip': previous_kill['player_ip'],
                'points': previous_kill['points'] + 1
            })
        else:
            return pd.Series({
                'player_id': row['killer_id'],
                'score': 1,
                'player_ip': row['killer_ip'],
                'points': 1
            })
    return row

# Apply the function to fill missing values
df = df.apply(lambda row: fill_missing_values(row, df.loc[:row.name-1]), axis=1)

# Fill remaining NaN values with defaults
df['player_id'] = df['player_id'].ffill()
df['score'] = df['score'].fillna(0)
df['player_ip'] = df['player_ip'].ffill()
df['points'] = df['points'].fillna(0)

# Reorder columns
column_order = [
    'timestamp', 'game_round', 'map', 'latency', 'event', 'killer_id', 'victim_id', 'weapon_id',
    'killer_ip', 'victim_ip', 'weapon', 'player_id', 'score', 'player_ip', 'points', 'log_line'
]

# Reorder the DataFrame columns
df = df[column_order]

# Save the filled and reordered DataFrame to a new CSV file
df.to_csv(output_path, index=False)

print(f"Filled and reordered round score summary saved to {output_path}")