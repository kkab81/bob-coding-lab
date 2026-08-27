# 🌍 World Time Application

A Flask-based world clock application displaying real-time information for 50+ cities worldwide, including time, weather, sunrise/sunset, moon phases, and holidays.

**Author:** Alex Abderrazag, IBM UK  
**Version:** 1

## Features

- **Real-time Clock**: Live time display for 50+ cities across all continents
- **Weather Data**: Current conditions and 5-day forecasts (via Open-Meteo API)
- **Astronomical Info**: Sunrise/sunset times, moon phases, and illumination
- **Public Holidays**: Country-specific holiday calendars
- **DST Tracking**: Daylight saving time transitions
- **Meeting Planner**: Find optimal meeting times across timezones
- **Responsive UI**: Clean, modern interface

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd wt-2

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Fetch weather data (optional)
python3 weather.py

# Run application
python3 app.py
```

Open browser: **http://localhost:5001**

## Project Structure

```
wt-2/
├── app.py              # Main Flask application
├── weather.py          # Weather cache builder
├── requirements.txt    # Python dependencies
├── SETUP.md           # Detailed setup guide
├── templates/
│   └── index.html     # Frontend UI
└── weather_cache.json # Weather data cache (generated)
```

## API Endpoints

- `GET /api/worldclock` - Time data for all cities
- `GET /api/forecast?city=<name>` - 5-day weather forecast
- `GET /api/holidays?city=<name>` - Public holidays
- `GET /api/dst-transitions?city=<name>` - DST changes
- `GET /api/meeting-planner?cities=<list>` - Optimal meeting times
- `POST /api/refresh-weather` - Manual weather refresh

## Weather Data

Weather data is cached for 24 hours to respect API rate limits. To refresh:

```bash
python3 weather.py
```

Or use the in-app refresh button (rate-limited to once per 2 hours).

## Supported Cities

**50+ cities** including:
- **Europe**: London, Paris, Berlin, Amsterdam, Madrid, Rome, Stockholm, Warsaw, Athens, Istanbul, Moscow
- **Asia**: Tokyo, Hong Kong, Singapore, Bangkok, Dubai, Tel Aviv, Kolkata, Seoul
- **Americas**: New York, Los Angeles, Toronto, Mexico City, Buenos Aires, São Paulo
- **Oceania**: Sydney, Melbourne, Auckland, Perth
- **Africa**: Cairo, Johannesburg, Lagos, Nairobi, Cape Town

## Dependencies

- Flask 3.1.0 - Web framework
- pytz 2024.2 - Timezone handling
- httpx 0.27.2 - HTTP client for weather API
- holidays 0.94 - Public holiday data
- ephem 4.2.1 - Astronomical calculations

## Configuration

Edit `app.py` to:
- Change port (default: 5001)
- Add/remove cities
- Adjust weather cache duration
- Modify API endpoints

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5001 in use | Change port in `app.py` line 839 |
| Weather not showing | Run `python3 weather.py` |
| Command not found | Activate virtual environment |

## License

---

For detailed setup instructions, see [SETUP.md](SETUP.md)
