import json
import requests

def get_weather_json(lat, lon):
    with open('secrets.json', 'r') as f:
        WEATHER_TOKEN = json.loads(f.read())['WEATHER_API_TOKEN']

    weather = requests.get((
        "https://api.openweathermap.org/data/2.5/onecall?"
        f"lat={lat}&lon={lon}"
        "&units=metric&exclude=minutely,hourly,alerts"
        f"&appid={WEATHER_TOKEN}"))

    return json.loads(weather.text)

def parse_weather(w, day):
    frisbee = {
        'Thunderstorm': 'too scary for frisbee.',
        'Drizzle': 'a bit wet for frisbee.',
        'Rain': 'too wet for frisbee.',
        'Fog': 'cant see enough for frisbee.',
        'Snow': 'better wrap up if u wanna frisbee.',
        'Clear': 'perfect for frisbee!',
        'Clouds': 'pretty good for frisbee.'
    }

    if day == 'right now':
        temp = w['temp']
        feels_like = w['feels_like']
    else:
        temp = w['temp']['day']
        feels_like = w['feels_like']['day']

    if (
        w['weather'][0]['main'] in ['Clear', 'Clouds'] and
        feels_like < 10
    ):
        status = 'bit cold, but the weather is ' + frisbee[w['weather'][0]['main']]
    else:
        status = frisbee[w['weather'][0]['main']]

    return (f"{day} there's "
            f"{w['weather'][0]['description']} at "
            f"{temp}°C. "
            f"{status}")

def get_weather(lat, lon, day='current'):
    days = {'today': 0, 'tomorrow': 1}
    weather = get_weather_json(lat, lon)

    if day == 'current':
        return parse_weather(weather['current'], 'right now')
    else:
        if day not in days:
            return 'not a valid day'

        d = days[day]

        return parse_weather(weather['daily'][d], day)
