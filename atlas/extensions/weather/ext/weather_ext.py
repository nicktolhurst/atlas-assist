import requests, os, re, json, math, datetime, dateparser
from atlas.extension_router import AtlasExtension

class WeatherExtension(AtlasExtension):
    def __init__(self, logger):
        self.log = logger
        self.base_url = "http://api.openweathermap.org/data/2.5/forecast"
        self.api_key = os.environ.get('WEATHER_EXT__API_KEY')

    def can_handle_input(self, voice_input):
        # This is a simple example, you might want to use more sophisticated NLP techniques
        return 'weather' in voice_input.lower()

    def process_voice_input(self, voice_input):
        # Extract the city name from the voice input
        location, time = self._extract_context(voice_input)
        
        self.log.debug(f"Got location: {location}")
        self.log.debug(f"Got time: {time}")
        
        time = dateparser.parse(time)
        
        self.log.debug(f"Parsed time to datetime: {time}")
        
        hours_from_now = (time - datetime.datetime.now()).total_seconds() / 3600
        
        self.log.debug(f"Got hours from now: {hours_from_now}")
        
        response = self.get_forecast(location, hours_from_now)
        return response

    def get_forecast(self, city, hours_from_now):
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'  # Use 'imperial' for Fahrenheit
        }
        response = requests.get(self.base_url, params=params)
        data = response.json()

        if response.status_code != 200:
            return f"Sorry, I couldn't get the weather for {city}."
        
        # Calculate the nearest 3-hour interval
        nearest_interval = math.ceil(hours_from_now / 3)
        self.log.debug(f"Got nearest interval index as: {nearest_interval} ({nearest_interval * 3} hours from now)")
        if nearest_interval >= len(data['list']):
            return f"Sorry, I couldn't get the weather forecast for {hours_from_now} hours from now."
        
        facts = self._get_weather_facts(data, nearest_interval)        
        
        self.log.debug(f"Got weather data: {json.dumps(facts, indent=4)}")
        return f"Tell the user some of the facts about. \
            Make sure the include the temperature and weather description. \
            Round the numbers to the nearest whole number. \
            Convert the degrees into compass bearing like 'North East'. \
            Don't abbreviate the measurements, km/h should be 'kilometres per hour', \
                hPa should be 'hectoPascals', - should be 'negative', etc. \
            Use the word rain instead of precipitation. \
            Only mention the wind speed if it is greater than 5 km/h or gusts if they are greater than 10km/h \
            Here is the weather data: {facts}"

    def is_in_conversation(self):
        # This extension does not support conversations
        return False
    
    def _extract_context(self, voice_input):
        location_regex = r"in\s([\w\s]+)[\?]"
        time_regex = r"(this evening|tomorrow|at \d+pm|on (monday|tuesday|wednesday|thursday|friday|saturday|sunday)|next week|later today|later|this afternoon|tonight)"

        location_match = re.search(location_regex, voice_input)
        time_match = re.search(time_regex, voice_input)
        
        location = location_match.group(1) if location_match else "Silkstone, UK"
        time = time_match.group(1) if time_match else "now"
        
        return location, time
    
    def _get_weather_facts(self, data, nearest_interval):
        try:
                
            forecast = data['list'][nearest_interval]
            return {
                'temperature': forecast['main']['temp'],
                'weather': forecast['weather'][0]['description'],
                'wind_speed': forecast['wind']['speed'],
                'wind_gust': forecast['wind']['gust'],
                'wind_direction': forecast['wind']['deg'],
                'humidity': forecast['main']['humidity'],
                'cloudiness': forecast['clouds']['all'],
                'rain': forecast['rain']['3h'] if 'rain' in forecast else 0,
                'snow': forecast['snow']['3h'] if 'snow' in forecast else 0
            }
        except Exception as e:
            self.log.error(f"Error getting weather facts: {e}")
            return None
        

            