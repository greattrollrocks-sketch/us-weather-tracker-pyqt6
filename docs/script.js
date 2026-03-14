const STATE_COORDS = {
  alabama:[32.377716,-86.300568], alaska:[58.301598,-134.420212], arizona:[33.448143,-112.096962], arkansas:[34.746613,-92.288986], california:[38.576668,-121.493629], colorado:[39.739227,-104.984856], connecticut:[41.764046,-72.682198], delaware:[39.157307,-75.519722], florida:[30.438118,-84.281296], georgia:[33.749027,-84.388229], hawaii:[21.307442,-157.857376], idaho:[43.617775,-116.199722], illinois:[39.798363,-89.654961], indiana:[39.768623,-86.162643], iowa:[41.591087,-93.603729], kansas:[39.048191,-95.677956], kentucky:[38.186722,-84.875374], louisiana:[30.457069,-91.187393], maine:[44.307167,-69.781693], maryland:[38.978764,-76.490936], massachusetts:[42.358162,-71.063698], michigan:[42.733635,-84.555328], minnesota:[44.955097,-93.102211], mississippi:[32.303848,-90.182106], missouri:[38.579201,-92.172935], montana:[46.585709,-112.018417], nebraska:[40.808075,-96.699654], nevada:[39.163914,-119.766121], 'new hampshire':[43.206898,-71.537994], 'new jersey':[40.220596,-74.769913], 'new mexico':[35.68224,-105.939728], 'new york':[42.652843,-73.757874], 'north carolina':[35.78043,-78.639099], 'north dakota':[46.82085,-100.783318], ohio:[39.961346,-82.999069], oklahoma:[35.492207,-97.503342], oregon:[44.938461,-123.030403], pennsylvania:[40.264378,-76.883598], 'rhode island':[41.830914,-71.414963], 'south carolina':[34.000343,-81.033211], 'south dakota':[44.367031,-100.346405], tennessee:[36.16581,-86.784241], texas:[30.27467,-97.740349], utah:[40.777477,-111.888237], vermont:[44.262436,-72.580536], virginia:[37.538857,-77.43364], washington:[47.035805,-122.905014], 'west virginia':[38.336246,-81.612328], wisconsin:[43.074684,-89.384445], wyoming:[41.140259,-104.820236]
};
const ABBR = {al:'alabama',ak:'alaska',az:'arizona',ar:'arkansas',ca:'california',co:'colorado',ct:'connecticut',de:'delaware',fl:'florida',ga:'georgia',hi:'hawaii',id:'idaho',il:'illinois',in:'indiana',ia:'iowa',ks:'kansas',ky:'kentucky',la:'louisiana',me:'maine',md:'maryland',ma:'massachusetts',mi:'michigan',mn:'minnesota',ms:'mississippi',mo:'missouri',mt:'montana',ne:'nebraska',nv:'nevada',nh:'new hampshire',nj:'new jersey',nm:'new mexico',ny:'new york',nc:'north carolina',nd:'north dakota',oh:'ohio',ok:'oklahoma',or:'oregon',pa:'pennsylvania',ri:'rhode island',sc:'south carolina',sd:'south dakota',tn:'tennessee',tx:'texas',ut:'utah',vt:'vermont',va:'virginia',wa:'washington',wv:'west virginia',wi:'wisconsin',wy:'wyoming'};

const $ = (id) => document.getElementById(id);
const stateInput = $('stateInput');
const statusEl = $('status');
const forecastEl = $('forecast');

$('themeBtn').onclick = () => document.documentElement.classList.toggle('light');
$('weatherBtn').onclick = () => fetchByState();
$('autoBtn').onclick = () => fetchAuto();

function normalizeState(v) {
  v = v.trim().toLowerCase();
  return STATE_COORDS[v] ? v : (ABBR[v] || null);
}

function weatherInfo(code) {
  const map = {
    0:['☀️','Clear sky'],1:['🌤️','Mostly clear'],2:['⛅','Partly cloudy'],3:['☁️','Overcast'],
    45:['🌫️','Fog'],48:['🌫️','Rime fog'],
    51:['🌦️','Light drizzle'],53:['🌦️','Drizzle'],55:['🌧️','Heavy drizzle'],
    61:['🌦️','Slight rain'],63:['🌧️','Rain'],65:['🌧️','Heavy rain'],
    71:['🌨️','Slight snow'],73:['❄️','Snow'],75:['❄️','Heavy snow'],
    80:['🌦️','Rain showers'],81:['🌧️','Rain showers'],82:['⛈️','Violent showers'],
    95:['⛈️','Thunderstorm'],96:['⛈️','Thunderstorm w/ hail'],99:['⛈️','Strong thunderstorm w/ hail']
  };
  return map[code] || ['🌡️','Unknown'];
}

function setCurrent(cur) {
  const [emoji, desc] = weatherInfo(cur.weather_code);
  $('iconText').textContent = emoji;
  $('cond').textContent = `Condition: ${desc}`;
  $('temp').textContent = `Temperature: ${cur.temperature_2m.toFixed(1)} °F`;
  $('feels').textContent = `Feels Like: ${cur.apparent_temperature.toFixed(1)} °F`;
  $('hum').textContent = `Humidity: ${cur.relative_humidity_2m}%`;
  $('wind').textContent = `Wind: ${cur.wind_speed_10m.toFixed(1)} mph`;
}

function setForecast(daily) {
  forecastEl.innerHTML = '';
  for (let i = 0; i < Math.min(5, daily.time.length); i++) {
    const [emoji, desc] = weatherInfo(daily.weather_code[i]);
    const d = new Date(daily.time[i] + 'T12:00:00').toLocaleDateString(undefined,{weekday:'short', month:'short', day:'numeric'});
    const hi = Math.round(daily.temperature_2m_max[i]);
    const lo = Math.round(daily.temperature_2m_min[i]);
    const li = document.createElement('li');
    li.textContent = `${d}: ${emoji} ${desc}, High ${hi}°F / Low ${lo}°F`;
    forecastEl.appendChild(li);
  }
}

async function fetchAndRender(lat, lon, label) {
  try {
    statusEl.textContent = `Loading ${label}...`;
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&temperature_unit=fahrenheit&wind_speed_unit=mph&current=temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Weather request failed');
    const data = await res.json();

    setCurrent(data.current);
    setForecast(data.daily);
    statusEl.textContent = `Showing weather for ${label}`;
  } catch (e) {
    statusEl.textContent = `Error: ${e.message}`;
  }
}

function pretty(name) {
  return name.replace(/\b\w/g, c => c.toUpperCase());
}

function fetchByState() {
  const s = normalizeState(stateInput.value);
  if (!s) return statusEl.textContent = 'Enter a valid US state.';
  const [lat, lon] = STATE_COORDS[s];
  fetchAndRender(lat, lon, pretty(s));
}

async function fetchAuto() {
  try {
    statusEl.textContent = 'Detecting location...';
    const geo = await (await fetch('https://ipapi.co/json/')).json();
    if (geo.region) {
      const s = normalizeState(geo.region);
      if (s) {
        const [lat, lon] = STATE_COORDS[s];
        return fetchAndRender(lat, lon, `${pretty(s)} (Auto)`);
      }
    }
    if (!geo.latitude || !geo.longitude) throw new Error('Could not detect location.');
    fetchAndRender(geo.latitude, geo.longitude, `${geo.city || 'Your Area'} (Auto)`);
  } catch (e) {
    statusEl.textContent = `Auto-detect failed: ${e.message}`;
  }
}
