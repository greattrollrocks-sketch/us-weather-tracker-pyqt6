import os
import sys
from datetime import datetime

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFrame,
)

# Representative coordinates (state capitals) for each US state
STATE_COORDS = {
    "alabama": (32.377716, -86.300568),
    "alaska": (58.301598, -134.420212),
    "arizona": (33.448143, -112.096962),
    "arkansas": (34.746613, -92.288986),
    "california": (38.576668, -121.493629),
    "colorado": (39.739227, -104.984856),
    "connecticut": (41.764046, -72.682198),
    "delaware": (39.157307, -75.519722),
    "florida": (30.438118, -84.281296),
    "georgia": (33.749027, -84.388229),
    "hawaii": (21.307442, -157.857376),
    "idaho": (43.617775, -116.199722),
    "illinois": (39.798363, -89.654961),
    "indiana": (39.768623, -86.162643),
    "iowa": (41.591087, -93.603729),
    "kansas": (39.048191, -95.677956),
    "kentucky": (38.186722, -84.875374),
    "louisiana": (30.457069, -91.187393),
    "maine": (44.307167, -69.781693),
    "maryland": (38.978764, -76.490936),
    "massachusetts": (42.358162, -71.063698),
    "michigan": (42.733635, -84.555328),
    "minnesota": (44.955097, -93.102211),
    "mississippi": (32.303848, -90.182106),
    "missouri": (38.579201, -92.172935),
    "montana": (46.585709, -112.018417),
    "nebraska": (40.808075, -96.699654),
    "nevada": (39.163914, -119.766121),
    "new hampshire": (43.206898, -71.537994),
    "new jersey": (40.220596, -74.769913),
    "new mexico": (35.68224, -105.939728),
    "new york": (42.652843, -73.757874),
    "north carolina": (35.78043, -78.639099),
    "north dakota": (46.82085, -100.783318),
    "ohio": (39.961346, -82.999069),
    "oklahoma": (35.492207, -97.503342),
    "oregon": (44.938461, -123.030403),
    "pennsylvania": (40.264378, -76.883598),
    "rhode island": (41.830914, -71.414963),
    "south carolina": (34.000343, -81.033211),
    "south dakota": (44.367031, -100.346405),
    "tennessee": (36.16581, -86.784241),
    "texas": (30.27467, -97.740349),
    "utah": (40.777477, -111.888237),
    "vermont": (44.262436, -72.580536),
    "virginia": (37.538857, -77.43364),
    "washington": (47.035805, -122.905014),
    "west virginia": (38.336246, -81.612328),
    "wisconsin": (43.074684, -89.384445),
    "wyoming": (41.140259, -104.820236),
}

STATE_ABBREVS = {
    "al": "alabama", "ak": "alaska", "az": "arizona", "ar": "arkansas", "ca": "california",
    "co": "colorado", "ct": "connecticut", "de": "delaware", "fl": "florida", "ga": "georgia",
    "hi": "hawaii", "id": "idaho", "il": "illinois", "in": "indiana", "ia": "iowa",
    "ks": "kansas", "ky": "kentucky", "la": "louisiana", "me": "maine", "md": "maryland",
    "ma": "massachusetts", "mi": "michigan", "mn": "minnesota", "ms": "mississippi", "mo": "missouri",
    "mt": "montana", "ne": "nebraska", "nv": "nevada", "nh": "new hampshire", "nj": "new jersey",
    "nm": "new mexico", "ny": "new york", "nc": "north carolina", "nd": "north dakota", "oh": "ohio",
    "ok": "oklahoma", "or": "oregon", "pa": "pennsylvania", "ri": "rhode island", "sc": "south carolina",
    "sd": "south dakota", "tn": "tennessee", "tx": "texas", "ut": "utah", "vt": "vermont",
    "va": "virginia", "wa": "washington", "wv": "west virginia", "wi": "wisconsin", "wy": "wyoming",
}


def normalize_state(user_input: str):
    value = user_input.strip().lower()
    if not value:
        return None
    if value in STATE_COORDS:
        return value
    if value in STATE_ABBREVS:
        return STATE_ABBREVS[value]
    return None


def icon_url(icon_code: str):
    return f"https://openweathermap.org/img/wn/{icon_code}@2x.png"


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.dark_mode = True
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        self.setWindowTitle("US Weather Tracker (PyQt6)")
        self.setMinimumSize(700, 620)

        main = QVBoxLayout()
        main.setSpacing(10)

        title = QLabel("US State Weather Tracker")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        main.addWidget(title)

        subtitle = QLabel("Type a US state (e.g., California / CA) or use auto-detect")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(subtitle)

        input_row = QHBoxLayout()
        self.input_state = QLineEdit()
        self.input_state.setPlaceholderText("Enter state or abbreviation...")
        self.input_state.returnPressed.connect(self.fetch_by_state)

        self.btn_get = QPushButton("Get Weather")
        self.btn_get.clicked.connect(self.fetch_by_state)

        self.btn_auto = QPushButton("Auto Detect Location")
        self.btn_auto.clicked.connect(self.fetch_by_auto_location)

        self.btn_theme = QPushButton("Toggle Dark/Light")
        self.btn_theme.clicked.connect(self.toggle_theme)

        input_row.addWidget(self.input_state)
        input_row.addWidget(self.btn_get)
        input_row.addWidget(self.btn_auto)
        input_row.addWidget(self.btn_theme)
        main.addLayout(input_row)

        self.status = QLabel("Ready")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main.addWidget(self.status)

        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedHeight(90)
        main.addWidget(self.icon_label)

        self.temp_label = QLabel("Temperature: --")
        self.feels_like_label = QLabel("Feels Like: --")
        self.condition_label = QLabel("Condition: --")
        self.humidity_label = QLabel("Humidity: --")
        self.wind_label = QLabel("Wind: --")

        for label in [
            self.temp_label,
            self.feels_like_label,
            self.condition_label,
            self.humidity_label,
            self.wind_label,
        ]:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFont(QFont("Arial", 12))
            main.addWidget(label)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        main.addWidget(sep)

        forecast_title = QLabel("5-Day Forecast (around 12:00 PM)")
        forecast_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        forecast_title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        main.addWidget(forecast_title)

        self.forecast_labels = []
        for _ in range(5):
            lbl = QLabel("--")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFont(QFont("Arial", 11))
            self.forecast_labels.append(lbl)
            main.addWidget(lbl)

        hint = QLabel("API key is read from OPENWEATHER_API_KEY env var (never hardcoded).")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color: #888;")
        main.addWidget(hint)

        self.setLayout(main)

    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet(
                """
                QWidget { background-color: #121212; color: #EDEDED; }
                QLineEdit { background-color: #1E1E1E; border: 1px solid #333; padding: 8px; border-radius: 6px; }
                QPushButton { background-color: #2C2C2C; border: 1px solid #444; padding: 8px 10px; border-radius: 6px; }
                QPushButton:hover { background-color: #3A3A3A; }
                """
            )
        else:
            self.setStyleSheet(
                """
                QWidget { background-color: #F4F6F8; color: #1D1D1D; }
                QLineEdit { background-color: #FFFFFF; border: 1px solid #BBB; padding: 8px; border-radius: 6px; }
                QPushButton { background-color: #FFFFFF; border: 1px solid #BBB; padding: 8px 10px; border-radius: 6px; }
                QPushButton:hover { background-color: #ECECEC; }
                """
            )

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def ensure_api_key(self):
        if not self.api_key:
            QMessageBox.warning(
                self,
                "Missing API Key",
                "Set OPENWEATHER_API_KEY before running.\n"
                "macOS/Linux: export OPENWEATHER_API_KEY='your_key'",
            )
            return False
        return True

    def fetch_by_state(self):
        if not self.ensure_api_key():
            return

        state_key = normalize_state(self.input_state.text())
        if not state_key:
            QMessageBox.information(self, "Invalid State", "Enter a valid US state name or abbreviation.")
            return

        lat, lon = STATE_COORDS[state_key]
        self.fetch_and_render(lat, lon, state_key.title())

    def fetch_by_auto_location(self):
        if not self.ensure_api_key():
            return

        self.status.setText("Detecting location...")
        try:
            geo = requests.get("https://ipapi.co/json/", timeout=10).json()
            region = (geo.get("region") or "").strip()
            state_key = normalize_state(region)

            if state_key:
                lat, lon = STATE_COORDS[state_key]
                label = f"{state_key.title()} (Auto)"
            else:
                lat, lon = geo.get("latitude"), geo.get("longitude")
                if lat is None or lon is None:
                    raise ValueError("Could not detect coordinates from IP location")
                label = f"{geo.get('city', 'Your Area')} (Auto)"

            self.fetch_and_render(float(lat), float(lon), label)
        except Exception as exc:
            self.status.setText("Auto-detect failed")
            QMessageBox.critical(self, "Auto Location Error", str(exc))

    def fetch_and_render(self, lat: float, lon: float, label: str):
        self.status.setText(f"Loading weather for {label}...")
        current_url = "https://api.openweathermap.org/data/2.5/weather"
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "imperial"}

        try:
            current_resp = requests.get(current_url, params=params, timeout=12)
            current_resp.raise_for_status()
            current = current_resp.json()

            forecast_resp = requests.get(forecast_url, params=params, timeout=12)
            forecast_resp.raise_for_status()
            forecast = forecast_resp.json()
        except requests.RequestException as exc:
            self.status.setText("Failed to fetch weather")
            QMessageBox.critical(self, "Network/API Error", str(exc))
            return

        temp = current["main"].get("temp", 0.0)
        feels_like = current["main"].get("feels_like", 0.0)
        humidity = current["main"].get("humidity", "--")
        weather_info = current.get("weather", [{}])[0]
        description = weather_info.get("description", "Unknown")
        wind = current.get("wind", {}).get("speed", "--")

        self.temp_label.setText(f"Temperature: {temp:.1f} °F")
        self.feels_like_label.setText(f"Feels Like: {feels_like:.1f} °F")
        self.condition_label.setText(f"Condition: {description.title()}")
        self.humidity_label.setText(f"Humidity: {humidity}%")
        self.wind_label.setText(f"Wind: {wind} mph")
        self.status.setText(f"Showing weather for {label}")

        # Weather icon
        icon_code = weather_info.get("icon")
        if icon_code:
            try:
                img = requests.get(icon_url(icon_code), timeout=10).content
                pix = QPixmap()
                pix.loadFromData(img)
                self.icon_label.setPixmap(pix.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            except requests.RequestException:
                self.icon_label.clear()
        else:
            self.icon_label.clear()

        # 5-day forecast: pick entries closest to 12:00 each day
        daily = {}
        for item in forecast.get("list", []):
            dt = datetime.fromtimestamp(item.get("dt", 0))
            day_key = dt.date().isoformat()
            if day_key not in daily:
                daily[day_key] = []
            daily[day_key].append(item)

        forecast_lines = []
        for day in sorted(daily.keys())[:5]:
            slots = daily[day]
            best = min(slots, key=lambda i: abs(datetime.fromtimestamp(i["dt"]).hour - 12))
            d = datetime.fromtimestamp(best["dt"]).strftime("%a %b %d")
            t = best["main"].get("temp", 0)
            desc = best.get("weather", [{}])[0].get("description", "Unknown").title()
            forecast_lines.append(f"{d}: {t:.0f}°F, {desc}")

        for i in range(5):
            self.forecast_labels[i].setText(forecast_lines[i] if i < len(forecast_lines) else "--")


def main():
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
