# US Weather Tracker (PyQt6)

Desktop weather app built with Python + PyQt6.

## Features
- Search weather by **US state name or abbreviation** (e.g., `Texas`, `TX`)
- **Auto-detect location** from IP and fetch weather
- **Current weather icon** display
- **5-day forecast** summary
- **Dark/Light mode toggle**
- API key is loaded from environment variable (not hardcoded)

## Setup
```bash
python3 -m pip install -r requirements.txt
export OPENWEATHER_API_KEY="your_openweather_api_key"
python3 main.py
```

## API
Uses OpenWeather endpoints:
- Current weather: `/data/2.5/weather`
- 5-day forecast: `/data/2.5/forecast`
