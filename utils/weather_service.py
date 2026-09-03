"""
Real-time weather integration using Open-Meteo API and OpenWeather API.
Fetches high-resolution current, historical (past 7 days), and forecast (14 days)
meteorological and soil moisture variables.
"""

import requests
import requests_cache
import pandas as pd
import numpy as np
from retry_requests import retry
import openmeteo_requests

OPENWEATHER_API_KEY = "b9ce4e84aac9aeb541da6cda7d2186f7"

# Initialize cached and retrying Open-Meteo client
_cache_session = requests_cache.CachedSession('.cache', expire_after=1800)
_retry_session = retry(_cache_session, retries=4, backoff_factor=0.3)
_openmeteo_client = openmeteo_requests.Client(session=_retry_session)


def fetch_openmeteo_weather(lat: float, lon: float, past_days: int = 7, forecast_days: int = 14) -> dict:
    """
    Fetch comprehensive weather & multi-depth soil moisture data from Open-Meteo API.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": [
            "temperature_2m", "relative_humidity_2m", "dew_point_2m", 
            "apparent_temperature", "precipitation", "precipitation_probability", "rain",
            "soil_moisture_27_to_81cm", "soil_moisture_9_to_27cm", "soil_moisture_3_to_9cm", 
            "soil_moisture_1_to_3cm", "soil_moisture_0_to_1cm",
            "soil_temperature_54cm", "soil_temperature_18cm", "soil_temperature_6cm", "soil_temperature_0cm",
            "cloud_cover_high", "cloud_cover_mid", "cloud_cover_low", "cloud_cover",
            "surface_pressure",
            "wind_direction_180m", "wind_direction_120m", "wind_direction_80m", "wind_direction_10m",
            "wind_speed_180m", "wind_speed_120m", "wind_speed_80m", "wind_speed_10m"
        ],
        "current": ["precipitation", "temperature_2m", "relative_humidity_2m", "apparent_temperature", "rain"],
        "past_days": past_days,
        "forecast_days": forecast_days,
    }

    try:
        responses = _openmeteo_client.weather_api(url, params=params)
        response = responses[0]

        # Process current data
        current = response.Current()
        curr_precip = float(current.Variables(0).Value())
        curr_temp = float(current.Variables(1).Value())
        curr_humidity = float(current.Variables(2).Value())
        curr_apparent_temp = float(current.Variables(3).Value())
        curr_rain = float(current.Variables(4).Value())

        # Process hourly data
        hourly = response.Hourly()
        n_vars = hourly.VariablesLength()
        
        start_ts = pd.to_datetime(hourly.Time(), unit="s", utc=True)
        end_ts = pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True)
        date_range = pd.date_range(
            start=start_ts,
            end=end_ts,
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )

        hourly_dict = {"datetime": date_range}
        var_names = params["hourly"]
        for idx, vname in enumerate(var_names):
            if idx < n_vars:
                hourly_dict[vname] = hourly.Variables(idx).ValuesAsNumpy()

        df_hourly = pd.DataFrame(hourly_dict)
        df_hourly['date'] = df_hourly['datetime'].dt.date

        # Compute key hydrometeorological trigger metrics
        now_utc = pd.Timestamp.now(tz="UTC")
        df_past = df_hourly[df_hourly['datetime'] <= now_utc]
        df_future = df_hourly[df_hourly['datetime'] > now_utc]

        # Past rainfall accumulation
        rain_past_24h = float(df_past.tail(24)['precipitation'].sum()) if len(df_past) >= 24 else float(df_past['precipitation'].sum())
        rain_past_48h = float(df_past.tail(48)['precipitation'].sum()) if len(df_past) >= 48 else float(df_past['precipitation'].sum())
        rain_past_72h = float(df_past.tail(72)['precipitation'].sum()) if len(df_past) >= 72 else float(df_past['precipitation'].sum())
        rain_past_7d = float(df_past['precipitation'].sum())

        # Current soil moisture (most recent readings)
        latest_hourly = df_hourly.iloc[min(len(df_past), len(df_hourly)-1)] if len(df_past) > 0 else df_hourly.iloc[0]
        soil_top = float(np.mean([
            latest_hourly.get('soil_moisture_0_to_1cm', 0.25),
            latest_hourly.get('soil_moisture_1_to_3cm', 0.25),
            latest_hourly.get('soil_moisture_3_to_9cm', 0.25)
        ]))
        soil_mid = float(latest_hourly.get('soil_moisture_9_to_27cm', 0.28))
        soil_deep = float(latest_hourly.get('soil_moisture_27_to_81cm', 0.30))
        soil_mean = float(np.mean([soil_top, soil_mid, soil_deep]))

        # Daily aggregations for 14-day forecast
        daily_summary = df_hourly.groupby('date').agg({
            'precipitation': 'sum',
            'temperature_2m': ['min', 'max'],
            'soil_moisture_0_to_1cm': 'mean',
            'soil_moisture_3_to_9cm': 'mean',
            'soil_moisture_27_to_81cm': 'mean',
            'wind_speed_10m': 'max'
        })
        daily_summary.columns = [
            'total_precip_mm', 'temp_min_c', 'temp_max_c', 
            'soil_moist_top', 'soil_moist_mid', 'soil_moist_deep', 
            'wind_max_kmh'
        ]
        daily_summary = daily_summary.reset_index()

        return {
            "status": "success",
            "elevation": float(response.Elevation()),
            "latitude": float(response.Latitude()),
            "longitude": float(response.Longitude()),
            "current": {
                "temperature": curr_temp,
                "apparent_temperature": curr_apparent_temp,
                "humidity": curr_humidity,
                "precipitation_rate": curr_precip,
                "rain_rate": curr_rain,
            },
            "triggers": {
                "rain_past_24h": round(rain_past_24h, 2),
                "rain_past_48h": round(rain_past_48h, 2),
                "rain_past_72h": round(rain_past_72h, 2),
                "rain_past_7d": round(rain_past_7d, 2),
                "soil_moisture_top": round(soil_top, 4),
                "soil_moisture_mid": round(soil_mid, 4),
                "soil_moisture_deep": round(soil_deep, 4),
                "soil_moisture_mean": round(soil_mean, 4),
            },
            "hourly_df": df_hourly,
            "daily_df": daily_summary
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def fetch_openweather_current(lat: float, lon: float, api_key: str = OPENWEATHER_API_KEY) -> dict:
    """
    Fetch real-time weather conditions from OpenWeather API for validation and cross-checking.
    """
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            data = res.json()
            main = data.get("main", {})
            weather = data.get("weather", [{}])[0]
            rain = data.get("rain", {}).get("1h", 0.0)
            return {
                "status": "success",
                "city": data.get("name", "Unknown"),
                "temp": main.get("temp", 0.0),
                "feels_like": main.get("feels_like", 0.0),
                "humidity": main.get("humidity", 0),
                "pressure": main.get("pressure", 1013),
                "condition": weather.get("main", "Clear"),
                "description": weather.get("description", "").title(),
                "icon": weather.get("icon", "01d"),
                "wind_speed": data.get("wind", {}).get("speed", 0.0),
                "rain_1h": rain
            }
        else:
            return {"status": "error", "message": f"HTTP {res.status_code}: {res.text}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
