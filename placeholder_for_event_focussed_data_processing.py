def prepare_event_focused_data(player_performance, mouse_keyboard_data, window_size=5):
    event_data = []
    for _, event in player_performance.iterrows():
        event_time = event['timestamp']
        start_time = event_time - pd.Timedelta(seconds=window_size)
        end_time = event_time + pd.Timedelta(seconds=window_size)
        
        period_data = mouse_keyboard_data[
            (mouse_keyboard_data['timestamp'] >= start_time) &
            (mouse_keyboard_data['timestamp'] <= end_time)
        ]
        
        if not period_data.empty:
            freq_data = create_frequency_data(period_data, input_columns, start_time)
            freq_data['Player'] = event['killer_ip']
            freq_data['Latency'] = event['latency']
            freq_data['Event_Type'] = 'Kill' if event['killer_ip'] == event['Player'] else 'Death'
            event_data.append(freq_data)
    
    return pd.concat(event_data, ignore_index=True)

# Usage in your main code
all_event_data = []
for player in selected_players:
    mouse_keyboard_data = load_mouse_data(player.split('_')[1])
    if mouse_keyboard_data is not None:
        player_events = player_performance[
            (player_performance['killer_ip'] == player) |
            (player_performance['victim_ip'] == player)
        ]
        event_data = prepare_event_focused_data(player_events, mouse_keyboard_data)
        all_event_data.append(event_data)

df = pd.concat(all_event_data, ignore_index=True)


"""
This event-focused approach will give you a more targeted analysis of how latency affects player performance during critical moments. You can then use this df in all your subsequent analyses.
Remember to update your interpretation of results to reflect this new focus on events. For example, in the bootstrap analysis, you might say:
"This bootstrap analysis now focuses on the input frequencies during the 5 seconds before and after kill/death events. The results show how latency affects player inputs during these critical moments. Non-overlapping confidence intervals between latency levels suggest that latency significantly impacts player behavior during key gameplay events."
These changes should significantly improve the quality and relevance of your analysis. Let me know if you need any clarification or have any questions about implementing these changes!
"""