import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

def process_csv(file_path):
    df = pd.read_csv(file_path)
    player_id = df['player_id'].iloc[0]
    player_ip = df['player_ip'].iloc[0]
    
    kills = df[df['event'] == 'Kill'][df['killer_ip'] == player_ip].shape[0]
    deaths = df[df['event'] == 'Kill'][df['victim_ip'] == player_ip].shape[0]
    avg_latency = df['latency'].mean()
    
    return {
        'player_id': player_id,
        'player_ip': player_ip,
        'kills': kills,
        'deaths': deaths,
        'kd_ratio': kills / deaths if deaths > 0 else kills,
        'avg_latency': avg_latency
    }

def analyze_player_performance(directory):
    all_files = glob.glob(os.path.join(directory, "*.csv"))
    player_stats = [process_csv(file) for file in all_files]
    return pd.DataFrame(player_stats)

def plot_kd_ratio_vs_latency(df):
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=df, x='avg_latency', y='kd_ratio')
    plt.title('K/D Ratio vs Average Latency')
    plt.xlabel('Average Latency')
    plt.ylabel('K/D Ratio')
    plt.savefig('kd_ratio_vs_latency.png')
    plt.close()

def plot_kills_deaths_distribution(df):
    plt.figure(figsize=(12, 8))
    sns.histplot(data=df, x='kills', kde=True, color='blue', label='Kills')
    sns.histplot(data=df, x='deaths', kde=True, color='red', label='Deaths')
    plt.title('Distribution of Kills and Deaths')
    plt.xlabel('Count')
    plt.ylabel('Frequency')
    plt.legend()
    plt.savefig('kills_deaths_distribution.png')
    plt.close()

def main(directory):
    df = analyze_player_performance(directory)
    plot_kd_ratio_vs_latency(df)
    plot_kills_deaths_distribution(df)
    print(df.describe())

if __name__ == "__main__":
    main("final-data/player_performance_per_round.csv")