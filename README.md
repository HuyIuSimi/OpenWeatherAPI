# Weather Data Collection Project

A Python application that gets weather data for multiple cities within a region using OpenWeather API.

## What it does
- Gets weather data for cities in a region you specify
- Gets data for multiple cities at once using async programming
- Saves the weather data to a JSON file

## Setup

1. Make sure you have Python installed (3.8 or newer)

2. Install the required packages:
```bash
pip install aiohttp python-dotenv
```

3. Get an OpenWeather API key:
- Go to https://openweathermap.org/
- Create a free account
- Get your API key from the "API keys" tab
- Wait a few hours for the API key to activate

4. Edit a file named `.env` and put your API key in it:
```
OPENWEATHER_API_KEY=your_api_key_here
```

## How to use

1. Run the program:
```bash
python weather_app.py
```

2. Enter the coordinates when asked. For example, for London area:
```
Minimum latitude: 51.4
Maximum latitude: 51.6
Minimum longitude: -0.2
Maximum longitude: 0.0
```

3. The program will:
- Find cities in that area
- Get weather for each city
- Save the results in a file named `weather_data_[timestamp].json`

## Example Output

The program will show:
```
Weather Data Collection System
Found 5 cities. Collecting weather data...
Successfully collected data for 5 cities

City: London
Temperature: 18.5°C
Weather: partly cloudy
```

## Notes
- If you get errors, make sure your API key is correct and activated
- The program might take a few seconds to run depending on how many cities it finds
- If no cities are found, try a larger area by changing the coordinates
