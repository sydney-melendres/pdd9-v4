import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pytz import timezone
import numpy as np
from scipy import stats
import os

# Load the datasets
mouse_keyboard_data = pd.read_csv('/workspaces/pdd9-v4/mouse_movement_data4.csv')
kills_data = pd.read_csv('/workspaces/pdd9-v4/final-data/player_performance_per_round_adjusted.csv/round_15_player_Player_138.25.249.94.csv')
deaths_data = pd.read_csv('/workspaces/pdd9-v4/round_15_deaths_of_player_Player_138_25_249_94.csv')

# Convert timestamps to datetime
mouse_keyboard_data['timestamp'] = pd.to_datetime(mouse_keyboard_data['timestamp'], unit='s')
kills_data['timestamp'] = pd.to_datetime(kills_data['timestamp'])

# Convert death data timestamps from AEST to UTC
aest = timezone('Australia/Sydney')
utc = timezone('UTC')
deaths_data['timestamp'] = pd.to_datetime(deaths_data['timestamp']).dt.tz_localize(aest).dt.tz_convert(utc).dt.tz_localize(None)

# Get the time range for the round
round_start = min(kills_data['timestamp'].min(), deaths_data['timestamp'].min())
round_end = max(kills_data['timestamp'].max(), deaths_data['timestamp'].max())

# Filter mouse_keyboard_data for the specific round
round_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= round_start) & 
                                 (mouse_keyboard_data['timestamp'] <= round_end)]

# Function to create frequency data
def create_frequency_data(data, columns, start_time):
    # Ensure data is sorted by timestamp
    data = data.sort_values('timestamp')
    
    # Create a datetime range for every second in the round
    date_range = pd.date_range(start=start_time, end=round_end, freq='s')
    
    # Initialize a DataFrame with this range
    freq_data = pd.DataFrame({'timestamp': date_range})
    
    # Function to get the last value in a group
    def get_last_value(group):
        return group.iloc[-1] if len(group) > 0 else 0

    # Get last value in each second for all columns
    for column in columns:
        # Group by second and get the last value
        grouped = data.groupby(data['timestamp'].dt.floor('S'))[column].apply(get_last_value)
        
        # Reindex to include all seconds, forward fill, and reset index
        full_range = pd.date_range(start=grouped.index.min(), end=grouped.index.max(), freq='S')
        filled_data = grouped.reindex(full_range).ffill().reset_index()
        
        # Merge with freq_data
        freq_data = pd.merge(freq_data, filled_data, left_on='timestamp', right_on='index', how='left')
        freq_data[column] = freq_data[column].ffill().fillna(0)
        freq_data = freq_data.drop('index', axis=1)

    # Calculate differences
    for column in columns:
        freq_data[f'{column}_diff'] = freq_data[column].diff().fillna(0)
    
    return freq_data

# Function to find nearest second
def find_nearest_second(time, freq_data):
    return freq_data['timestamp'].iloc[(freq_data['timestamp'] - time).abs().argsort()[0]]

# Function to remove outliers
def remove_outliers(data, column, z_threshold=3):
    if column not in data.columns:
        print(f"Warning: Column '{column}' not found in the data. Available columns: {data.columns.tolist()}")
        return data
    z_scores = np.abs(stats.zscore(data[column]))
    return data[z_scores < z_threshold]

# Create visualizations
input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']

# Create frequency data
freq_data = create_frequency_data(round_data, input_columns, round_start)

# Print column names for debugging
print("Columns in freq_data:", freq_data.columns.tolist())

# Create subplots
fig = make_subplots(rows=3, cols=2, subplot_titles=[f'{col.capitalize()} Frequency Change' for col in input_columns])

for i, col in enumerate(input_columns):
    row = i // 2 + 1
    col_num = i % 2 + 1
    
    diff_col = f'{col}_diff'
    if diff_col not in freq_data.columns:
        print(f"Warning: Column '{diff_col}' not found in freq_data. Skipping this plot.")
        continue
    
    # Remove outliers
    plot_data = remove_outliers(freq_data, diff_col)
    
    # Plot frequency data
    fig.add_trace(go.Scatter(x=plot_data['timestamp'], y=plot_data[diff_col], name=col, mode='lines'), row=row, col=col_num)
    
    # Add kill events
    for _, kill in kills_data.iterrows():
        nearest_time = find_nearest_second(kill['timestamp'], plot_data)
        y_value = plot_data.loc[plot_data['timestamp'] == nearest_time, diff_col].values[0]
        fig.add_trace(go.Scatter(x=[nearest_time], y=[y_value], mode='markers', marker=dict(symbol='triangle-up', size=10, color='green'), name='Kill'), row=row, col=col_num)

    # Add death events
    for _, death in deaths_data.iterrows():
        nearest_time = find_nearest_second(death['timestamp'], plot_data)
        y_value = plot_data.loc[plot_data['timestamp'] == nearest_time, diff_col].values[0]
        fig.add_trace(go.Scatter(x=[nearest_time], y=[y_value], mode='markers', marker=dict(symbol='triangle-down', size=10, color='red'), name='Death'), row=row, col=col_num)

# Update layout
fig.update_layout(height=900, width=1200, title_text="Input Frequency Changes, Kills, and Deaths (UTC)")
fig.update_xaxes(title_text="Time (UTC)")
fig.update_yaxes(title_text="Frequency Change")

# Save the plot
dir_path = 'plots/' + str(os.path.basename(__file__))
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
    print("Directory created successfully!")

fig.write_html(dir_path + '/all_inputs_frequency_change_with_events_utc.html')
print("Interactive Plotly visualization has been saved as 'all_inputs_frequency_change_with_events_utc.html'.")