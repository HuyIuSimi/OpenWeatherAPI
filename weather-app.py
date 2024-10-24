"""
Weather Data Collection Application

This application efficiently retrieves weather data for multiple cities within a specified region
using parallel API calls and optimization strategies.

Core Features:
1. Asynchronous API calls using asyncio and aiohttp
2. Grid-based city search with configurable density
3. Efficient deduplication of cities
4. Retry mechanism for failed requests

"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WeatherDataCollector:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.weather_url = "http://api.openweathermap.org/data/2.5/weather"
        self.geocoding_url = "http://api.openweathermap.org/geo/1.0/reverse"
        self.semaphore = asyncio.Semaphore(10)

    async def collect_weather_data(self, lat_min: float, lat_max: float, 
                                 lon_min: float, lon_max: float) -> list:
        """Main method to collect weather data for all cities in the region."""
        async with aiohttp.ClientSession() as session:
            print("Searching for cities...")
            cities = await self._find_cities(session, lat_min, lat_max, lon_min, lon_max)
            
            if not cities:
                print("No cities found in the specified region.")
                return []

            print(f"Found {len(cities)} cities. Collecting weather data...")
            weather_data = await self._collect_parallel_weather(session, cities)
            
            print(f"Successfully collected data for {len(weather_data)} cities")
            return weather_data

    async def _find_cities(self, session, lat_min, lat_max, lon_min, lon_max) -> list:
        """Find unique cities using a grid-based search pattern."""
        unique_cities = {}
        grid_points = self._generate_grid(lat_min, lat_max, lon_min, lon_max)

        for lat, lon in grid_points:
            params = {
                'lat': lat,
                'lon': lon,
                'limit': 5,
                'appid': self.api_key
            }

            try:
                async with self.semaphore:
                    async with session.get(self.geocoding_url, params=params) as response:
                        response.raise_for_status()
                        locations = await response.json()
                        
                        for loc in locations:
                            if self._is_within_bounds(loc, lat_min, lat_max, lon_min, lon_max):
                                city_key = f"{loc['name'].lower()}_{round(loc['lat'], 3)}"
                                if city_key not in unique_cities:
                                    unique_cities[city_key] = loc

            except Exception as e:
                print(f"Error finding cities at {lat}, {lon}: {e}")

        return list(unique_cities.values())

    def _generate_grid(self, lat_min, lat_max, lon_min, lon_max, density=3) -> list:
        """Generate a grid of points for city search."""
        lat_step = (lat_max - lat_min) / density
        lon_step = (lon_max - lon_min) / density
        
        return [(lat_min + (i * lat_step), lon_min + (j * lon_step))
                for i in range(density + 1)
                for j in range(density + 1)]

    async def _collect_parallel_weather(self, session, cities) -> list:
        """Collect weather data for multiple cities in parallel."""
        tasks = [self._get_weather(session, city) for city in cities]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    async def _get_weather(self, session, city) -> dict:
        """Get weather data for a single city with retry mechanism."""
        params = {
            'lat': city['lat'],
            'lon': city['lon'],
            'appid': self.api_key,
            'units': 'metric'
        }

        async with self.semaphore:
            for attempt in range(3):
                try:
                    async with session.get(self.weather_url, params=params) as response:
                        response.raise_for_status()
                        data = await response.json()
                        data['city_name'] = city['name']
                        return data
                except Exception as e:
                    if attempt == 2:
                        print(f"Failed to get weather for {city['name']}: {e}")
                    await asyncio.sleep(1)
        return None

    def _is_within_bounds(self, location, lat_min, lat_max, lon_min, lon_max) -> bool:
        """Check if location is within the specified bounds."""
        return (lat_min <= location['lat'] <= lat_max and 
                lon_min <= location['lon'] <= lon_max)

    def save_results(self, results: list):
        """Save weather data to a JSON file."""
        if not results:
            return

        filename = f'weather_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        formatted_data = [{
            'city': r['city_name'],
            'coordinates': {
                'latitude': r['coord']['lat'],
                'longitude': r['coord']['lon']
            },
            'temperature': r['main']['temp'],
            'humidity': r['main']['humidity'],
            'weather': r['weather'][0]['description'],
            'wind_speed': r['wind']['speed']
        } for r in results]

        with open(filename, 'w') as f:
            json.dump(formatted_data, f, indent=2)
        print(f"Results saved to {filename}")

async def main():
    try:
        print("\nWeather Data Collection System")
        lat_min = float(input("Minimum latitude: "))
        lat_max = float(input("Maximum latitude: "))
        lon_min = float(input("Minimum longitude: "))
        lon_max = float(input("Maximum longitude: "))

        if lat_min > lat_max or lon_min > lon_max:
            print("Error: Minimum values must be less than maximum values!")
            return

        collector = WeatherDataCollector()
        results = await collector.collect_weather_data(lat_min, lat_max, lon_min, lon_max)
        
        if results:
            print("\nWeather Data Summary:")
            for result in results:
                print(f"\nCity: {result['city_name']}")
                print(f"Temperature: {result['main']['temp']}°C")
                print(f"Weather: {result['weather'][0]['description']}")
            
            collector.save_results(results)

    except ValueError:
        print("Error: Please enter valid numbers for coordinates.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())