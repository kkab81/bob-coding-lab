"""
Weather cache builder for the World Clock application.

Usage:
    python3 weather.py

This script fetches weather data for all cities defined in app.py,
stores the results in weather_cache.json, and prints verbose progress
including total API requests made.
"""
from datetime import datetime, timedelta, timezone
import json
import time
import sys
from pathlib import Path

import httpx

from app import CITIES, WEATHER_CODES, get_wind_direction

CACHE_FILE = Path(__file__).resolve().parent / "weather_cache.json"
PROGRESS_FILE = Path(__file__).resolve().parent / "weather_progress.json"
CACHE_VALID_HOURS = 24
REQUEST_TIMEOUT = 20.0
RETRY_COUNT = 3
RETRY_BASE_DELAY = 3


def update_progress(status, current=0, total=0, city=None, message=None):
    """Write progress to a JSON file for the web UI to read"""
    progress_data = {
        "status": status,  # "running", "complete", "error"
        "current": current,
        "total": total,
        "city": city,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    try:
        PROGRESS_FILE.write_text(json.dumps(progress_data), encoding="utf-8")
        sys.stdout.flush()  # Ensure output is flushed
    except Exception:
        pass  # Don't let progress tracking break the main process


def iso_utc(dt):
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_weather_url(lat, lon):
    return (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        "&current_weather=true"
        "&daily=weathercode,temperature_2m_max,temperature_2m_min,rain_sum,"
        "precipitation_probability_max,windspeed_10m_max"
        "&timezone=auto"
        "&wind_speed_unit=mph"
        "&forecast_days=5"
    )


def build_air_quality_url(lat, lon):
    """Build URL for Open-Meteo Air Quality API"""
    return (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}"
        f"&longitude={lon}"
        "&current=us_aqi,pm10,pm2_5"
        "&timezone=auto"
    )


def fetch_city_weather(client, city_name, city_info, counters, city_index, total_cities):
    lat = city_info["lat"]
    lon = city_info["lon"]
    weather_url = build_weather_url(lat, lon)
    aqi_url = build_air_quality_url(lat, lon)

    for attempt in range(1, RETRY_COUNT + 1):
        counters["requests"] += 1
        update_progress("running", city_index, total_cities, city_name,
                       f"Fetching weather (attempt {attempt}/{RETRY_COUNT})")
        print(f"🌤️  [{city_name}] Weather request {counters['requests']} (attempt {attempt}/{RETRY_COUNT})")

        try:
            response = client.get(weather_url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            current = data["current_weather"]
            daily = data["daily"]

            current_payload = {
                "temperature": f"{current['temperature']:.1f}°C",
                "conditions": WEATHER_CODES.get(current["weathercode"], "Unknown"),
                "minmax": f"{daily['temperature_2m_min'][0]:.1f} - {daily['temperature_2m_max'][0]:.1f}°C",
                "wind": f"{current['windspeed']:.1f} mph {get_wind_direction(current['winddirection'])}",
                "rain": daily["rain_sum"][0] or 0
            }

            # Fetch Air Quality data
            aqi_data = None
            try:
                counters["requests"] += 1
                update_progress("running", city_index, total_cities, city_name, "Fetching air quality data")
                print(f"🌬️  [{city_name}] AQI request {counters['requests']}")
                aqi_response = client.get(aqi_url, timeout=REQUEST_TIMEOUT)
                aqi_response.raise_for_status()
                aqi_json = aqi_response.json()
                
                if "current" in aqi_json:
                    aqi_current = aqi_json["current"]
                    aqi_data = {
                        "us_aqi": aqi_current.get("us_aqi"),
                        "pm10": aqi_current.get("pm10"),
                        "pm2_5": aqi_current.get("pm2_5")
                    }
                    print(f"   ✓ AQI: {aqi_data['us_aqi']}")
            except Exception as aqi_error:
                print(f"   ⚠️  AQI fetch failed: {aqi_error}")
                aqi_data = None

            # Add AQI to current payload
            current_payload["aqi"] = aqi_data

            forecast_payload = []
            for i in range(len(daily["time"])):
                forecast_payload.append({
                    "date": daily["time"][i],
                    "temp_max": daily["temperature_2m_max"][i],
                    "temp_min": daily["temperature_2m_min"][i],
                    "weathercode": daily["weathercode"][i],
                    "conditions": WEATHER_CODES.get(daily["weathercode"][i], "Unknown"),
                    "precipitation": daily.get("precipitation_probability_max", [0] * len(daily["time"]))[i],
                    "wind_speed": daily.get("windspeed_10m_max", [0] * len(daily["time"]))[i],
                    "rain": daily["rain_sum"][i] or 0
                })

            update_progress("running", city_index, total_cities, city_name, "✅ Complete")
            print(f"✅ [{city_name}] Current + 5-day forecast cached")
            return {
                "current": current_payload,
                "forecast": forecast_payload,
                "fetched_at": iso_utc(datetime.now(timezone.utc))
            }, None

        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status == 429 and attempt < RETRY_COUNT:
                wait_seconds = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                print(f"⚠️  [{city_name}] Rate limited (HTTP 429). Waiting {wait_seconds}s before retry...")
                time.sleep(wait_seconds)
                continue

            message = f"HTTP {status}"
            print(f"❌ [{city_name}] {message}")
            return None, message

        except Exception as exc:
            if attempt < RETRY_COUNT:
                wait_seconds = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                print(f"⚠️  [{city_name}] {type(exc).__name__}: {str(exc)[:120]}")
                print(f"   Retrying in {wait_seconds}s...")
                time.sleep(wait_seconds)
                continue

            message = f"{type(exc).__name__}: {str(exc)}"
            print(f"❌ [{city_name}] {message[:160]}")
            return None, message

    return None, "Unknown error"


def main():
    started_at = datetime.now(timezone.utc)
    expires_at = started_at + timedelta(hours=CACHE_VALID_HOURS)
    counters = {"requests": 0}

    total_cities = len(CITIES)
    update_progress("running", 0, total_cities, None, "Starting weather refresh...")

    print("🌍 Weather cache build starting...")
    print(f"📍 Cities to process: {total_cities}")
    print(f"🕒 Cache validity: {CACHE_VALID_HOURS} hours")
    print(f"💾 Output file: {CACHE_FILE}")
    print("-" * 60)

    city_results = {}
    failed_cities = []

    with httpx.Client() as client:
        for index, (city_name, city_info) in enumerate(CITIES.items(), start=1):
            print(f"\n[{index}/{total_cities}] Processing {city_name}...")
            result, error = fetch_city_weather(client, city_name, city_info, counters, index, total_cities)

            if result is not None:
                city_results[city_name] = result
            else:
                city_results[city_name] = {
                    "current": None,
                    "forecast": None,
                    "fetched_at": iso_utc(datetime.now(timezone.utc)),
                    "error": error
                }
                failed_cities.append(city_name)

            print(f"📊 Progress: {index}/{len(CITIES)} cities complete")

    payload = {
        "generated_at": iso_utc(started_at),
        "expires_at": iso_utc(expires_at),
        "cache_valid_hours": CACHE_VALID_HOURS,
        "request_count": counters["requests"],
        "success_count": len(CITIES) - len(failed_cities),
        "failure_count": len(failed_cities),
        "failed_cities": failed_cities,
        "cities": city_results
    }

    update_progress("running", total_cities, total_cities, None, "Writing cache file...")
    CACHE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    update_progress("complete", total_cities, total_cities, None,
                   f"✅ Complete! {payload['success_count']} cities updated")

    print("\n" + "=" * 60)
    print("✅ Weather cache build complete")
    print(f"💾 Cache written to: {CACHE_FILE}")
    print(f"✅ Successful cities: {payload['success_count']}")
    print(f"❌ Failed cities: {payload['failure_count']}")
    if failed_cities:
        print(f"⚠️  Failures: {', '.join(failed_cities)}")
    print(f"🔢 Total API requests made: {payload['request_count']}")
    print(f"🕒 Cache valid until: {payload['expires_at']}")
    print("=" * 60)


if __name__ == "__main__":
    main()

# Made with Bob
