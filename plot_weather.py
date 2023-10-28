import pandas as pd
import plotly.express as px
import requests

def fetch_weather_data(start_year=2013, end_year=2023):
    """
    Fetch weather data using a Weather API.
    Note: Replace the API endpoint and parameters with those of the actual API you're using.
    """
    weather_data = []
    
    for year in range(start_year, end_year):
        for week in range(27, 36):  # Weeks corresponding to July and August
            response = requests.get(f"https://api.weather.com/v1/location/OXFORD/history/{year}/W/{week}")
            week_data = response.json()  # Hypothetical JSON response
            
            # Aggregate and append the data to our list
            weather_data.append({
                'date': f"{year}-W{week}",
                'sunshine_hours': sum(day['sunshine_hours'] for day in week_data['days']),
            })
            
    return pd.DataFrame(weather_data)

def aggregate_by_week(df):
    """
    Aggregate the weather data by week.
    """
    df['date'] = pd.to_datetime(df['date'] + '-0', format='%Y-W%U-%w')  # Convert to datetime
    df.set_index('date', inplace=True)
    
    return df.resample('W').sum().reset_index()

def plot_sunshine_data(df):
    """
    Plot the aggregated sunshine data using Plotly.
    """
    fig = px.bar(df, x='date', y='sunshine_hours', title='Total Sunshine Hours by Week',
                 labels={'date': 'Week Starting', 'sunshine_hours': 'Total Sunshine Hours'})
    
    fig.show()

# Main execution flow
if __name__ == "__main__":
    # Step 1: Fetch weather data from API
    weather_data = fetch_weather_data()
    
    # Step 2: Aggregate the data by week
    aggregated_data = aggregate_by_week(weather_data)
    
    # Step 3: Plot the aggregated data
    plot_sunshine_data(aggregated_data)
