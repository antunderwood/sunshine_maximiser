#%%
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
from datetime import datetime

def fetch_weather_data(start_year=2013, end_year=2023, latitude=51.754816, longitude=-1.254367):
    """
    Fetch weather data using the Open-Meteo API.
    """
    weather_data = []
    
    for year in range(start_year, end_year):
        for month in [7, 8,9]:  # July and August
            params = {
                'latitude':     latitude,
                'longitude': longitude,
                'hourly': 'precipitation,weathercode',
                'start_date': datetime(year, month, 1).strftime('%Y-%m-%d'),
                'end_date': datetime(year, month, 28).strftime('%Y-%m-%d') # Assuming all months end on the 28th for simplicity
            }
            response = requests.get("https://archive-api.open-meteo.com/v1/archive", params=params)
            month_data = response.json()  # Hypothetical JSON response
            
            for index, time in enumerate(month_data['hourly']['time']):
                weather_data.append({
                    'date': time,  # Convert this to your local time
                    'precipitation': month_data['hourly']['precipitation'][index]
                })
            
    return pd.DataFrame(weather_data)


def aggregate_by_week(df):
    """
    Aggregate the weather data by week.
    """
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    # Aggregating by week and resetting index
    aggregated_df = df.resample('W').sum().reset_index()
    
    # Adding a 'year' and 'week_of_year' column
    aggregated_df['year'] = aggregated_df['date'].dt.isocalendar().year
    aggregated_df['week_of_year'] = aggregated_df['date'].dt.isocalendar().week
    
    return aggregated_df
    
    return aggregated_df

def filter_weeks(df, start_week=25, end_week=40):
    """
    Filter the DataFrame to only include data for weeks between start_week and end_week.
    """
    return df[(df['week_of_year'] >= start_week) & (df['week_of_year'] <= end_week)]

def plot_precipitation_data(df):
    """
    Plot the aggregated sunshine data using Plotly, with jittered bars.
    """
    # Create an empty figure
    fig = go.Figure()

    # Add bars for each year
    for year in df['year'].unique():
        filtered_df = df[df['year'] == year]
        fig.add_trace(go.Bar(
            x=filtered_df['week_of_year'],
            y=filtered_df['precipitation'],
            name=str(year),
            width=0.1  # Adjust the width as needed
        ))

    # Update layout
    fig.update_layout(
        title='Total Precipitation Hours by Week of the Year',
        xaxis_title='Week of the Year',
        yaxis_title='Total Precipitation Hours',
        barmode='group'  # Bars are placed on top of each other, set to 'group' for side-by-side
    )

    # Show the figure
    fig.show()


def aggregate_by_iso_week(df):
    """
    Aggregate the weather data by ISO week and calculate the mean.
    """
    df['date'] = pd.to_datetime(df['date'])
    df['iso_week'] = df['date'].dt.isocalendar().week
    df['year'] = df['date'].dt.isocalendar().year
    
    # Group by ISO week and year, then calculate the mean precipitation for each week
    aggregated_df = df.groupby(['iso_week', 'year']).agg({'precipitation': 'mean'}).reset_index()
    
    # Calculate the overall mean precipitation for each ISO week
    overall_mean = aggregated_df.groupby('iso_week').agg({'precipitation': 'mean'}).reset_index()
    
    return overall_mean

def find_min_rain_weeks(df, window_size=2):
    """
    Find the starting week of the two consecutive weeks with the least average rain.
    """
    min_rain = float('inf')
    min_week = None
    for week in range(len(df) - window_size + 1):
        rain_sum = df.iloc[week:week + window_size]['precipitation'].sum()
        if rain_sum < min_rain:
            min_rain = rain_sum
            min_week = df.iloc[week]['iso_week']
    return min_week, min_week + window_size - 1

# Main execution flow
if __name__ == "__main__":
    # Step 1: Fetch weather data from Open-Meteo API
    weather_data = fetch_weather_data()
    
    # Step 2: Aggregate the data by week
    aggregated_data = aggregate_by_week(weather_data)
    
    # Step 2.5: Filter the weeks
    filtered_data = filter_weeks(aggregated_data)

    # Step 3: Plot the aggregated data
    plot_precipitation_data(filtered_data)

    # Step 4: Find the two consecutive weeks with the least rain
    weather_data = fetch_weather_data()
    aggregated_data = aggregate_by_iso_week(weather_data)
    
    # Step 4: Filter the aggregated data to only include ISO weeks 25 to 40
    filtered_data = aggregated_data[(aggregated_data['iso_week'] >= 30) & (aggregated_data['iso_week'] <= 40)]
    
    # Step 5: Find the two consecutive weeks with the least average rain
    start_week, end_week = find_min_rain_weeks(filtered_data)
    print(f"The two consecutive ISO weeks with the least average rain are weeks {start_week} and {end_week}.")


# %%
