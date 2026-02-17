import openai
import json


def extract_the_city_and_country(user_query):
    client = openai.OpenAI()

    prompt = (
        f"Extract the city and country from: '{user_query}'. "
        "Return as JSON with 'city' and 'country' keys."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    try:
        return json.loads(response.choices[0].message.content)
    except:
        return None



from geopy.geocoders import Nominatim


def get_coordinates_for_city(city, country):
    geolocator = Nominatim(user_agent="city_coordinate_finder")
    location = geolocator.geocode(f"{city}, {country}")

    if location:
        return location.latitude, location.longitude
    else:
        print(f"Could not find coordinates for '{city}, {country}'.")
        return None, None




import requests


def get_current_weather_open_meteo(latitude, longitude):
    """
    Fetches current weather data from Open-Meteo for a given location.
    """
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,precipitation,"
            "weather_code,wind_speed_10m"
        ),
        "timezone": "auto",  # Automatically determine timezone based on location
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx/5xx)
        weather_data = response.json()
        return weather_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None



import openai


def create_weather_prompt(user_query, weather_data):
    if not weather_data:
        return "No weather data available."

    prompt = (
        "You are a helpful assistant. Based on the weather data below, answer the "
        "user's question in a clear and simple way.\n\n"
        f"User question: {user_query}\n\n"
        f"Weather data (JSON):\n{weather_data}\n"
        "Summarize the weather information so that it is easy for anyone to understand."
    )
    return prompt


def send_prompt_to_llm(prompt):
    client = openai.OpenAI()

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content.strip()


