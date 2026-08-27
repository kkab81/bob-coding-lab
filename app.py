"""
World Time Application - Simple Flask Version
Single file replacement for worldclock.php
Author: Alex Abderrazag IBM UK
Version: 2.0-simple
"""
from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta, timezone
import pytz
from math import cos, sin, acos, pi
import logging
import json
from pathlib import Path
import holidays
import ephem

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Disable Flask request logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# TEMPORARY: Test date override (format: YYYY-MM-DD)
# Set this to test moon phases at different dates
# Example: TEST_DATE_OVERRIDE = "2024-03-25" for waxing gibbous
# Set to None to use current date
TEST_DATE_OVERRIDE = None

WEATHER_CACHE_FILE = Path(__file__).resolve().parent / 'weather_cache.json'
WEATHER_PROGRESS_FILE = Path(__file__).resolve().parent / 'weather_progress.json'
WEATHER_CACHE_MAX_AGE_HOURS = 24

# City coordinates and timezones
CITIES = {
    # Europe
    'London': {'tz': 'Europe/London', 'lat': 51.5074, 'lon': -0.1278},
    'Paris': {'tz': 'Europe/Paris', 'lat': 48.8566, 'lon': 2.3522},
    'Berlin': {'tz': 'Europe/Berlin', 'lat': 52.5200, 'lon': 13.4050},
    'Amsterdam': {'tz': 'Europe/Amsterdam', 'lat': 52.3676, 'lon': 4.9041},
    'Madrid': {'tz': 'Europe/Madrid', 'lat': 40.4168, 'lon': -3.7038},
    'Rome': {'tz': 'Europe/Rome', 'lat': 41.9028, 'lon': 12.4964},
    'Stockholm': {'tz': 'Europe/Stockholm', 'lat': 59.3293, 'lon': 18.0686},
    'Warsaw': {'tz': 'Europe/Warsaw', 'lat': 52.2297, 'lon': 21.0122},
    'Athens': {'tz': 'Europe/Athens', 'lat': 37.9838, 'lon': 23.7275},
    'Istanbul': {'tz': 'Europe/Istanbul', 'lat': 41.0082, 'lon': 28.9784},
    'Moscow': {'tz': 'Europe/Moscow', 'lat': 55.7558, 'lon': 37.6173},
    
    # Middle East
    'Dubai': {'tz': 'Asia/Dubai', 'lat': 25.276987, 'lon': 55.296249},
    'Tel_Aviv': {'tz': 'Asia/Tel_Aviv', 'lat': 32.0853, 'lon': 34.7818},
    'Tehran': {'tz': 'Asia/Tehran', 'lat': 35.6892, 'lon': 51.3890},
    
    # Africa
    'Cairo': {'tz': 'Africa/Cairo', 'lat': 30.0444, 'lon': 31.2357},
    'Johannesburg': {'tz': 'Africa/Johannesburg', 'lat': -26.2041, 'lon': 28.0473},
    'Lagos': {'tz': 'Africa/Lagos', 'lat': 6.5244, 'lon': 3.3792},
    'Nairobi': {'tz': 'Africa/Nairobi', 'lat': -1.2864, 'lon': 36.8172},
    'Cape_Town': {'tz': 'Africa/Johannesburg', 'lat': -33.9249, 'lon': 18.4241},
    
    # Asia
    'Kolkata': {'tz': 'Asia/Kolkata', 'lat': 22.5726, 'lon': 88.3639},
    'Dhaka': {'tz': 'Asia/Dhaka', 'lat': 23.8103, 'lon': 90.4125},
    'Bangkok': {'tz': 'Asia/Bangkok', 'lat': 13.7563, 'lon': 100.5018},
    'Singapore': {'tz': 'Asia/Singapore', 'lat': 1.3521, 'lon': 103.8198},
    'Jakarta': {'tz': 'Asia/Jakarta', 'lat': -6.2088, 'lon': 106.8456},
    'Manila': {'tz': 'Asia/Manila', 'lat': 14.5995, 'lon': 120.9842},
    'Hong_Kong': {'tz': 'Asia/Hong_Kong', 'lat': 22.3193, 'lon': 114.1694},
    'Seoul': {'tz': 'Asia/Seoul', 'lat': 37.5665, 'lon': 126.9780},
    'Tokyo': {'tz': 'Asia/Tokyo', 'lat': 35.6895, 'lon': 139.6917},
    
    # Oceania
    'Perth': {'tz': 'Australia/Perth', 'lat': -31.9505, 'lon': 115.8605},
    'Sydney': {'tz': 'Australia/Sydney', 'lat': -33.8688, 'lon': 151.2093},
    'Melbourne': {'tz': 'Australia/Melbourne', 'lat': -37.8136, 'lon': 144.9631},
    'Auckland': {'tz': 'Pacific/Auckland', 'lat': -36.8485, 'lon': 174.7633},
    'Honolulu': {'tz': 'Pacific/Honolulu', 'lat': 21.3099, 'lon': -157.8581},
    
    # South America
    'Buenos_Aires': {'tz': 'America/Buenos_Aires', 'lat': -34.6037, 'lon': -58.3816},
    'Sao_Paulo': {'tz': 'America/Sao_Paulo', 'lat': -23.5505, 'lon': -46.6333},
    'Santiago': {'tz': 'America/Santiago', 'lat': -33.4489, 'lon': -70.6693},
    'Bogota': {'tz': 'America/Bogota', 'lat': 4.7110, 'lon': -74.0721},
    
    # North America
    'Halifax': {'tz': 'America/Halifax', 'lat': 44.6488, 'lon': -63.5752},
    'New_York': {'tz': 'America/New_York', 'lat': 40.7128, 'lon': -74.0060},
    'Miami': {'tz': 'America/New_York', 'lat': 25.7617, 'lon': -80.1918},
    'Toronto': {'tz': 'America/Toronto', 'lat': 43.651070, 'lon': -79.347015},
    'Chicago': {'tz': 'America/Chicago', 'lat': 41.8781, 'lon': -87.6298},
    'Mexico_City': {'tz': 'America/Mexico_City', 'lat': 19.4326, 'lon': -99.1332},
    'Denver': {'tz': 'America/Denver', 'lat': 39.7392, 'lon': -104.9903},
    'Los_Angeles': {'tz': 'America/Los_Angeles', 'lat': 34.0522, 'lon': -118.2437},
    'San_Francisco': {'tz': 'America/Los_Angeles', 'lat': 37.7749, 'lon': -122.4194},
    'Vancouver': {'tz': 'America/Vancouver', 'lat': 49.2827, 'lon': -123.1207},
    'Anchorage': {'tz': 'America/Anchorage', 'lat': 61.2181, 'lon': -149.9003}
}

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
}

# Map cities to country codes for holidays library
CITY_TO_COUNTRY = {
    # Europe
    'London': 'GB', 'Paris': 'FR', 'Berlin': 'DE', 'Amsterdam': 'NL',
    'Madrid': 'ES', 'Rome': 'IT', 'Stockholm': 'SE', 'Warsaw': 'PL',
    'Athens': 'GR', 'Istanbul': 'TR', 'Moscow': 'RU',
    # Middle East
    'Dubai': 'AE', 'Tel_Aviv': 'IL', 'Tehran': 'IR',
    # Africa
    'Cairo': 'EG', 'Johannesburg': 'ZA', 'Lagos': 'NG', 'Nairobi': 'KE', 'Cape_Town': 'ZA',
    # Asia
    'Kolkata': 'IN', 'Dhaka': 'BD', 'Bangkok': 'TH', 'Singapore': 'SG',
    'Jakarta': 'ID', 'Manila': 'PH', 'Hong_Kong': 'HK', 'Seoul': 'KR', 'Tokyo': 'JP',
    # Oceania
    'Perth': 'AU', 'Sydney': 'AU', 'Melbourne': 'AU', 'Auckland': 'NZ', 'Honolulu': 'US',
    # South America
    'Buenos_Aires': 'AR', 'Sao_Paulo': 'BR', 'Santiago': 'CL', 'Bogota': 'CO',
    # North America
    'Halifax': 'CA', 'New_York': 'US', 'Miami': 'US', 'Toronto': 'CA',
    'Chicago': 'US', 'Mexico_City': 'MX', 'Denver': 'US', 'Los_Angeles': 'US',
    'San_Francisco': 'US', 'Vancouver': 'CA', 'Anchorage': 'US'
}

# Map cities to subdivisions (states/provinces) for more accurate holidays
CITY_TO_SUBDIVISION = {
    'London': 'ENG',  # England subdivision for UK to get all bank holidays
}

def load_weather_cache():
    """Load weather cache file written by weather.py"""
    if not WEATHER_CACHE_FILE.exists():
        return None

    try:
        with WEATHER_CACHE_FILE.open('r', encoding='utf-8') as cache_file:
            return json.load(cache_file)
    except Exception as exc:
        print(f"⚠️  Failed to read weather cache: {exc}")
        return None


def parse_cache_timestamp(value):
    """Parse ISO timestamp from cache metadata"""
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None


def get_weather_cache_status():
    """Return cache metadata and staleness information"""
    cache_data = load_weather_cache()

    if not cache_data:
        return {
            'available': False,
            'stale': True,
            'warning': 'Weather cache is missing. Run python3 weather.py to refresh weather data.',
            'cache': None
        }

    generated_at = parse_cache_timestamp(cache_data.get('generated_at'))
    if not generated_at:
        return {
            'available': True,
            'stale': True,
            'warning': 'Weather cache timestamp is invalid. Run python3 weather.py to refresh weather data.',
            'cache': cache_data
        }

    age = datetime.now(timezone.utc) - generated_at.astimezone(timezone.utc)
    stale = age > timedelta(hours=WEATHER_CACHE_MAX_AGE_HOURS)

    warning = None
    if stale:
        generated_local = generated_at.astimezone()
        warning = (
            f"Weather cache is older than {WEATHER_CACHE_MAX_AGE_HOURS} hours "
            f"(last updated {generated_local.strftime('%Y-%m-%d %H:%M:%S %Z')}). "
            f"Run python3 weather.py to refresh it."
        )

    return {
        'available': True,
        'stale': stale,
        'warning': warning,
        'cache': cache_data
    }


def get_weather(cache_data, city_name):
    """Get current weather for a city from persisted cache"""
    if not cache_data:
        return None
    return cache_data.get('cities', {}).get(city_name, {}).get('current')


def get_forecast(cache_data, city_name):
    """Get forecast for a city from persisted cache"""
    if not cache_data:
        return None
    return cache_data.get('cities', {}).get(city_name, {}).get('forecast')

def get_wind_direction(degree):
    """Convert degrees to cardinal direction"""
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    return directions[round(degree / 45) % 8]

def get_aqi_info(aqi_value):
    """
    Get AQI category, color, and health message based on US AQI value.
    Returns dict with category, color, and message.
    """
    if aqi_value is None:
        return {
            'category': 'Unknown',
            'color': '#999999',
            'message': 'Air quality data unavailable'
        }
    
    aqi = int(aqi_value)
    
    if aqi <= 50:
        return {
            'category': 'Good',
            'color': '#00e400',
            'message': 'Air quality is satisfactory'
        }
    elif aqi <= 100:
        return {
            'category': 'Moderate',
            'color': '#ffff00',
            'message': 'Acceptable for most people'
        }
    elif aqi <= 150:
        return {
            'category': 'Unhealthy for Sensitive Groups',
            'color': '#ff7e00',
            'message': 'Sensitive groups may experience health effects'
        }
    elif aqi <= 200:
        return {
            'category': 'Unhealthy',
            'color': '#ff0000',
            'message': 'Everyone may begin to experience health effects'
        }
    elif aqi <= 300:
        return {
            'category': 'Very Unhealthy',
            'color': '#8f3f97',
            'message': 'Health alert: everyone may experience serious effects'
        }
    else:
        return {
            'category': 'Hazardous',
            'color': '#7e0023',
            'message': 'Health warning of emergency conditions'
        }
def get_moon_phase(dt):
    """Calculate moon phase from date - returns phase value, name, and illumination percentage"""
    # Convert dt to UTC for ephem
    if dt.tzinfo is None:
        dt_utc = pytz.UTC.localize(dt)
    else:
        dt_utc = dt.astimezone(pytz.UTC)
    
    # Use ephem library for accurate astronomical calculations
    moon = ephem.Moon(dt_utc)
    
    # Get illumination percentage (moon_phase returns 0.0-1.0)
    illumination = moon.moon_phase * 100
    
    # Calculate phase for phase name determination
    # ephem doesn't directly give us phase angle, so we calculate it
    # New moon is when moon and sun have same ecliptic longitude
    sun = ephem.Sun(dt_utc)
    phase_angle = (moon.ra - sun.ra) % (2 * pi)
    phase = phase_angle / (2 * pi)
    
    # Determine phase name
    # New moon occurs at phase ~0 or ~1 (wraps around)
    if phase < 0.0625 or phase >= 0.9375:
        phase_name = "New Moon"
    elif phase < 0.1875:
        phase_name = "Waxing Crescent"
    elif phase < 0.3125:
        phase_name = "First Quarter"
    elif phase < 0.4375:
        phase_name = "Waxing Gibbous"
    elif phase < 0.5625:
        phase_name = "Full Moon"
    elif phase < 0.6875:
        phase_name = "Waning Gibbous"
    elif phase < 0.8125:
        phase_name = "Last Quarter"
    else:
        phase_name = "Waning Crescent"
    
    # Return phase value (0-1), name, and illumination percentage
    return phase_name, phase, int(illumination)

def get_moon_details(dt, lat, lon, tz):
    """Get comprehensive moon data for a specific location and time"""
    # Create observer
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    
    # Convert dt to UTC for ephem
    if dt.tzinfo is None:
        dt_utc = pytz.UTC.localize(dt)
    else:
        dt_utc = dt.astimezone(pytz.UTC)
    
    observer.date = dt_utc
    
    # Calculate moon position
    moon = ephem.Moon(observer)
    
    # Distance (convert from AU to km)
    distance_km = moon.earth_distance * ephem.meters_per_au / 1000
    
    # Direction (Azimuth) - 0° = North, 90° = East, 180° = South, 270° = West
    azimuth = float(moon.az) * 180 / pi
    
    # Altitude (Elevation above horizon)
    altitude = float(moon.alt) * 180 / pi
    
    # Determine direction label
    if azimuth < 22.5 or azimuth >= 337.5:
        direction_label = "N"
    elif azimuth < 67.5:
        direction_label = "NE"
    elif azimuth < 112.5:
        direction_label = "E"
    elif azimuth < 157.5:
        direction_label = "SE"
    elif azimuth < 202.5:
        direction_label = "S"
    elif azimuth < 247.5:
        direction_label = "SW"
    elif azimuth < 292.5:
        direction_label = "W"
    else:
        direction_label = "NW"
    
    # Add up/down indicator based on altitude
    if altitude > 0:
        direction_label += "↑"
    else:
        direction_label += "↓"
    
    # Moonrise/Moonset
    try:
        # Find next moonrise
        observer.date = dt_utc
        next_rising = observer.next_rising(ephem.Moon())
        moonrise_dt = ephem.Date(next_rising).datetime()
        moonrise_dt = pytz.UTC.localize(moonrise_dt).astimezone(tz)
        moonrise_str = moonrise_dt.strftime('%H:%M')
        
        # Determine if moonrise is today or tomorrow
        if moonrise_dt.date() == dt.date():
            moonrise_label = "Today, " + moonrise_str
        elif moonrise_dt.date() == (dt + timedelta(days=1)).date():
            moonrise_label = "Tomorrow, " + moonrise_str
        else:
            moonrise_label = moonrise_dt.strftime('%b %d, %H:%M')
        
        # Find next moonset
        observer.date = dt_utc
        next_setting = observer.next_setting(ephem.Moon())
        moonset_dt = ephem.Date(next_setting).datetime()
        moonset_dt = pytz.UTC.localize(moonset_dt).astimezone(tz)
        moonset_str = moonset_dt.strftime('%H:%M')
        
        # Determine if moonset is today or tomorrow
        if moonset_dt.date() == dt.date():
            moonset_label = "Today, " + moonset_str
        elif moonset_dt.date() == (dt + timedelta(days=1)).date():
            moonset_label = "Tomorrow, " + moonset_str
        else:
            moonset_label = moonset_dt.strftime('%b %d, %H:%M')
            
    except (ephem.AlwaysUpError, ephem.NeverUpError):
        moonrise_label = "N/A"
        moonset_label = "N/A"
    
    # Astronomical constellation (actual star positions)
    astronomical_constellation = ephem.constellation(moon)[1]
    
    # Astrological zodiac sign (tropical zodiac - what most people expect)
    # Convert ecliptic longitude to degrees
    ecl_lon = float(moon.hlon) * 180 / pi
    
    # Determine tropical zodiac sign based on ecliptic longitude
    if ecl_lon < 30:
        zodiac_sign = "Aries"
    elif ecl_lon < 60:
        zodiac_sign = "Taurus"
    elif ecl_lon < 90:
        zodiac_sign = "Gemini"
    elif ecl_lon < 120:
        zodiac_sign = "Cancer"
    elif ecl_lon < 150:
        zodiac_sign = "Leo"
    elif ecl_lon < 180:
        zodiac_sign = "Virgo"
    elif ecl_lon < 210:
        zodiac_sign = "Libra"
    elif ecl_lon < 240:
        zodiac_sign = "Scorpio"
    elif ecl_lon < 270:
        zodiac_sign = "Sagittarius"
    elif ecl_lon < 300:
        zodiac_sign = "Capricorn"
    elif ecl_lon < 330:
        zodiac_sign = "Aquarius"
    else:
        zodiac_sign = "Pisces"
    
    # Calculate distance in miles (1 km = 0.621371 miles)
    distance_miles = distance_km * 0.621371
    
    return {
        'distance_km': int(round(distance_km, 0)),
        'distance_miles': int(round(distance_miles, 0)),
        'azimuth': round(azimuth, 2),
        'altitude': round(altitude, 2),
        'direction_label': direction_label,
        'moonrise': moonrise_label,
        'moonset': moonset_label,
        'zodiac_sign': zodiac_sign,
        'astronomical_constellation': astronomical_constellation
    }

def get_full_moons_for_year(year=None, start_date=None):
    """Calculate all full moon dates for a given calendar year"""
    if year is None:
        year = datetime.now().year
    
    # Start from January 1st of the year
    year_start = datetime(year, 1, 1, tzinfo=pytz.UTC)
    year_end = datetime(year, 12, 31, 23, 59, 59, tzinfo=pytz.UTC)
    
    # If start_date is provided and it's in the same year, use it
    if start_date:
        if start_date.tzinfo is None:
            start_date = pytz.UTC.localize(start_date)
        else:
            start_date = start_date.astimezone(pytz.UTC)
        
        if start_date.year == year:
            current_date = start_date
        else:
            current_date = year_start
    else:
        current_date = year_start
    
    full_moons = []
    
    # Find all full moons in the year
    while True:
        # Use ephem to find the next full moon
        next_full = ephem.next_full_moon(current_date)
        
        # Convert ephem date to Python datetime
        full_moon_dt = ephem.Date(next_full).datetime()
        full_moon_dt = pytz.UTC.localize(full_moon_dt)
        
        # Stop if we've gone past the end of the year
        if full_moon_dt > year_end:
            break
        
        full_moons.append({
            'datetime': full_moon_dt.isoformat(),
            'date': full_moon_dt.strftime('%Y-%m-%d'),
            'time_utc': full_moon_dt.strftime('%H:%M:%S'),
            'timestamp': int(full_moon_dt.timestamp())
        })
        
        # Move to the day after this full moon to find the next one
        current_date = full_moon_dt + timedelta(days=1)
    
    return full_moons

def get_new_moons_for_year(year=None, start_date=None):
    """Calculate all new moon dates for a given calendar year"""
    if year is None:
        year = datetime.now().year
    
    # Start from January 1st of the year
    year_start = datetime(year, 1, 1, tzinfo=pytz.UTC)
    year_end = datetime(year, 12, 31, 23, 59, 59, tzinfo=pytz.UTC)
    
    # If start_date is provided and it's in the same year, use it
    if start_date:
        if start_date.tzinfo is None:
            start_date = pytz.UTC.localize(start_date)
        else:
            start_date = start_date.astimezone(pytz.UTC)
        
        if start_date.year == year:
            current_date = start_date
        else:
            current_date = year_start
    else:
        current_date = year_start
    
    new_moons = []
    
    # Find all new moons in the year
    while True:
        # Use ephem to find the next new moon
        next_new = ephem.next_new_moon(current_date)
        
        # Convert ephem date to Python datetime
        new_moon_dt = ephem.Date(next_new).datetime()
        new_moon_dt = pytz.UTC.localize(new_moon_dt)
        
        # Stop if we've gone past the end of the year
        if new_moon_dt > year_end:
            break
        
        new_moons.append({
            'datetime': new_moon_dt.isoformat(),
            'date': new_moon_dt.strftime('%Y-%m-%d'),
            'time_utc': new_moon_dt.strftime('%H:%M:%S'),
            'timestamp': int(new_moon_dt.timestamp())
        })
        
        # Move to the day after this new moon to find the next one
        current_date = new_moon_dt + timedelta(days=1)
    
    return new_moons


def get_solar_events_for_year(year=None, lat=None, lon=None, tz=None):
    """Calculate solstices and equinoxes for a given year with sunrise/sunset times"""
    if year is None:
        year = datetime.now().year
    
    # Default to London if no location provided
    if lat is None or lon is None or tz is None:
        lat, lon = 51.5074, -0.1278
        tz = pytz.timezone('Europe/London')
    
    # Calculate the four key solar events using ephem
    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.lon = str(lon)
    observer.date = f'{year}/1/1'
    
    solar_events = []
    
    # Spring Equinox (Vernal Equinox) - around March 20
    spring_equinox = ephem.next_vernal_equinox(f'{year}/1/1')
    spring_dt = ephem.Date(spring_equinox).datetime()
    spring_dt = pytz.UTC.localize(spring_dt).astimezone(tz)
    
    # Summer Solstice - around June 21
    summer_solstice = ephem.next_summer_solstice(f'{year}/1/1')
    summer_dt = ephem.Date(summer_solstice).datetime()
    summer_dt = pytz.UTC.localize(summer_dt).astimezone(tz)
    
    # Autumn Equinox (Autumnal Equinox) - around September 22
    autumn_equinox = ephem.next_autumn_equinox(f'{year}/1/1')
    autumn_dt = ephem.Date(autumn_equinox).datetime()
    autumn_dt = pytz.UTC.localize(autumn_dt).astimezone(tz)
    
    # Winter Solstice - around December 21
    winter_solstice = ephem.next_winter_solstice(f'{year}/1/1')
    winter_dt = ephem.Date(winter_solstice).datetime()
    winter_dt = pytz.UTC.localize(winter_dt).astimezone(tz)
    
    # Calculate sunrise/sunset for each event
    events = [
        ('Spring Equinox', spring_dt, 'Equal day and night'),
        ('Summer Solstice', summer_dt, 'Longest day of the year'),
        ('Autumn Equinox', autumn_dt, 'Equal day and night'),
        ('Winter Solstice', winter_dt, 'Shortest day of the year')
    ]
    
    for event_name, event_dt, description in events:
        # Calculate sunrise and sunset for this date
        observer.date = event_dt.astimezone(pytz.UTC)
        
        try:
            sunrise = observer.next_rising(ephem.Sun())
            sunset = observer.next_setting(ephem.Sun())
            
            sunrise_dt = ephem.Date(sunrise).datetime()
            sunrise_dt = pytz.UTC.localize(sunrise_dt).astimezone(tz)
            
            sunset_dt = ephem.Date(sunset).datetime()
            sunset_dt = pytz.UTC.localize(sunset_dt).astimezone(tz)
            
            # Calculate daylight duration
            daylight_seconds = (sunset_dt - sunrise_dt).total_seconds()
            daylight_hours = int(daylight_seconds // 3600)
            daylight_minutes = int((daylight_seconds % 3600) // 60)
            
            solar_events.append({
                'name': event_name,
                'datetime': event_dt.isoformat(),
                'date': event_dt.strftime('%Y-%m-%d'),
                'time': event_dt.strftime('%H:%M:%S'),
                'day_name': event_dt.strftime('%A'),
                'month': event_dt.strftime('%B'),
                'formatted_date': event_dt.strftime('%A, %B %d, %Y'),
                'sunrise': sunrise_dt.strftime('%H:%M'),
                'sunset': sunset_dt.strftime('%H:%M'),
                'daylight_hours': daylight_hours,
                'daylight_minutes': daylight_minutes,
                'daylight_duration': f'{daylight_hours}h {daylight_minutes}m',
                'description': description,
                'timestamp': int(event_dt.timestamp())
            })
        except (ephem.AlwaysUpError, ephem.NeverUpError):
            # Handle polar regions where sun may not rise/set
            solar_events.append({
                'name': event_name,
                'datetime': event_dt.isoformat(),
                'date': event_dt.strftime('%Y-%m-%d'),
                'time': event_dt.strftime('%H:%M:%S'),
                'day_name': event_dt.strftime('%A'),
                'month': event_dt.strftime('%B'),
                'formatted_date': event_dt.strftime('%A, %B %d, %Y'),
                'sunrise': 'N/A',
                'sunset': 'N/A',
                'daylight_hours': 0,
                'daylight_minutes': 0,
                'daylight_duration': 'N/A',
                'description': description,
                'timestamp': int(event_dt.timestamp())
            })
    
    return solar_events


def calculate_sun_times(lat, lon, dt, tz):
    """Calculate sunrise/sunset times in local timezone"""
    try:
        # Get the date in UTC for calculation
        if dt.tzinfo is None:
            dt_utc = pytz.UTC.localize(dt)
        else:
            dt_utc = dt.astimezone(pytz.UTC)
        
        day_of_year = dt_utc.timetuple().tm_yday
        declination = 23.45 * sin(2 * pi * (284 + day_of_year) / 365)
        lat_rad = lat * pi / 180
        decl_rad = declination * pi / 180
        cos_hour = -sin(lat_rad) * sin(decl_rad) / (cos(lat_rad) * cos(decl_rad))
        
        if cos_hour > 1:
            return 'No sunrise', 'No sunset'
        elif cos_hour < -1:
            return '24h daylight', '24h daylight'
        
        hour_angle = acos(cos_hour) * 180 / pi
        sunrise_utc_hours = 12 - hour_angle / 15 - lon / 15
        sunset_utc_hours = 12 + hour_angle / 15 - lon / 15
        
        # Create UTC datetime objects for sunrise/sunset
        sunrise_utc = dt_utc.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=sunrise_utc_hours)
        sunset_utc = dt_utc.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=sunset_utc_hours)
        
        # Convert to local timezone
        sunrise_local = sunrise_utc.astimezone(tz)
        sunset_local = sunset_utc.astimezone(tz)
        
        return sunrise_local.strftime('%H:%M'), sunset_local.strftime('%H:%M')
    except Exception as e:
        return 'Unknown', 'Unknown'

@app.route('/')
def index():
    """Main page with integrated settings modal"""
    cache_status = get_weather_cache_status()
    return render_template('index.html', weather_cache_warning=cache_status['warning'])

@app.route('/api/worldclock')
def worldclock():
    """API endpoint - returns timezone data (replaces worldclock.php)"""
    home_city = request.args.get('home', 'London')
    # Support both integer and decimal (float) time offsets for minute precision
    time_offset_str = request.args.get('tm', '0')
    try:
        time_offset = float(time_offset_str)
    except (ValueError, TypeError):
        time_offset = 0
    
    cache_status = get_weather_cache_status()
    cache_data = cache_status['cache']

    # Get home timezone
    home_tz = pytz.timezone(CITIES.get(home_city, CITIES['London'])['tz'])
    
    # TEMPORARY: Use test date if set, otherwise use current time
    if TEST_DATE_OVERRIDE:
        try:
            test_date = datetime.strptime(TEST_DATE_OVERRIDE, '%Y-%m-%d')
            home_time = home_tz.localize(test_date.replace(hour=12, minute=0))
        except:
            home_time = datetime.now(home_tz)
    else:
        home_time = datetime.now(home_tz)
    
    if time_offset:
        home_time += timedelta(hours=time_offset)
    
    times = {}
    
    for city, info in CITIES.items():
        tz = pytz.timezone(info['tz'])
        
        # TEMPORARY: Use test date if set, otherwise use current time
        if TEST_DATE_OVERRIDE:
            try:
                test_date = datetime.strptime(TEST_DATE_OVERRIDE, '%Y-%m-%d')
                current_time = tz.localize(test_date.replace(hour=12, minute=0))
            except:
                current_time = datetime.now(tz)
        else:
            current_time = datetime.now(tz)
        
        if time_offset:
            current_time += timedelta(hours=time_offset)
        
        # Calculate offset from home
        current_offset = current_time.utcoffset() or timedelta(0)
        home_offset = home_time.utcoffset() or timedelta(0)
        offset_seconds = current_offset.total_seconds() - home_offset.total_seconds()
        offset_hours = int(offset_seconds / 3600)
        offset_str = f"{'+' if offset_hours >= 0 else ''}{offset_hours:02d} hrs"
        
        # Get sun times
        sunrise, sunset = calculate_sun_times(info['lat'], info['lon'], current_time, tz)
        
        # Get weather from persisted weather.py cache
        weather = get_weather(cache_data, city)
        
        # Get moon phase (returns name, phase value 0-1, and illumination %)
        moon_phase_name, moon_phase_value, moon_illumination = get_moon_phase(current_time)
        
        times[city] = {
            'weather_cache_warning': cache_status['warning'] if city == home_city else None,
            'date': current_time.strftime('%a %d %B %Y'),
            'time24': current_time.strftime('%H:%M'),
            'time': f"{((current_time.hour - 1) % 12) + 1}:{current_time.strftime('%M')}",
            'ampm': current_time.strftime('%p').lower(),
            'secs': current_time.strftime('%S'),
            'timezone_abbr': current_time.strftime('%Z'),
            'offset': offset_str,
            'weekno': current_time.strftime('%W'),
            'dayno': current_time.strftime('%j'),
            'dst': 'Yes' if current_time.dst() else 'No',
            'sunrise': sunrise,
            'sunset': sunset,
            'epoch': int(current_time.timestamp()),
            'temperature': weather['temperature'] if weather else None,
            'conditions': weather['conditions'] if weather else None,
            'minmax': weather['minmax'] if weather else None,
            'wind': weather['wind'] if weather else None,
            'rain': weather['rain'] if weather else None,
            'moon_phase': moon_phase_name,
            'moon_phase_value': moon_phase_value,
            'moon_illumination': moon_illumination
        }
    
    return jsonify(times)

@app.route('/api/forecast')
def forecast():
    """API endpoint - returns 5-day weather forecast for a city"""
    city = request.args.get('city', 'London')
    
    if city not in CITIES:
        return jsonify({'error': 'City not found'}), 404
    
    cache_status = get_weather_cache_status()
    forecast_days = get_forecast(cache_status['cache'], city)

    if forecast_days is None:
        return jsonify({'error': 'Forecast not available in cache. Run python3 weather.py to refresh weather data.'}), 503

    # Get current weather (which includes AQI)
    current_weather = get_weather(cache_status['cache'], city)
    aqi_data = current_weather.get('aqi') if current_weather else None
    
    # Process AQI info if available
    aqi_info = None
    if aqi_data and aqi_data.get('us_aqi') is not None:
        aqi_details = get_aqi_info(aqi_data['us_aqi'])
        aqi_info = {
            'value': aqi_data['us_aqi'],
            'pm10': aqi_data.get('pm10'),
            'pm2_5': aqi_data.get('pm2_5'),
            'category': aqi_details['category'],
            'color': aqi_details['color'],
            'message': aqi_details['message']
        }

    # Include cache metadata in response
    cache_data = cache_status['cache']
    generated_at = None
    if cache_data:
        generated_at = parse_cache_timestamp(cache_data.get('generated_at'))
    
    return jsonify({
        'city': city,
        'forecast': forecast_days,
        'aqi': aqi_info,
        'weather_cache_warning': cache_status['warning'],
        'cache_generated_at': generated_at.isoformat() if generated_at else None
    })

@app.route('/api/weather-cache-info')
def weather_cache_info():
    """API endpoint - returns weather cache metadata"""
    cache_status = get_weather_cache_status()
    cache_data = cache_status['cache']
    
    if not cache_data:
        return jsonify({
            'available': False,
            'error': 'Cache not available'
        }), 404
    
    generated_at = parse_cache_timestamp(cache_data.get('generated_at'))
    
    return jsonify({
        'available': True,
        'generated_at': generated_at.isoformat() if generated_at else None,
        'request_count': cache_data.get('request_count', 0),
        'success_count': cache_data.get('success_count', 0),
        'failure_count': cache_data.get('failure_count', 0),
        'cache_valid_hours': cache_data.get('cache_valid_hours', WEATHER_CACHE_MAX_AGE_HOURS),
        'stale': cache_status['stale'],
        'warning': cache_status['warning']
    })

@app.route('/api/weather-progress')
def weather_progress():
    """API endpoint - returns current weather refresh progress"""
    if not WEATHER_PROGRESS_FILE.exists():
        return jsonify({
            'status': 'idle',
            'message': 'No refresh in progress'
        })
    
    try:
        with WEATHER_PROGRESS_FILE.open('r', encoding='utf-8') as f:
            progress_data = json.load(f)
        return jsonify(progress_data)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to read progress: {str(e)}'
        }), 500

@app.route('/api/refresh-weather', methods=['POST'])
def refresh_weather():
    """API endpoint - manually refresh weather data with rate limiting"""
    import subprocess
    import sys
    
    # Clear any existing progress file
    if WEATHER_PROGRESS_FILE.exists():
        try:
            WEATHER_PROGRESS_FILE.unlink()
        except:
            pass
    
    # Check if cache exists and is recent enough (less than 2 hours old)
    cache_status = get_weather_cache_status()
    
    if cache_status['available']:
        cache_data = cache_status['cache']
        generated_at = parse_cache_timestamp(cache_data.get('generated_at'))
        
        if generated_at:
            age = datetime.now(timezone.utc) - generated_at.astimezone(timezone.utc)
            min_refresh_hours = 2
            
            if age < timedelta(hours=min_refresh_hours):
                hours_remaining = min_refresh_hours - (age.total_seconds() / 3600)
                minutes_remaining = int(hours_remaining * 60)
                
                return jsonify({
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'message': f'Weather data was updated {int(age.total_seconds() / 60)} minutes ago. Please wait {minutes_remaining} more minutes before refreshing again.',
                    'last_updated': generated_at.isoformat(),
                    'next_allowed_refresh': (generated_at + timedelta(hours=min_refresh_hours)).isoformat()
                }), 429
    
    # Run weather.py script
    try:
        result = subprocess.run(
            [sys.executable, 'weather.py'],
            cwd=Path(__file__).resolve().parent,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            # Reload cache to get new data
            new_cache_status = get_weather_cache_status()
            new_cache_data = new_cache_status['cache']
            
            if new_cache_data:
                generated_at = parse_cache_timestamp(new_cache_data.get('generated_at'))
                
                return jsonify({
                    'success': True,
                    'message': 'Weather data refreshed successfully',
                    'last_updated': generated_at.isoformat() if generated_at else None,
                    'request_count': new_cache_data.get('request_count', 0),
                    'success_count': new_cache_data.get('success_count', 0),
                    'failure_count': new_cache_data.get('failure_count', 0)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Cache update failed',
                    'message': 'Weather script ran but cache file could not be read'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'Script execution failed',
                'message': f'Weather script failed with return code {result.returncode}',
                'stderr': result.stderr[:500] if result.stderr else None
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Timeout',
            'message': 'Weather refresh took too long and was cancelled'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Unexpected error',
            'message': str(e)
        }), 500

@app.route('/api/holidays')
def get_holidays():
    """API endpoint - returns public holidays for a city"""
    city = request.args.get('city', 'London')
    year = int(request.args.get('year', datetime.now().year))
    
    if city not in CITIES:
        return jsonify({'error': 'City not found'}), 404
    
    if city not in CITY_TO_COUNTRY:
        return jsonify({'error': 'Country code not available for this city'}), 404
    
    country_code = CITY_TO_COUNTRY[city]
    
    try:
        # Get holidays for the country (with subdivision if available)
        subdiv = CITY_TO_SUBDIVISION.get(city)
        if subdiv:
            country_holidays = holidays.country_holidays(country_code, subdiv=subdiv, years=year)
        else:
            country_holidays = holidays.country_holidays(country_code, years=year)
        
        # Convert to list of dicts with date and name
        holiday_list = []
        for date, name in sorted(country_holidays.items()):
            # Get timezone for the city
            tz = pytz.timezone(CITIES[city]['tz'])
            local_date = tz.localize(datetime.combine(date, datetime.min.time()))
            
            holiday_list.append({
                'date': date.isoformat(),
                'name': name,
                'day_of_week': local_date.strftime('%A'),
                'formatted_date': local_date.strftime('%B %d, %Y')
            })
        
        # Filter to show upcoming holidays (from today onwards)
        today = datetime.now().date()
        upcoming_holidays = [h for h in holiday_list if datetime.fromisoformat(h['date']).date() >= today]
        
        return jsonify({
            'city': city,
            'country_code': country_code,
            'year': year,
            'total_holidays': len(holiday_list),
            'upcoming_holidays': upcoming_holidays[:10],  # Next 10 holidays
            'all_holidays': holiday_list
        })
    except Exception as e:
        return jsonify({'error': f'Failed to fetch holidays: {str(e)}'}), 500

@app.route('/api/dst-transitions')
def dst_transitions():
    """API endpoint - returns DST transition dates for a city in a given year"""
    city = request.args.get('city', 'London')
    year = int(request.args.get('year', datetime.now().year))
    
    if city not in CITIES:
        return jsonify({'error': 'City not found'}), 404
    
    city_info = CITIES[city]
    tz = pytz.timezone(city_info['tz'])
    
    # Find DST transitions by checking each day of the year
    transitions = []
    start_date = datetime(year, 1, 1)
    
    try:
        prev_dst = None
        for day in range(366):  # Check all days including leap year
            try:
                current_date = start_date + timedelta(days=day)
                if current_date.year != year:  # Stop if we've moved to next year
                    break
                    
                # Localize to the timezone at noon to avoid ambiguous times
                current = tz.localize(current_date.replace(hour=12, minute=0, second=0))
                current_dst = current.dst()
                
                # Detect transition
                if prev_dst is not None and current_dst != prev_dst:
                    # DST transition occurred
                    transition_type = 'start' if current_dst else 'end'
                    # Calculate offset change safely
                    if current_dst and prev_dst:
                        offset_change = current_dst - prev_dst if transition_type == 'start' else prev_dst - current_dst
                    else:
                        offset_change = current_dst if current_dst else prev_dst
                    
                    # Find the exact hour of transition
                    transition_date = start_date + timedelta(days=day)
                    for hour in range(24):
                        try:
                            test_time = tz.localize(transition_date.replace(hour=hour, minute=0, second=0))
                            if (transition_type == 'start' and test_time.dst()) or \
                               (transition_type == 'end' and not test_time.dst()):
                                transition_datetime = test_time
                                break
                        except:
                            continue
                    else:
                        transition_datetime = current
                    
                    transitions.append({
                        'date': transition_datetime.strftime('%Y-%m-%d'),
                        'time': transition_datetime.strftime('%H:%M'),
                        'datetime': transition_datetime.strftime('%A, %B %d, %Y at %H:%M'),
                        'type': transition_type,
                        'description': 'Clocks spring forward' if transition_type == 'start' else 'Clocks fall back',
                        'offset_change_hours': int(offset_change.total_seconds() / 3600),
                        'timezone_abbr_before': tz.localize(transition_date - timedelta(days=1)).strftime('%Z'),
                        'timezone_abbr_after': transition_datetime.strftime('%Z')
                    })
                
                prev_dst = current_dst
            except:
                continue
        
        return jsonify({
            'city': city,
            'year': year,
            'timezone': city_info['tz'],
            'has_dst': len(transitions) > 0,
            'transitions': transitions
        })
    except Exception as e:
        return jsonify({'error': f'Failed to calculate DST transitions: {str(e)}'}), 500

@app.route('/api/week-day-info')
def week_day_info():
    """API endpoint - returns interesting facts about the current week and day"""
    city = request.args.get('city', 'London')
    
    if city not in CITIES:
        return jsonify({'error': 'City not found'}), 404
    
    city_info = CITIES[city]
    tz = pytz.timezone(city_info['tz'])
    current_time = datetime.now(tz)
    
    week_number = int(current_time.strftime('%W'))
    day_number = int(current_time.strftime('%j'))
    year = current_time.year
    
    # Calculate days remaining in year
    end_of_year = datetime(year, 12, 31, tzinfo=tz)
    days_remaining = (end_of_year - current_time).days
    
    # Calculate percentage of year completed
    total_days = 366 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 365
    year_progress = (day_number / total_days) * 100
    
    # Week facts
    weeks_remaining = 52 - week_number
    
    # Day of week info
    day_name = current_time.strftime('%A')
    month_name = current_time.strftime('%B')
    day_of_month = int(current_time.strftime('%d'))
    
    # Calculate which quarter we're in
    month = current_time.month
    if month <= 3:
        quarter = 1
    elif month <= 6:
        quarter = 2
    elif month <= 9:
        quarter = 3
    else:
        quarter = 4
    
    # Fun facts about the day number
    day_facts = []
    if day_number == 1:
        day_facts.append("🎉 First day of the year!")
    elif day_number == 100:
        day_facts.append("💯 The 100th day of the year!")
    elif day_number == 200:
        day_facts.append("🎊 The 200th day of the year!")
    elif day_number == total_days:
        day_facts.append("🎆 Last day of the year!")
    elif day_number == total_days // 2:
        day_facts.append("⚖️ Halfway through the year!")
    
    # Week facts
    week_facts = []
    if week_number == 1:
        week_facts.append("🌟 First week of the year!")
    elif week_number == 26:
        week_facts.append("⚖️ Halfway through the year!")
    elif week_number == 52:
        week_facts.append("🎊 Final week of the year!")
    
    # Special day patterns
    if day_number % 100 == 0:
        day_facts.append(f"🔢 Day {day_number} - a perfect hundred!")
    
    # Seasonal info - account for hemisphere
    latitude = city_info['lat']
    is_southern_hemisphere = latitude < 0
    
    if is_southern_hemisphere:
        # Southern hemisphere - seasons are reversed
        if month in [12, 1, 2]:
            season = "Summer ☀️"
        elif month in [3, 4, 5]:
            season = "Autumn 🍂"
        elif month in [6, 7, 8]:
            season = "Winter ❄️"
        else:
            season = "Spring 🌸"
    else:
        # Northern hemisphere
        if month in [12, 1, 2]:
            season = "Winter ❄️"
        elif month in [3, 4, 5]:
            season = "Spring 🌸"
        elif month in [6, 7, 8]:
            season = "Summer ☀️"
        else:
            season = "Autumn 🍂"
    
    return jsonify({
        'city': city,
        'current_date': current_time.strftime('%A, %B %d, %Y'),
        'week_number': week_number,
        'day_number': day_number,
        'day_name': day_name,
        'month_name': month_name,
        'day_of_month': day_of_month,
        'year': year,
        'quarter': quarter,
        'season': season,
        'days_remaining': days_remaining,
        'weeks_remaining': weeks_remaining,
        'year_progress': round(year_progress, 1),
        'total_days_in_year': total_days,
        'is_leap_year': total_days == 366,
        'day_facts': day_facts,
        'week_facts': week_facts
    })

@app.route('/api/meeting-planner')
def meeting_planner():
    """API endpoint - finds best meeting times across timezones with improved scoring"""
    # Get selected cities from query params (comma-separated)
    cities_param = request.args.get('cities', '')
    if not cities_param:
        return jsonify({'error': 'No cities specified'}), 400
    
    selected_cities = [c.strip() for c in cities_param.split(',') if c.strip()]
    if len(selected_cities) < 2:
        return jsonify({'error': 'At least 2 cities required'}), 400
    
    # Get duration in hours (default 1)
    duration = float(request.args.get('duration', 1))
    
    # Get date (default today)
    date_str = request.args.get('date', '')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
        except:
            target_date = datetime.now()
    else:
        target_date = datetime.now()
    
    # Define time ranges with weighted scoring
    # Business hours (9 AM - 6 PM): 3 points - ideal working hours
    # Extended hours (7-9 AM, 6-9 PM): 2 points - acceptable early/late
    # Acceptable hours (6-7 AM, 9-10 PM): 1 point - very early/late but possible
    # Outside (10 PM - 6 AM): 0 points - night time
    business_start = 9
    business_end = 18
    extended_morning_start = 7
    extended_evening_end = 21
    acceptable_start = 6
    acceptable_end = 22
    
    # Analyze each hour of the day
    time_slots = []
    
    for hour in range(24):
        slot_info = {
            'hour': hour,
            'time_display': f"{hour:02d}:00",
            'cities': {},
            'score': 0,
            'business_count': 0,
            'extended_count': 0,
            'acceptable_count': 0,
            'outside_count': 0,
            'category': 'ideal'  # Will be updated based on analysis
        }
        
        # Check this hour for each city
        for city in selected_cities:
            if city not in CITIES:
                continue
            
            city_info = CITIES[city]
            tz = pytz.timezone(city_info['tz'])
            
            # Create datetime for this hour in the first city's timezone
            if selected_cities[0] in CITIES:
                first_tz = pytz.timezone(CITIES[selected_cities[0]]['tz'])
                base_time = first_tz.localize(target_date.replace(hour=hour, minute=0, second=0))
                city_time = base_time.astimezone(tz)
            else:
                city_time = tz.localize(target_date.replace(hour=hour, minute=0, second=0))
            
            city_hour = city_time.hour
            
            # Determine time category for this city
            in_business = business_start <= city_hour < business_end
            in_extended = (extended_morning_start <= city_hour < business_start) or (business_end <= city_hour < extended_evening_end)
            in_acceptable = (acceptable_start <= city_hour < extended_morning_start) or (extended_evening_end <= city_hour < acceptable_end)
            in_range = acceptable_start <= city_hour < acceptable_end
            
            # Categorize
            if in_business:
                category = 'business'
                points = 3
                slot_info['business_count'] += 1
            elif in_extended:
                category = 'extended'
                points = 2
                slot_info['extended_count'] += 1
            elif in_acceptable:
                category = 'acceptable'
                points = 1
                slot_info['acceptable_count'] += 1
            else:
                category = 'outside'
                points = 0
                slot_info['outside_count'] += 1
            
            slot_info['cities'][city] = {
                'local_time': city_time.strftime('%H:%M'),
                'local_hour': city_hour,
                'category': category,
                'in_business_hours': in_business,
                'in_extended_hours': in_extended,
                'in_acceptable_hours': in_acceptable,
                'in_any_acceptable_range': in_range
            }
            
            slot_info['score'] += points
        
        # Determine overall slot category
        total_cities = len(selected_cities)
        if slot_info['business_count'] == total_cities:
            slot_info['category'] = 'ideal'
        elif slot_info['business_count'] >= total_cities * 0.5:
            slot_info['category'] = 'good'
        elif slot_info['outside_count'] == 0:
            slot_info['category'] = 'acceptable'
        else:
            slot_info['category'] = 'poor'
        
        time_slots.append(slot_info)
    
    # Sort by score (best times first), then by business count
    time_slots.sort(key=lambda x: (x['score'], x['business_count']), reverse=True)
    
    # Categorize slots
    ideal_slots = [slot for slot in time_slots if slot['category'] == 'ideal']
    good_slots = [slot for slot in time_slots if slot['category'] == 'good']
    acceptable_slots = [slot for slot in time_slots if slot['category'] == 'acceptable']
    
    # Get top slots from each category
    top_ideal = ideal_slots[:10]
    top_good = good_slots[:10]
    top_acceptable = acceptable_slots[:10]
    
    # Combine for display (show best available)
    if top_ideal:
        best_slots = top_ideal
        good_slots_display = top_good[:5] if top_good else []
    elif top_good:
        best_slots = top_good
        good_slots_display = top_acceptable[:5] if top_acceptable else []
    else:
        best_slots = top_acceptable[:10]
        good_slots_display = []
    
    return jsonify({
        'selected_cities': selected_cities,
        'duration': duration,
        'date': target_date.strftime('%Y-%m-%d'),
        'best_slots': best_slots,
        'good_slots': good_slots_display,
        'all_slots': time_slots,
        'summary': {
            'ideal_count': len(ideal_slots),
            'good_count': len(good_slots),
            'acceptable_count': len(acceptable_slots),
            'total_cities': len(selected_cities)
        }
    })

@app.route('/api/moon-phases')
def moon_phases():
    """API endpoint - returns both full moon and new moon dates for the current calendar year"""
    city = request.args.get('city', 'London')
    year = int(request.args.get('year', datetime.now().year))
    
    if city not in CITIES:
        return jsonify({'error': 'City not found'}), 404
    
    city_info = CITIES[city]
    tz = pytz.timezone(city_info['tz'])
    lat = city_info['lat']
    lon = city_info['lon']
    current_time = datetime.now(tz)
    
    # Get current moon details for this location
    current_moon_details = get_moon_details(current_time, lat, lon, tz)
    current_moon_phase_name, current_moon_phase_value, current_moon_illumination = get_moon_phase(current_time)
    
    # Get full moons and new moons for the specified year (default: current year)
    full_moons_utc = get_full_moons_for_year(year, current_time)
    new_moons_utc = get_new_moons_for_year(year, current_time)
    
    # Convert each full moon to the city's local timezone
    full_moons_local = []
    for fm in full_moons_utc:
        fm_dt = datetime.fromisoformat(fm['datetime'])
        fm_local = fm_dt.astimezone(tz)
        
        # Calculate moon phase details for this date
        moon_phase_name, moon_phase_value, moon_illumination = get_moon_phase(fm_local)
        
        full_moons_local.append({
            'datetime_utc': fm['datetime'],
            'datetime_local': fm_local.isoformat(),
            'date_local': fm_local.strftime('%Y-%m-%d'),
            'time_local': fm_local.strftime('%H:%M:%S'),
            'day_name': fm_local.strftime('%A'),
            'formatted_date': fm_local.strftime('%A, %B %d, %Y at %H:%M'),
            'month': fm_local.strftime('%B'),
            'year': fm_local.year,
            'timestamp': fm['timestamp'],
            'phase_name': moon_phase_name,
            'illumination': moon_illumination
        })
    
    # Convert each new moon to the city's local timezone
    new_moons_local = []
    for nm in new_moons_utc:
        nm_dt = datetime.fromisoformat(nm['datetime'])
        nm_local = nm_dt.astimezone(tz)
        
        # Calculate moon phase details for this date
        moon_phase_name, moon_phase_value, moon_illumination = get_moon_phase(nm_local)
        
        new_moons_local.append({
            'datetime_utc': nm['datetime'],
            'datetime_local': nm_local.isoformat(),
            'date_local': nm_local.strftime('%Y-%m-%d'),
            'time_local': nm_local.strftime('%H:%M:%S'),
            'day_name': nm_local.strftime('%A'),
            'formatted_date': nm_local.strftime('%A, %B %d, %Y at %H:%M'),
            'month': nm_local.strftime('%B'),
            'year': nm_local.year,
            'timestamp': nm['timestamp'],
            'phase_name': moon_phase_name,
            'illumination': moon_illumination
        })
    
    return jsonify({
        'city': city,
        'timezone': city_info['tz'],
        'current_time': current_time.isoformat(),
        'year': year,
        'current_moon': {
            'phase_name': current_moon_phase_name,
            'illumination': current_moon_illumination,
            'distance_km': current_moon_details['distance_km'],
            'distance_miles': current_moon_details['distance_miles'],
            'azimuth': current_moon_details['azimuth'],
            'altitude': current_moon_details['altitude'],
            'direction': current_moon_details['direction_label'],
            'moonrise': current_moon_details['moonrise'],
            'moonset': current_moon_details['moonset'],
            'zodiac_sign': current_moon_details['zodiac_sign'],
            'astronomical_constellation': current_moon_details['astronomical_constellation']
        },
        'full_moons': full_moons_local,
        'new_moons': new_moons_local,
        'full_moon_count': len(full_moons_local),
        'new_moon_count': len(new_moons_local)
    })

@app.route('/api/solar-events')
def solar_events():
    """API endpoint - returns solar events (solstices and equinoxes) for the current calendar year"""
    city = request.args.get('city', 'London')
    year = int(request.args.get('year', datetime.now().year))
    
    if city not in CITIES:
        return jsonify({'error': 'City not found'}), 404
    
    city_info = CITIES[city]
    tz = pytz.timezone(city_info['tz'])
    lat = city_info['lat']
    lon = city_info['lon']
    
    # Get solar events for the specified year
    events = get_solar_events_for_year(year, lat, lon, tz)
    
    return jsonify({
        'city': city,
        'timezone': city_info['tz'],
        'year': year,
        'events': events,
        'count': len(events)
    })

if __name__ == '__main__':
    import os
    # Only print startup messages once (not in reloader process)
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        print("🌍 World Clock starting...")
        print("⚡ Weather data will load on-demand (API quota protection)")
        print(f"🚀 Server ready! Open http://localhost:5001")
        print("-" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5001)

# Made with Bob
