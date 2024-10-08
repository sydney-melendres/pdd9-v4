import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from datetime import datetime, timedelta
import pytz
import statsmodels.api as sm
from statsmodels.formula.api import poisson
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scipy.stats import chisquare, anderson_ksamp
import gc

# Set the page to wide mode
st.set_page_config(layout="wide")

# Load the datasets
@st.cache_data
def load_data():
    try:
        player_performance = pd.read_csv('final-data/player_performance.csv', parse_dates=['timestamp'])
        return player_performance
    except Exception as e:
        st.error(f"Error loading the player performance data: {str(e)}")
        return None

@st.cache_data
def load_mouse_data(ip_address):
    try:
        filename = f'{ip_address}_activity_data.csv'
        return pd.read_csv(filename)
    except Exception as e:
        st.error(f"Error loading the mouse movement data for IP {ip_address}: {str(e)}")
        return None

player_performance = load_data()

if player_performance is not None:
    # Define timezones
    utc = pytz.UTC
    aest = pytz.timezone('Australia/Sydney')

    # Function to convert timestamp to AEST
    def to_aest(time_obj):
        if isinstance(time_obj, (int, float)):
            time_obj = datetime.fromtimestamp(time_obj)
        elif isinstance(time_obj, str):
            time_obj = pd.to_datetime(time_obj)
        
        if time_obj.tzinfo is None:
            time_obj = utc.localize(time_obj)
        return time_obj.astimezone(aest)

    # Convert timestamps for player performance data
    player_performance['timestamp'] = player_performance['timestamp'].apply(to_aest)

# Function to create frequency data
def create_frequency_data(data, columns, start_time):
    st.write("Debug: create_frequency_data input")
    st.write(f"Data shape: {data.shape}")
    st.write(f"Columns: {columns}")
    st.write(f"Start time: {start_time}")

    data = data.sort_values('timestamp')
    date_range = pd.date_range(start=start_time, periods=600, freq='s')
    freq_data = pd.DataFrame({'timestamp': date_range})
    
    def get_last_value(group):
        return group.iloc[-1] if len(group) > 0 else 0

    for column in columns:
        grouped = data.groupby(data['timestamp'].dt.floor('s'))[column].apply(get_last_value)
        if grouped.empty:
            st.warning(f"No data for column {column}")
            continue
        
        start = grouped.index.min()
        end = grouped.index.max()
        
        if pd.isnull(start) or pd.isnull(end):
            st.warning(f"NaT values found in grouped data for column {column}")
            continue
        
        full_range = pd.date_range(start=start, end=end, freq='s')
        filled_data = grouped.reindex(full_range).ffill().reset_index()
        freq_data = pd.merge(freq_data, filled_data, left_on='timestamp', right_on='index', how='left')
        freq_data[column] = freq_data[column].ffill().fillna(0)
        freq_data = freq_data.drop('index', axis=1)

    for column in columns:
        freq_data[f'{column}_diff'] = freq_data[column].diff().fillna(0)
    
    st.write("Debug: create_frequency_data output")
    st.write(f"Freq data shape: {freq_data.shape}")
    st.write(f"Freq data columns: {freq_data.columns}")
    
    return freq_data

    # Streamlit app
    st.title('Comprehensive Player Performance Analysis')

    # Sidebar for selections
    st.sidebar.header('Filters and Analyses')

    # Player selection
    all_players = pd.concat([player_performance['killer_ip'], player_performance['victim_ip']]).unique()
    selected_players = st.sidebar.multiselect('Select Players', all_players)

    # Latency selection
    all_latencies = player_performance['latency'].unique()
    selected_latencies = st.sidebar.multiselect('Select Latencies', all_latencies)

    # Input column selection
    input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']
    selected_column = st.sidebar.selectbox('Select Input Column', input_columns)

    # Analysis selection
    st.sidebar.header('Select Analyses')
    
    st.sidebar.subheader('Recommended Methods')
    show_poisson = st.sidebar.checkbox('Poisson Regression', value=True)
    show_negative_binomial = st.sidebar.checkbox('Negative Binomial Regression')
    show_glm = st.sidebar.checkbox('Generalized Linear Model (GLM)')
    show_chi_square = st.sidebar.checkbox('Chi-square Goodness-of-fit Test')
    
    st.sidebar.subheader('Additional Methods')
    show_cdf = st.sidebar.checkbox('Show CDF')
    show_qq = st.sidebar.checkbox('Show Q-Q Plot')
    show_anova = st.sidebar.checkbox('Perform ANOVA')
    show_kruskal = st.sidebar.checkbox('Kruskal-Wallis Test')
    show_anderson = st.sidebar.checkbox('Anderson-Darling Test')
    show_bootstrap = st.sidebar.checkbox('Bootstrap Analysis')

    if selected_players and selected_latencies:
        all_freq_data = []

        for player in selected_players:
            mouse_keyboard_data = load_mouse_data(player.split('_')[1])
            if mouse_keyboard_data is None:
                st.warning(f"No mouse movement data available for {player}")
                continue

            mouse_keyboard_data['timestamp'] = pd.to_datetime(mouse_keyboard_data['timestamp'], unit='s')
            mouse_keyboard_data['timestamp'] = mouse_keyboard_data['timestamp'].dt.tz_localize(None)

            for latency in selected_latencies:
                latency_data = player_performance[(player_performance['killer_ip'] == player) & 
                                                (player_performance['latency'] == latency)]
                if not latency_data.empty:
                    start = latency_data['timestamp'].min().replace(tzinfo=None)
                    end = start + timedelta(minutes=10)
                    period_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= start) & 
                                                    (mouse_keyboard_data['timestamp'] <= end)]
                    
                    if period_data.empty:
                        st.warning(f"No data for player {player} at latency {latency}")
                        continue
                    
                    try:
                        freq_data = create_frequency_data(period_data, input_columns, start)
                        freq_data['Player'] = player
                        freq_data['Latency'] = latency
                        all_freq_data.append(freq_data)
                    except Exception as e:
                        st.error(f"Error creating frequency data for player {player} at latency {latency}: {str(e)}")

        if all_freq_data:
            df = pd.concat(all_freq_data, ignore_index=True)
            
            # Data cleaning and preprocessing
            st.subheader("Data Cleaning and Preprocessing")
            st.write("Original data types:")
            st.write(df.dtypes)
            
            # Convert 'Latency' to numeric, removing any non-numeric characters
            df['Latency'] = pd.to_numeric(df['Latency'].astype(str).str.extract('(\d+)', expand=False), errors='coerce')
            
            # Convert selected column to numeric
            df[f'{selected_column}_diff'] = pd.to_numeric(df[f'{selected_column}_diff'], errors='coerce')
            
            # Remove rows with NaN values
            df = df.dropna(subset=[f'{selected_column}_diff', 'Latency'])
            
            # Ensure 'Latency' is integer type
            df['Latency'] = df['Latency'].astype(int)
            
            # Remove timezone information from timestamp column
            df['timestamp'] = df['timestamp'].dt.tz_localize(None)
            
            st.write("Cleaned data types:")
            st.write(df.dtypes)
            
            st.write("Data sample after cleaning:")
            st.write(df.head())
            
            st.write(f"Number of rows after cleaning: {len(df)}")
        
        if show_cdf:
            st.subheader('Cumulative Distribution Function (CDF)')
            st.write("The CDF shows the probability that the input frequency is less than or equal to a given value. "
                        "It helps compare distributions across different latencies or players.")
            
            fig_cdf = go.Figure()
            for (player, latency), group in df.groupby(['Player', 'Latency']):
                data = group[f'{selected_column}_diff']
                sorted_data = np.sort(data)
                cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
                fig_cdf.add_trace(go.Scatter(x=sorted_data, y=cdf, mode='lines',
                                                name=f'{player} - {latency}ms'))
            
            fig_cdf.update_layout(title=f'CDF of {selected_column} (Events per Second)',
                                    xaxis_title='Events per Second',
                                    yaxis_title='Cumulative Probability')
            st.plotly_chart(fig_cdf)
            del fig_cdf
            gc.collect()
            
            st.write("Interpretation: Look for differences in the CDF curves between latencies. "
                        "If the curves are similar, it suggests that latency may not have a significant effect on the input frequency. "
                        "If there are noticeable differences, especially in the steepness or position of the curves, "
                        "it may indicate that latency is affecting the input patterns.")

        if show_qq:
            st.subheader('Q-Q Plot')
            st.write("The Q-Q plot compares the distribution of the data to a normal distribution. "
                        "Points following a straight line suggest the data is normally distributed.")
            
            fig_qq = go.Figure()
            for (player, latency), group in df.groupby(['Player', 'Latency']):
                data = group[f'{selected_column}_diff']
                qq = stats.probplot(data, dist='norm')
                fig_qq.add_trace(go.Scatter(x=qq[0][0], y=qq[0][1], mode='markers',
                                            name=f'{player} - {latency}ms'))
            
            fig_qq.update_layout(title=f'Q-Q Plot of {selected_column} (Events per Second)',
                                    xaxis_title='Theoretical Quantiles',
                                    yaxis_title='Sample Quantiles')
            st.plotly_chart(fig_qq)
            del fig_qq
            gc.collect()
            
            st.write("Interpretation: If the points closely follow the diagonal line, it suggests that the data is normally distributed. "
                        "Deviations from the line, especially at the tails, indicate departures from normality. "
                        "This can help in deciding whether to use parametric or non-parametric tests for further analysis.")

        if show_anova:
            st.subheader('ANOVA Results')
            st.write("ANOVA tests if there are significant differences in the means across different groups (latencies).")
            
            try:
                anova_groups = [group[f'{selected_column}_diff'].values for name, group in df.groupby('Latency')]
                f_statistic, p_value = stats.f_oneway(*anova_groups)
                
                st.write(f"F-statistic: {f_statistic:.4f}")
                st.write(f"p-value: {p_value:.4f}")
                st.write("A small p-value (< 0.05) suggests significant differences between latencies.")
                
                st.write("Interpretation: If the p-value is less than 0.05, it suggests that there are significant differences "
                        "in the mean input frequency across different latencies. This would indicate that latency has a "
                        "measurable effect on player input patterns. If the p-value is greater than 0.05, it suggests that "
                        "there's no strong evidence of latency affecting input frequency.")
            except Exception as e:
                st.error(f"An error occurred during ANOVA: {str(e)}")

        if show_poisson:
            st.subheader('Poisson Regression Results')
            st.write("Poisson regression models count data and can test for the effect of latency on the rate of events.")
            
            try:
                model = poisson(f"{selected_column}_diff ~ C(Latency)", data=df).fit()
                st.write(model.summary())
                
                st.write("\nIncident Rate Ratios:")
                st.write(np.exp(model.params))
                st.write("\nConfidence Intervals for IRR:")
                st.write(np.exp(model.conf_int()))
                
                st.write("Interpretation: Look at the coefficients for each latency level. Positive coefficients suggest an increase "
                        "in input frequency compared to the baseline, while negative coefficients suggest a decrease. "
                        "The p-values indicate whether these effects are statistically significant. "
                        "The Incident Rate Ratios (IRR) show the multiplicative effect of each latency level on the input frequency. "
                        "An IRR > 1 indicates an increase in frequency, while IRR < 1 indicates a decrease.")
            except Exception as e:
                st.error(f"An error occurred during Poisson regression: {str(e)}")

        if show_negative_binomial:
            st.subheader('Negative Binomial Regression Results')
            st.write("Negative Binomial regression is useful when the data is overdispersed (variance > mean).")
            
            try:
                # Create dummy variables for Latency
                latency_dummies = pd.get_dummies(df['Latency'], prefix='Latency', drop_first=True)
                
                # Combine with the constant term
                exog = sm.add_constant(latency_dummies)
                
                st.write("Exogenous variables:")
                st.write(exog.head())
                st.write("Exogenous variables data types:")
                st.write(exog.dtypes)
                
                st.write(f"Endogenous variable ({selected_column}_diff) statistics:")
                st.write(df[f'{selected_column}_diff'].describe())
                
                # Ensure the endogenous variable is non-negative
                endog = np.maximum(df[f'{selected_column}_diff'], 0)
                
                # Fit the model
                model = sm.GLM(endog, 
                                exog, 
                                family=sm.families.NegativeBinomial(alpha=1.0))
                results = model.fit()
                
                st.write(results.summary())
                
                st.write("Interpretation: Similar to Poisson regression, look at the coefficients and their p-values. "
                            "The key difference is that Negative Binomial regression allows for more variability in the data. "
                            "If the results differ significantly from the Poisson regression, it suggests that overdispersion "
                            "is present and the Negative Binomial model may be more appropriate.")
            except Exception as e:
                st.error(f"An error occurred during Negative Binomial regression: {str(e)}")
                st.write("Error details:")
                st.write(f"Exog shape: {exog.shape}")
                st.write(f"Endog shape: {endog.shape}")
                st.write("Exog data types:")
                st.write(exog.dtypes)
                st.write("Endog data type:")
                st.write(endog.dtype)
                st.write("Endog sample:")
                st.write(endog[:10])

        if show_glm:
            st.subheader('Generalized Linear Model (GLM) Results')
            st.write("GLM with Poisson family, allowing for more complex model specifications.")
            
            try:
                exog = sm.add_constant(pd.get_dummies(df['Latency'], drop_first=True))
                model = sm.GLM(df[f'{selected_column}_diff'], 
                            exog, 
                            family=sm.families.Poisson())
                results = model.fit()
                st.write(results.summary())
                
                st.write("Interpretation: The GLM results provide a more flexible framework for analyzing the data. "
                        "Look at the coefficients, standard errors, and p-values for each latency level. "
                        "Significant p-values (< 0.05) indicate that the corresponding latency level has a measurable effect "
                        "on the input frequency compared to the baseline. The magnitude and direction of the coefficients "
                        "show the strength and direction of these effects.")
            except Exception as e:
                st.error(f"An error occurred during GLM: {str(e)}")

        if show_chi_square:
            st.subheader('Chi-square Goodness-of-fit Test Results')
            st.write("This test compares the observed frequencies to expected frequencies under a Poisson distribution.")
            
            for latency in selected_latencies:
                data = df[df['Latency'] == latency][f'{selected_column}_diff']
                expected = stats.poisson.pmf(np.arange(max(data)+1), data.mean()) * len(data)
                observed = np.bincount(data.astype(int))
                if len(observed) < len(expected):
                    observed = np.pad(observed, (0, len(expected) - len(observed)))
                chi2, p_value = chisquare(observed, expected)
                st.write(f"Latency {latency}ms - Chi-square statistic: {chi2:.4f}, p-value: {p_value:.4f}")
            
            st.write("Interpretation: For each latency level, a small p-value (< 0.05) suggests that the observed data "
                        "doesn't follow a Poisson distribution. This could indicate that the input patterns are more complex "
                        "than a simple Poisson process, possibly due to the influence of latency or other factors. "
                        "If p-values are consistently large across latencies, it suggests that a Poisson distribution "
                        "might be a good fit for modeling the input frequencies.")

        if show_kruskal:
            st.subheader('Kruskal-Wallis Test Results')
            st.write("Non-parametric alternative to one-way ANOVA.")
            
            groups = [group[f'{selected_column}_diff'].values for name, group in df.groupby('Latency')]
            h_statistic, p_value = stats.kruskal(*groups)
            st.write(f"H-statistic: {h_statistic:.4f}")
            st.write(f"p-value: {p_value:.4f}")
            
            st.write("Interpretation: The Kruskal-Wallis test is useful when the data doesn't meet the assumptions of ANOVA. "
                    "A small p-value (< 0.05) suggests that there are significant differences in input frequencies "
                    "across different latency levels, without assuming normality. This would indicate that latency "
                    "has a measurable effect on player input patterns, even if the data is not normally distributed.")

        if show_anderson:
            st.subheader('Anderson-Darling Test Results')
            st.write("This test is often more powerful than the K-S test for detecting differences in distributions.")
            
            groups = [group[f'{selected_column}_diff'].values for name, group in df.groupby('Latency')]
            statistic, critical_values, significance_level = anderson_ksamp(groups)
            st.write(f"Statistic: {statistic:.4f}")
            st.write(f"Critical Values: {critical_values}")
            st.write(f"Significance Level: {significance_level:.4f}")
            
            st.write("Interpretation: The Anderson-Darling test compares the distributions of input frequencies across latency levels. "
                    "A small significance level (< 0.05) indicates that there are significant differences in the distributions. "
                    "This suggests that latency not only affects the average input frequency but also changes the overall "
                    "distribution of inputs, which could indicate changes in player behavior or strategy at different latencies.")

        if show_bootstrap:
            st.subheader('Bootstrap Analysis Results')
            st.write("Bootstrap analysis to estimate confidence intervals for mean event rates.")
            
            n_iterations = 1000
            for latency in selected_latencies:
                data = df[df['Latency'] == latency][f'{selected_column}_diff']
                bootstrap_means = [np.mean(np.random.choice(data, size=len(data), replace=True)) 
                                for _ in range(n_iterations)]
                ci_lower, ci_upper = np.percentile(bootstrap_means, [2.5, 97.5])
                st.write(f"Latency {latency}ms - Mean: {np.mean(data):.4f}, "
                        f"95% CI: ({ci_lower:.4f}, {ci_upper:.4f})")
            
            st.write("Interpretation: The bootstrap analysis provides a robust estimate of the mean input frequency "
                    "and its confidence interval for each latency level. Compare the means and confidence intervals "
                    "across latencies. Non-overlapping confidence intervals suggest significant differences in input "
                    "frequencies between those latency levels. This analysis is particularly useful as it doesn't "
                    "rely on assumptions about the underlying distribution of the data.")

        else:
            st.warning('No data available for the selected players and latencies.')

    else:
        st.warning('Please select at least one player and one latency value.')

else:
    st.error("Cannot proceed with analysis due to data loading error.")