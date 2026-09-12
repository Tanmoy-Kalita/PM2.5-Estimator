"""
PM2.5 Estimation - Streamlit Frontend
- Integrated single autocomplete search box
- Real-time = current day's live data
- Clear data source attribution
Run with: streamlit run pm25_app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import warnings
import io
from datetime import datetime, timezone
warnings.filterwarnings('ignore')

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PM2.5 Estimator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0d1117; color: #e6edf3; }

section[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #30363d;
}
section[data-testid="stSidebar"] * { color: #e6edf3 !important; }

/* Make search text input and selectbox look like one widget */
div[data-testid="stTextInput"] input {
    border-radius: 8px 8px 0px 0px !important;
    border-bottom: none !important;
    background: #1c2333 !important;
    color: #e6edf3 !important;
    border-color: #30363d !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #58a6ff !important;
    box-shadow: none !important;
}
/* Selectbox that appears below search input */
.search-dropdown div[data-baseweb="select"] > div {
    border-radius: 0px 0px 8px 8px !important;
    border-top: 1px solid #30363d !important;
    background: #1c2333 !important;
    margin-top: -2px;
}
.search-dropdown div[data-baseweb="select"] > div:focus-within {
    border-color: #58a6ff !important;
}

.main-header {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem; font-weight: 700;
    color: #58a6ff; letter-spacing: -1px;
    line-height: 1.1; margin-bottom: 0.2rem;
}
.main-sub {
    font-size: 0.95rem; color: #8b949e;
    font-weight: 300; margin-bottom: 1.5rem;
}
.city-badge {
    display: inline-block;
    background: linear-gradient(135deg, #1f6feb, #388bfd);
    color: white; font-family: 'Space Mono', monospace;
    font-size: 0.75rem; padding: 4px 12px;
    border-radius: 20px; margin-bottom: 1rem;
    letter-spacing: 1px; text-transform: uppercase;
}
.source-badge-realtime {
    display: inline-block;
    background: linear-gradient(135deg, #238636, #2ea043);
    color: white; font-family: 'Space Mono', monospace;
    font-size: 0.72rem; padding: 3px 10px;
    border-radius: 20px; margin-left: 8px; letter-spacing: 1px;
}
.source-badge-upload {
    display: inline-block;
    background: linear-gradient(135deg, #9e6a03, #d29922);
    color: white; font-family: 'Space Mono', monospace;
    font-size: 0.72rem; padding: 3px 10px;
    border-radius: 20px; margin-left: 8px; letter-spacing: 1px;
}
.metric-card {
    background: #161b22; border: 1px solid #30363d;
    border-radius: 12px; padding: 1.2rem 1.5rem;
    text-align: center; transition: border-color 0.2s;
}
.metric-card:hover { border-color: #58a6ff; }
.metric-card .metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem; font-weight: 700; color: #58a6ff;
}
.metric-card .metric-label {
    font-size: 0.8rem; color: #8b949e;
    text-transform: uppercase; letter-spacing: 1px; margin-top: 4px;
}
/* Live reading hero card */
.live-card {
    background: linear-gradient(135deg, #0d2137, #0d1117);
    border: 1px solid #1f6feb;
    border-radius: 16px; padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
}
.live-card .live-value {
    font-family: 'Space Mono', monospace;
    font-size: 3.5rem; font-weight: 700; color: #58a6ff;
    line-height: 1;
}
.live-card .live-label {
    font-size: 0.85rem; color: #8b949e;
    text-transform: uppercase; letter-spacing: 2px;
    margin-top: 4px;
}
.live-card .live-meta {
    font-size: 0.78rem; color: #58a6ff;
    margin-top: 8px; font-family: 'Space Mono', monospace;
}
/* Data source attribution box */
.source-attribution {
    background: #161b22;
    border: 1px solid #30363d;
    border-left: 3px solid #58a6ff;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.8rem;
    color: #8b949e;
}
.source-attribution a { color: #58a6ff; text-decoration: none; }
.source-attribution a:hover { text-decoration: underline; }
.source-attribution .src-title {
    color: #e6edf3; font-weight: 600;
    font-size: 0.82rem; margin-bottom: 3px;
}
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 1rem; color: #58a6ff;
    text-transform: uppercase; letter-spacing: 2px;
    border-bottom: 1px solid #30363d;
    padding-bottom: 0.5rem; margin-bottom: 1rem; margin-top: 1.5rem;
}
.feature-tag {
    display: inline-block;
    background: #1c2333; border: 1px solid #30363d;
    color: #8b949e; font-size: 0.72rem;
    padding: 2px 8px; border-radius: 6px; margin: 2px;
    font-family: 'Space Mono', monospace;
}
.aqi-pill {
    display: inline-block; padding: 4px 14px;
    border-radius: 20px; font-size: 0.82rem;
    font-weight: 700; font-family: 'Space Mono', monospace;
}
.aqi-good      { background:#00e400; color:#000; }
.aqi-moderate  { background:#ffff00; color:#000; }
.aqi-sensitive { background:#ff7e00; color:#fff; }
.aqi-unhealthy { background:#ff0000; color:#fff; }
.aqi-very      { background:#8f3f97; color:#fff; }
.aqi-hazardous { background:#7e0023; color:#fff; }
.stButton > button {
    background: linear-gradient(135deg, #1f6feb, #388bfd);
    color: white; border: none; border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem; padding: 0.6rem 2rem;
    width: 100%; transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }
.stTabs [data-baseweb="tab-list"] {
    background: #161b22; border-radius: 8px; gap: 4px; padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; color: #8b949e; border-radius: 6px;
    font-family: 'Space Mono', monospace; font-size: 0.78rem; letter-spacing: 1px;
}
.stTabs [aria-selected="true"] { background: #1f6feb !important; color: white !important; }
hr { border-color: #30363d; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
AQI_BREAKPOINTS = [
    (0.0,   12.0,   "Good",                           "aqi-good"),
    (12.1,  35.4,   "Moderate",                       "aqi-moderate"),
    (35.5,  55.4,   "Unhealthy for Sensitive Groups",  "aqi-sensitive"),
    (55.5,  150.4,  "Unhealthy",                      "aqi-unhealthy"),
    (150.5, 250.4,  "Very Unhealthy",                 "aqi-very"),
    (250.5, 9999,   "Hazardous",                      "aqi-hazardous"),
]
ALL_FEATURES = ['NO2', 'SO2', 'CO', 'O3', 'Optical_Depth_047',
                'temperature_2m', 'RelativeHumidity', 'WindSpeed']
TARGET = 'PM2.5'

BEST_PARAMS = {
    'RF':       dict(n_estimators=200, max_depth=20, min_samples_split=2,
                     min_samples_leaf=1, random_state=42),
    'XGBoost':  dict(n_estimators=200, max_depth=7, learning_rate=0.1,
                     subsample=0.8, colsample_bytree=0.8, random_state=42),
    'SVM':      dict(C=10, gamma=0.1, epsilon=0.1, kernel='rbf'),
    'KNN':      dict(n_neighbors=5, weights='distance', algorithm='auto'),
    'LightGBM': dict(n_estimators=200, max_depth=7, learning_rate=0.1,
                     num_leaves=31, random_state=42, verbose=-1),
    'CatBoost': dict(iterations=200, depth=7, learning_rate=0.1,
                     random_state=42, verbose=0),
}

# ─── AQI helpers ─────────────────────────────────────────────────────────────
def pm25_to_aqi(val):
    for lo, hi, label, css in AQI_BREAKPOINTS:
        if lo <= val <= hi:
            return label, css
    return "Hazardous", "aqi-hazardous"

def aqi_pill(val):
    label, css = pm25_to_aqi(val)
    return f'<span class="aqi-pill {css}">{label}</span>'

# ─── Location Search (Nominatim) ─────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def search_locations(query: str):
    if not query or len(query.strip()) < 2:
        return []
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={'q': query, 'format': 'json', 'limit': 7, 'addressdetails': 1},
            headers={'User-Agent': 'PM25-Estimator-App'},
            timeout=8
        )
        resp.raise_for_status()
        out = []
        for r in resp.json():
            parts = r['display_name'].split(',')
            short = parts[0].strip() + ', ' + parts[-1].strip()
            out.append({
                'display_name': r['display_name'],
                'short_name':   short,
                'lat': float(r['lat']),
                'lon': float(r['lon']),
            })
        return out
    except Exception:
        return []

# ─── Real-Time Data (Current reading + 1 year history for model training) ────
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_realtime_data(lat: float, lon: float):
    """
    Fetch CURRENT day's live reading + 1 year of historical data for training.
    
    APIs used:
      - Live / recent (last 92 days):  Open-Meteo Air Quality + Forecast API
      - Historical (beyond 92 days):   Open-Meteo Archive API
      Together they provide ~1 year of daily data for better model training.
    Returns: (today_info dict, training_df DataFrame)
    """
    from datetime import date, timedelta

    today      = date.today()
    # Historical window: 1 year back
    hist_start = today - timedelta(days=365)
    # Archive covers up to ~5 days before today; recent API covers the rest
    archive_end   = today - timedelta(days=6)
    recent_start  = archive_end + timedelta(days=1)

    start_str  = hist_start.strftime('%Y-%m-%d')
    arch_end_s = archive_end.strftime('%Y-%m-%d')
    today_str  = today.strftime('%Y-%m-%d')

    fetch_time   = datetime.now(timezone.utc).strftime('%d %b %Y, %H:%M UTC')

    # ── Helper: fetch air quality for a date range ────────────────────────
    def fetch_aq(start, end):
        r = requests.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={
                'latitude': lat, 'longitude': lon, 'timezone': 'auto',
                'start_date': start, 'end_date': end,
                'hourly': 'pm2_5,nitrogen_dioxide,sulphur_dioxide,'
                          'carbon_monoxide,ozone,aerosol_optical_depth',
            }, timeout=60)
        r.raise_for_status()
        h = r.json()['hourly']
        return pd.DataFrame({
            'datetime':          pd.to_datetime(h['time']),
            'PM2.5':             h['pm2_5'],
            'NO2':               h['nitrogen_dioxide'],
            'SO2':               h['sulphur_dioxide'],
            'CO':                h['carbon_monoxide'],
            'O3':                h['ozone'],
            'Optical_Depth_047': h['aerosol_optical_depth'],
        })

    # ── Helper: fetch weather from archive API (handles >92 days) ────────
    def fetch_wx_archive(start, end):
        r = requests.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                'latitude': lat, 'longitude': lon, 'timezone': 'auto',
                'start_date': start, 'end_date': end,
                'hourly': 'temperature_2m,relativehumidity_2m,windspeed_10m',
            }, timeout=60)
        r.raise_for_status()
        h = r.json()['hourly']
        return pd.DataFrame({
            'datetime':         pd.to_datetime(h['time']),
            'temperature_2m':   h['temperature_2m'],
            'RelativeHumidity': h['relativehumidity_2m'],
            'WindSpeed':        h['windspeed_10m'],
        })

    # ── Helper: fetch recent weather from forecast API ────────────────────
    def fetch_wx_recent():
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                'latitude': lat, 'longitude': lon, 'timezone': 'auto',
                'past_days': 7, 'forecast_days': 1,
                'hourly': 'temperature_2m,relativehumidity_2m,windspeed_10m',
            }, timeout=30)
        r.raise_for_status()
        h = r.json()['hourly']
        tz = r.json().get('timezone', 'UTC')
        return pd.DataFrame({
            'datetime':         pd.to_datetime(h['time']),
            'temperature_2m':   h['temperature_2m'],
            'RelativeHumidity': h['relativehumidity_2m'],
            'WindSpeed':        h['windspeed_10m'],
        }), tz

    # ── Fetch all data ────────────────────────────────────────────────────
    # Air quality: full 1 year range
    df_aq_hist   = fetch_aq(start_str, arch_end_s)
    df_aq_recent = fetch_aq(recent_start.strftime('%Y-%m-%d'), today_str)
    df_aq        = pd.concat([df_aq_hist, df_aq_recent], ignore_index=True)
    df_aq        = df_aq.drop_duplicates(subset='datetime').sort_values('datetime')

    # Weather: archive for old data, forecast API for recent
    df_wx_hist          = fetch_wx_archive(start_str, arch_end_s)
    df_wx_recent, tz_str = fetch_wx_recent()
    df_wx               = pd.concat([df_wx_hist, df_wx_recent], ignore_index=True)
    df_wx               = df_wx.drop_duplicates(subset='datetime').sort_values('datetime')

    # ── Merge hourly ──────────────────────────────────────────────────────
    df = pd.merge(df_aq, df_wx, on='datetime', how='inner')

    # ── Today's live reading ──────────────────────────────────────────────
    df_today       = df[df['datetime'].dt.date == today].copy()
    df_valid_today = df_today.dropna(subset=['PM2.5'])
    if len(df_valid_today) == 0:
        df_valid_today = df.dropna(subset=['PM2.5'])

    latest_row  = df_valid_today.iloc[-1]
    today_info  = {
        'pm25':        round(latest_row['PM2.5'],          2) if pd.notna(latest_row['PM2.5'])          else None,
        'temperature': round(latest_row['temperature_2m'], 1) if pd.notna(latest_row['temperature_2m']) else None,
        'humidity':    round(latest_row['RelativeHumidity'],1) if pd.notna(latest_row['RelativeHumidity']) else None,
        'wind_speed':  round(latest_row['WindSpeed'],      1) if pd.notna(latest_row['WindSpeed'])      else None,
        'time':        latest_row['datetime'].strftime('%d %b %Y, %H:%M'),
        'fetch_time':  fetch_time,
        'timezone':    tz_str,
    }

    # ── Daily averages for model training (full 1 year) ───────────────────
    df['Date'] = df['datetime'].dt.date
    daily = df.groupby('Date').mean(numeric_only=True).reset_index()
    daily['Date'] = pd.to_datetime(daily['Date'])
    daily = daily.dropna(subset=['PM2.5'])

    for col in ALL_FEATURES + [TARGET]:
        if daily[col].isnull().sum() > 0:
            daily[col] = daily[col].interpolate(method='linear', limit_direction='both')

    # Note: Open-Meteo returns gas concentrations in µg/m³ (surface level).
    # We keep the raw µg/m³ values — StandardScaler normalizes them during training.
    # No unit conversion needed; models only require internally consistent values.

    return today_info, daily.reset_index(drop=True)

# ─── CSV Loader ───────────────────────────────────────────────────────────────
def load_csv_data(uploaded_file) -> pd.DataFrame:
    df = pd.read_csv(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
    for col in ALL_FEATURES + [TARGET]:
        if col in df.columns and df[col].isnull().sum() > 0:
            df[col] = df[col].interpolate(method='linear', limit_direction='both')
    return df

# ─── ML Libraries ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_libs():
    from sklearn.model_selection import train_test_split, KFold
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import r2_score, mean_squared_error, f1_score
    from sklearn.ensemble import (RandomForestRegressor, BaggingRegressor,
                                   VotingRegressor, StackingRegressor)
    from sklearn.svm import SVR
    from sklearn.neighbors import KNeighborsRegressor
    from sklearn.linear_model import Ridge
    from xgboost import XGBRegressor
    from lightgbm import LGBMRegressor
    from catboost import CatBoostRegressor
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, LSTM, Dropout
    from tensorflow.keras.optimizers import Adam
    from tensorflow.keras.callbacks import EarlyStopping
    import tensorflow as tf
    return locals()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## PM2.5 Estimator")
    st.markdown("---")

    st.markdown("### Data Source")
    data_source = st.radio(
        "Choose how to load data",
        ["Real-Time Data", "Upload CSV File"],
        index=0
    )
    st.markdown("---")

    # ── REAL-TIME: Integrated search ──────────────────────────────────────
    if data_source == "Real-Time Data":
        st.markdown("### Search Location")
        st.caption("Type any city, district, region or country")

        # Single text input — query triggers autocomplete
        search_query = st.text_input(
            "Search",
            value=st.session_state.get('last_query', ''),
            placeholder="e.g. Delhi, Tokyo, New York...",
            label_visibility="collapsed",
            key="loc_search"
        )

        selected_location = st.session_state.get('selected_location', None)

        # Live suggestions dropdown — appears right below as extension of search
        if search_query and len(search_query.strip()) >= 2:
            if search_query != st.session_state.get('last_query', ''):
                st.session_state['last_query'] = search_query
                st.session_state.pop('selected_location', None)
                selected_location = None

            suggestions = search_locations(search_query)

            if suggestions:
                option_labels = [s['short_name'] for s in suggestions]
                option_map    = {s['short_name']: s for s in suggestions}

                st.markdown('<div class="search-dropdown">', unsafe_allow_html=True)
                chosen = st.selectbox(
                    "results",
                    ["Select a location ▾"] + option_labels,
                    label_visibility="collapsed",
                    key="loc_dropdown"
                )
                st.markdown('</div>', unsafe_allow_html=True)

                if chosen != "Select a location ▾":
                    selected_location = option_map[chosen]
                    st.session_state['selected_location'] = selected_location
            else:
                st.caption("⚠️ No results found.")

        # Show selected location confirmation
        if selected_location:
            st.markdown(f"""
            <div style="background:#1c2333;border:1px solid #238636;
                        border-radius:8px;padding:8px 12px;margin-top:4px;
                        font-size:0.78rem">
                <span style="color:#3fb950">✓ Selected:</span>
                <span style="color:#e6edf3"> {selected_location['short_name']}</span><br>
                <span style="color:#8b949e;font-family:monospace;font-size:0.72rem">
                {selected_location['lat']:.4f}°N, {selected_location['lon']:.4f}°E</span>
            </div>""", unsafe_allow_html=True)

        # Data source attribution
        st.markdown("""
        <div class="source-attribution" style="margin-top:10px">
            <div class="src-title"> Data Sources</div>
            <b>Air Quality:</b> <a href="https://open-meteo.com/en/docs/air-quality-api" target="_blank">Open-Meteo Air Quality API</a><br>
            <b>Weather (recent):</b> <a href="https://open-meteo.com/en/docs" target="_blank">Open-Meteo Forecast API</a><br>
            <b>Weather (history):</b> <a href="https://open-meteo.com/en/docs/historical-weather-api" target="_blank">Open-Meteo Archive API</a><br>
            <b>Location:</b> <a href="https://nominatim.openstreetmap.org" target="_blank">OpenStreetMap Nominatim</a><br>
            <span style="color:#3fb950">Free · Open data · No API key · 1 year history</span>
        </div>""", unsafe_allow_html=True)

        uploaded_file = None
        display_city  = selected_location['short_name'] if selected_location else "—"

    # ── CSV UPLOAD ────────────────────────────────────────────────────────
    else:
        st.markdown("### City Name")
        csv_city_name = st.text_input("Name (for display)", value="My City",
                                      label_visibility="collapsed",
                                      placeholder="e.g. Delhi, Mumbai...")
        st.markdown("### Upload Dataset")
        uploaded_file = st.file_uploader(
            "Upload CSV File", type=["csv"],
            help="Required: Date, NO2, SO2, CO, O3, Optical_Depth_047, "
                 "temperature_2m, RelativeHumidity, WindSpeed, PM2.5"
        )
        selected_location = None
        display_city      = csv_city_name

    st.markdown("---")

    st.markdown("### Models")
    run_ml    = st.checkbox("ML Models",          value=True)
    run_dl    = st.checkbox("Deep Learning",      value=True)
    run_ens   = st.checkbox("Ensemble Methods",   value=True)
    run_hyb   = st.checkbox("Hybrid Models",      value=True)
    run_kfold = st.checkbox("K-Fold CV (5-Fold)", value=True)

    st.markdown("### DL Settings")
    dl_epochs     = st.slider("Epochs",     10, 200, 100, 10)
    dl_batch_size = st.slider("Batch Size", 16, 128,  32, 16)

    st.markdown("---")

    if data_source == "Real-Time Data":
        load_btn = st.button("Fetch Live Data",
                             disabled=(selected_location is None))
    else:
        load_btn = st.button("Load CSV Data")

    run_btn = st.button("Run Analysis")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="main-header">PM2.5 Concentration Estimator</div>', unsafe_allow_html=True)
st.markdown('<div class="main-sub">Satellite + Meteorological Data · ML · Deep Learning · Ensemble · Hybrid</div>',
            unsafe_allow_html=True)
st.markdown("""
<div style="margin-bottom:1.5rem">
<span class="feature-tag">NO2</span>
<span class="feature-tag">SO2</span>
<span class="feature-tag"> CO</span>
<span class="feature-tag"> O3</span>
<span class="feature-tag"> Aerosol OD</span>
<span class="feature-tag"> Temperature</span>
<span class="feature-tag"> Humidity</span>
<span class="feature-tag"> Wind Speed</span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
if load_btn:
    if data_source == "Real-Time Data":
        if not selected_location:
            st.error("Please search and select a location first.")
            st.stop()
        with st.spinner(f" Fetching live data for {selected_location['short_name']}..."):
            try:
                today_info, df = fetch_realtime_data(
                    selected_location['lat'], selected_location['lon'])
                st.session_state.update({
                    'df':           df,
                    'today_info':   today_info,
                    'display_name': selected_location['short_name'],
                    'full_name':    selected_location['display_name'],
                    'lat':          selected_location['lat'],
                    'lon':          selected_location['lon'],
                    'data_source':  'realtime',
                    'data_loaded':  True,
                })
                st.session_state.pop('ran', None)
                st.success(
                    f"✅ Live data fetched for **{selected_location['short_name']}** "
                    f"· **{len(df)} days** (1 year) for model training · "
                    f"Latest reading: **{today_info['pm25']} µg/m³** "
                    f"at {today_info['time']}"
                )
            except Exception as e:
                st.error(f"Failed to fetch data: {e}")
                st.stop()
    else:
        if uploaded_file is None:
            st.error("Please upload a CSV file first.")
            st.stop()
        try:
            df = load_csv_data(uploaded_file)
            missing = [c for c in ALL_FEATURES + [TARGET] if c not in df.columns]
            if missing:
                st.error(f"CSV missing columns: {missing}")
                st.stop()
            st.session_state.update({
                'df':           df,
                'today_info':   None,
                'display_name': csv_city_name,
                'full_name':    csv_city_name,
                'data_source':  'csv',
                'data_loaded':  True,
            })
            st.session_state.pop('ran', None)
            st.success(f"✅ Loaded **{len(df)} records** from CSV for **{csv_city_name}**!")
        except Exception as e:
            st.error(f"Failed to load CSV: {e}")
            st.stop()

# ─── Landing Page ─────────────────────────────────────────────────────────────
if 'data_loaded' not in st.session_state:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-title"> Real-Time Mode</div>', unsafe_allow_html=True)
        st.markdown("""<div class="metric-card">
            <p style="color:#e6edf3;font-size:0.9rem;margin-bottom:0.8rem">
            Type any city or region in the sidebar — a <b>dropdown</b> appears
            with matching locations. Select one and click <b>Fetch Live Data</b>
            to get <b>current readings</b> directly from Open-Meteo API.
            </p>
            <p style="color:#3fb950;font-size:0.8rem">
            ✓ Free · ✓ No API key · ✓ Any location worldwide · ✓ Current data
            </p></div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Data Sources</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="source-attribution">
            <div class="src-title"> Air Quality — Open-Meteo Air Quality API</div>
            PM2.5, NO2, SO2, CO, O3, Aerosol Optical Depth<br>
            <a href="https://open-meteo.com/en/docs/air-quality-api">open-meteo.com/en/docs/air-quality-api</a>
        </div>
        <div class="source-attribution">
            <div class="src-title"> Weather — Open-Meteo Weather API</div>
            Temperature, Relative Humidity, Wind Speed<br>
            <a href="https://open-meteo.com/en/docs">open-meteo.com/en/docs</a>
        </div>
        <div class="source-attribution">
            <div class="src-title"> Geocoding — OpenStreetMap Nominatim</div>
            Location search & coordinates<br>
            <a href="https://nominatim.openstreetmap.org">nominatim.openstreetmap.org</a>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="section-title"> Upload CSV Mode</div>', unsafe_allow_html=True)
        st.markdown("""<div class="metric-card">
            <p style="color:#e6edf3;font-size:0.9rem;margin-bottom:0.8rem">
            Upload your own historical dataset CSV.
            Ideal for research or offline analysis.
            </p>
            <p style="color:#d29922;font-size:0.8rem">
            ✓ Your own data · ✓ Full control · ✓ Works offline
            </p></div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">Required CSV Columns</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame({
            'Column':  ['Date','NO2','SO2','CO','O3','Optical_Depth_047',
                        'temperature_2m','RelativeHumidity','WindSpeed','PM2.5'],
            'Format':  ['DD-MM-YYYY','mol/m²','mol/m²','mol/m²','mol/m²',
                        'dimensionless','°C','%','km/h','µg/m³'],
        }), use_container_width=True, hide_index=True)

        st.markdown('<div class="section-title">AQI Breakpoints (US EPA)</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame([
            {"Category": "Good",                           "PM2.5": "0.0 – 12.0 µg/m³"},
            {"Category": "Moderate",                       "PM2.5": "12.1 – 35.4 µg/m³"},
            {"Category": "Unhealthy for Sensitive Groups", "PM2.5": "35.5 – 55.4 µg/m³"},
            {"Category": "Unhealthy",                      "PM2.5": "55.5 – 150.4 µg/m³"},
            {"Category": "Very Unhealthy",                 "PM2.5": "150.5 – 250.4 µg/m³"},
            {"Category": "Hazardous",                      "PM2.5": "250.5+ µg/m³"},
        ]), use_container_width=True, hide_index=True)
    st.stop()

# ─── Loaded state ─────────────────────────────────────────────────────────────
df           = st.session_state['df']
display_name = st.session_state.get('display_name', 'Unknown')
data_src_tag = st.session_state.get('data_source', 'csv')
today_info   = st.session_state.get('today_info', None)
src_badge    = ('<span class="source-badge-realtime"> Real-Time</span>'
                if data_src_tag == 'realtime'
                else '<span class="source-badge-upload"> CSV Upload</span>')

st.markdown(
    f'<div class="city-badge"> {display_name}</div>{src_badge}',
    unsafe_allow_html=True)

# ── Live current reading (real-time mode only) ─────────────────────────────
if data_src_tag == 'realtime' and today_info and today_info['pm25'] is not None:
    aqi_label, aqi_css = pm25_to_aqi(today_info['pm25'])
    c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 2])
    with c1:
        st.markdown(f"""
        <div class="live-card">
            <div class="live-label">Current PM2.5 Reading</div>
            <div class="live-value">{today_info['pm25']}<span style="font-size:1.2rem;color:#8b949e"> µg/m³</span></div>
            <div style="margin-top:8px">{aqi_pill(today_info['pm25'])}</div>
            <div class="live-meta"> {today_info['time']} ({today_info['timezone']})</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-value" style="font-size:1.4rem">{today_info["temperature"]}°</div>
            <div class="metric-label">Temperature</div></div>''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-value" style="font-size:1.4rem">{today_info["humidity"]}%</div>
            <div class="metric-label">Humidity</div></div>''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-value" style="font-size:1.4rem">{today_info["wind_speed"]}</div>
            <div class="metric-label">Wind km/h</div></div>''', unsafe_allow_html=True)
    with c5:
        # Data source attribution inline
        st.markdown(f"""
        <div class="source-attribution" style="height:100%;box-sizing:border-box">
            <div class="src-title"> Data Sources</div>
             <a href="https://open-meteo.com/en/docs/air-quality-api" target="_blank">Open-Meteo Air Quality API</a><br>
             <a href="https://open-meteo.com/en/docs" target="_blank">Open-Meteo Weather API</a><br>
             <a href="https://nominatim.openstreetmap.org" target="_blank">OpenStreetMap Nominatim</a><br>
            <span style="color:#3fb950;font-size:0.72rem">
            Fetched: {today_info['fetch_time']}</span>
        </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab_data, tab_results, tab_plots, tab_aqi, tab_kfold = st.tabs([
    " Data Overview", " Model Results", " Visualizations",
    " AQI Analysis",  " K-Fold CV"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DATA OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab_data:
    src_label = "Live Data" if data_src_tag == 'realtime' else "Uploaded CSV"
    st.markdown(f'<div class="section-title">{src_label} Summary</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-value">{len(df):,}</div>
            <div class="metric-label">Days of Data</div></div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-value">{df[TARGET].mean():.1f}</div>
            <div class="metric-label">Mean PM2.5 (µg/m³)</div></div>''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-value">{df[TARGET].max():.1f}</div>
            <div class="metric-label">Max PM2.5 (µg/m³)</div></div>''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''<div class="metric-card">
            <div class="metric-value" style="font-size:1rem">{aqi_pill(df[TARGET].mean())}</div>
            <div class="metric-label">Avg AQI Category</div></div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if 'Date' in df.columns:
        d_min = pd.to_datetime(df['Date']).min().strftime('%d %b %Y')
        d_max = pd.to_datetime(df['Date']).max().strftime('%d %b %Y')
        st.markdown(f"**Training Data Period:** {d_min} → {d_max}")
    if data_src_tag == 'realtime':
        st.markdown(f"**Coordinates:** `{st.session_state.get('lat',''):.4f}°N, "
                    f"{st.session_state.get('lon',''):.4f}°E`")

    # Attribution in data tab
    if data_src_tag == 'realtime':
        st.markdown("""
        <div class="source-attribution">
            <div class="src-title"> About this data</div>
            Air quality (PM2.5, NO2, SO2, CO, O3, Aerosol OD) from
            <a href="https://open-meteo.com/en/docs/air-quality-api">Open-Meteo Air Quality API</a> ·
            Weather (Temperature, Humidity, Wind) from
            <a href="https://open-meteo.com/en/docs">Open-Meteo Weather API</a> ·
            Location geocoding by <a href="https://nominatim.openstreetmap.org">OpenStreetMap Nominatim</a> ·
            <span style="color:#3fb950">All sources are free and open · No API key required</span>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Statistics</div>', unsafe_allow_html=True)
    st.dataframe(df[ALL_FEATURES + [TARGET]].describe().round(4), use_container_width=True)

    st.markdown('<div class="section-title">Data Preview</div>', unsafe_allow_html=True)
    st.dataframe(df.head(60), use_container_width=True)

    st.markdown('<div class="section-title">PM2.5 Time Series</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 4), facecolor='#0d1117')
    ax.set_facecolor('#0d1117')
    date_col = pd.to_datetime(df['Date']) if 'Date' in df.columns else df.index
    ax.plot(date_col, df[TARGET], color='#58a6ff', linewidth=1.2, alpha=0.9)
    ax.fill_between(date_col, df[TARGET], alpha=0.12, color='#58a6ff')
    # Mark today's live reading
    if data_src_tag == 'realtime' and today_info and today_info['pm25']:
        ax.axhline(y=today_info['pm25'], color='#3fb950', linestyle='--',
                   linewidth=1, alpha=0.7, label=f"Current: {today_info['pm25']} µg/m³")
    for _, hi, _, _ in AQI_BREAKPOINTS[1:4]:
        ax.axhline(y=hi, linestyle='--', linewidth=0.5, alpha=0.25, color='#8b949e')
    ax.set_xlabel('Date', color='#8b949e')
    ax.set_ylabel('PM2.5 (µg/m³)', color='#8b949e')
    ax.set_title(f'PM2.5 — {display_name}', color='#e6edf3', fontsize=11)
    ax.tick_params(colors='#8b949e')
    if data_src_tag == 'realtime' and today_info:
        ax.legend(facecolor='#161b22', edgecolor='#30363d', labelcolor='#8b949e', fontsize=8)
    for sp in ax.spines.values(): sp.set_edgecolor('#30363d')
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close()

    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False)
    st.download_button("⬇  Download Data as CSV", csv_buf.getvalue(),
                       file_name=f"{display_name.replace(' ','_')}_data.csv",
                       mime="text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# RUN MODELS
# ══════════════════════════════════════════════════════════════════════════════
if run_btn:
    if 'data_loaded' not in st.session_state:
        st.error("Please load data first.")
        st.stop()

    libs = load_libs()
    train_test_split = libs['train_test_split']
    StandardScaler   = libs['StandardScaler']
    r2_score         = libs['r2_score']
    mse_fn           = libs['mean_squared_error']
    f1_score         = libs['f1_score']
    KFold            = libs['KFold']
    tf               = libs['tf']
    np.random.seed(42); tf.random.set_seed(42)

    X = df[ALL_FEATURES].copy()
    y = df[TARGET].copy()
    if len(X) < 20:
        st.error("Not enough data. Please fetch more data or check your CSV.")
        st.stop()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=True)
    scaler_X = StandardScaler(); scaler_y = StandardScaler()
    X_train_sc = scaler_X.fit_transform(X_train)
    X_test_sc  = scaler_X.transform(X_test)
    y_train_sc = scaler_y.fit_transform(y_train.values.reshape(-1,1)).flatten()

    def eval_m(yt, yp):
        yp   = np.array(yp).flatten()
        r2   = r2_score(yt, yp)
        rmse = np.sqrt(mse_fn(yt, yp))
        ac   = [pm25_to_aqi(v)[0] for v in np.array(yt).flatten()]
        pc   = [pm25_to_aqi(v)[0] for v in yp]
        f1   = f1_score(ac, pc, average='weighted', zero_division=0)
        return round(r2,4), round(rmse,4), round(f1,4)

    def make_model(name):
        p = BEST_PARAMS[name]
        if name == 'RF':       return libs['RandomForestRegressor'](**p)
        if name == 'XGBoost':  return libs['XGBRegressor'](**p)
        if name == 'SVM':      return libs['SVR'](**p)
        if name == 'KNN':      return libs['KNeighborsRegressor'](**p)
        if name == 'LightGBM': return libs['LGBMRegressor'](**p)
        if name == 'CatBoost': return libs['CatBoostRegressor'](**p)

    es = libs['EarlyStopping'](monitor='loss', patience=10, restore_best_weights=True)

    def create_snn(d):
        m = libs['Sequential']([
            libs['Dense'](64, activation='relu', input_dim=d),
            libs['Dropout'](0.2), libs['Dense'](32, activation='relu'),
            libs['Dropout'](0.2), libs['Dense'](16, activation='relu'),
            libs['Dense'](1, activation='linear')
        ])
        m.compile(optimizer=libs['Adam'](0.001), loss='mse'); return m

    def create_lstm_model(d):
        m = libs['Sequential']([
            libs['LSTM'](50, activation='tanh', input_shape=(1,d), return_sequences=True),
            libs['Dropout'](0.2), libs['LSTM'](25, activation='tanh'),
            libs['Dropout'](0.2), libs['Dense'](12, activation='relu'),
            libs['Dense'](1, activation='linear')
        ])
        m.compile(optimizer=libs['Adam'](0.001), loss='mse'); return m

    all_results = {}; pred_store = {}

    if run_ml:
        with st.spinner("Training ML Models..."):
            prog = st.progress(0)
            for i, name in enumerate(['RF','XGBoost','SVM','KNN','LightGBM','CatBoost']):
                m = make_model(name); m.fit(X_train, y_train)
                yp = m.predict(X_test); pred_store[name] = yp
                all_results[name] = dict(zip(['R2','RMSE','F1'], eval_m(y_test, yp)))
                prog.progress((i+1)/6)

    if run_dl:
        X_tr_l = X_train_sc.reshape(X_train_sc.shape[0], 1, X_train_sc.shape[1])
        X_te_l = X_test_sc.reshape(X_test_sc.shape[0],   1, X_test_sc.shape[1])
        with st.spinner("Training SNN..."):
            s = create_snn(X_train_sc.shape[1])
            s.fit(X_train_sc, y_train_sc, epochs=dl_epochs, batch_size=dl_batch_size, callbacks=[es], verbose=0)
            yp = scaler_y.inverse_transform(s.predict(X_test_sc, verbose=0))
            pred_store['SNN'] = yp; all_results['SNN'] = dict(zip(['R2','RMSE','F1'], eval_m(y_test, yp)))
        with st.spinner("Training LSTM..."):
            lm = create_lstm_model(X_train_sc.shape[1])
            lm.fit(X_tr_l, y_train_sc, epochs=dl_epochs, batch_size=dl_batch_size, callbacks=[es], verbose=0)
            yp = scaler_y.inverse_transform(lm.predict(X_te_l, verbose=0))
            pred_store['LSTM'] = yp; all_results['LSTM'] = dict(zip(['R2','RMSE','F1'], eval_m(y_test, yp)))

    if run_ens:
        with st.spinner("Training Ensemble Methods..."):
            for ename, estimator in [
                ('Bagging',  libs['BaggingRegressor'](estimator=libs['RandomForestRegressor'](**BEST_PARAMS['RF']), n_estimators=10, random_state=42)),
                ('Voting',   libs['VotingRegressor'](estimators=[('rf', libs['RandomForestRegressor'](**BEST_PARAMS['RF'])),('xgb', libs['XGBRegressor'](**BEST_PARAMS['XGBoost'])),('lgbm', libs['LGBMRegressor'](**BEST_PARAMS['LightGBM']))])),
                ('Stacking', libs['StackingRegressor'](estimators=[('rf',libs['RandomForestRegressor'](**BEST_PARAMS['RF'])),('xgb',libs['XGBRegressor'](**BEST_PARAMS['XGBoost'])),('lgbm',libs['LGBMRegressor'](**BEST_PARAMS['LightGBM'])),('cat',libs['CatBoostRegressor'](**BEST_PARAMS['CatBoost'])),('knn',libs['KNeighborsRegressor'](**BEST_PARAMS['KNN']))], final_estimator=libs['Ridge'](), cv=5)),
            ]:
                estimator.fit(X_train, y_train); yp = estimator.predict(X_test)
                pred_store[ename] = yp; all_results[ename] = dict(zip(['R2','RMSE','F1'], eval_m(y_test, yp)))

            Xb_tr,Xb_val,yb_tr,yb_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)
            btr,bte=[],[]
            for _,mdl in [('rf',libs['RandomForestRegressor'](**BEST_PARAMS['RF'])),('xgb',libs['XGBRegressor'](**BEST_PARAMS['XGBoost'])),('lgbm',libs['LGBMRegressor'](**BEST_PARAMS['LightGBM']))]:
                mdl.fit(Xb_tr,yb_tr); btr.append(mdl.predict(Xb_val).reshape(-1,1)); bte.append(mdl.predict(X_test).reshape(-1,1))
            meta=libs['Ridge'](); meta.fit(np.hstack(btr),yb_val); yp=meta.predict(np.hstack(bte))
            pred_store['Blending']=yp; all_results['Blending']=dict(zip(['R2','RMSE','F1'],eval_m(y_test,yp)))

    if run_hyb:
        def train_hybrid(base):
            base.fit(X_train,y_train)
            Xh_tr=np.hstack([X_train_sc,base.predict(X_train).reshape(-1,1)]).reshape(-1,1,X_train_sc.shape[1]+1)
            Xh_te=np.hstack([X_test_sc,base.predict(X_test).reshape(-1,1)]).reshape(-1,1,X_test_sc.shape[1]+1)
            m=libs['Sequential']([libs['LSTM'](50,activation='tanh',input_shape=(1,Xh_tr.shape[2])),libs['Dropout'](0.2),libs['Dense'](25,activation='relu'),libs['Dense'](1,activation='linear')])
            m.compile(optimizer=libs['Adam'](0.001),loss='mse')
            m.fit(Xh_tr,y_train_sc,epochs=dl_epochs,batch_size=dl_batch_size,callbacks=[es],verbose=0)
            return scaler_y.inverse_transform(m.predict(Xh_te,verbose=0))
        for hname, hbase in [('RF-LSTM',libs['RandomForestRegressor'](**BEST_PARAMS['RF'])),('XGBoost-LSTM',libs['XGBRegressor'](**BEST_PARAMS['XGBoost'])),('SVM-LSTM',libs['SVR'](**BEST_PARAMS['SVM']))]:
            with st.spinner(f"Training {hname} Hybrid..."):
                yp=train_hybrid(hbase); pred_store[hname]=yp; all_results[hname]=dict(zip(['R2','RMSE','F1'],eval_m(y_test,yp)))

    kfold_results = {}
    if run_kfold:
        kf = KFold(n_splits=5, shuffle=True, random_state=42)
        with st.spinner("Running 5-Fold CV..."):
            for name in ['RF','XGBoost','SVM','KNN','LightGBM','CatBoost']:
                r2s,rmses=[],[]
                for ti,vi in kf.split(X):
                    m=make_model(name); m.fit(X.iloc[ti],y.iloc[ti]); yp=m.predict(X.iloc[vi])
                    r2s.append(r2_score(y.iloc[vi],yp)); rmses.append(np.sqrt(mse_fn(y.iloc[vi],yp)))
                kfold_results[name]={'Mean R2':round(np.mean(r2s),4),'Std R2':round(np.std(r2s),4),'Mean RMSE':round(np.mean(rmses),4)}

    st.session_state.update({'all_results':all_results,'pred_store':pred_store,
                              'kfold_results':kfold_results,'y_test':y_test,
                              'X_test_index': X_test.index.tolist(),
                              'ran':True})
    st.success(f"✅ Analysis complete for **{display_name}**!")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — MODEL RESULTS
# ══════════════════════════════════════════════════════════════════════════════
with tab_results:
    if 'ran' not in st.session_state:
        st.info("Click **Run Analysis** after loading data.")
    else:
        all_results = st.session_state['all_results']
        best_name   = max(all_results, key=lambda k: all_results[k]['R2'])

        st.markdown('<div class="section-title">Best Model</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'''<div class="metric-card">
                <div class="metric-value" style="font-size:1.2rem">{best_name}</div>
                <div class="metric-label">Best Model</div></div>''', unsafe_allow_html=True)
        with c2:
            st.markdown(f'''<div class="metric-card">
                <div class="metric-value">{all_results[best_name]["R2"]}</div>
                <div class="metric-label">R² Score</div></div>''', unsafe_allow_html=True)
        with c3:
            st.markdown(f'''<div class="metric-card">
                <div class="metric-value">{all_results[best_name]["RMSE"]}</div>
                <div class="metric-label">RMSE (µg/m³)</div></div>''', unsafe_allow_html=True)

        st.markdown('<div class="section-title">All Model Results</div>', unsafe_allow_html=True)
        rows = [{'Model':m,'R²':v['R2'],'RMSE':v['RMSE'],'F1-Score':v['F1']} for m,v in all_results.items()]
        res_df = pd.DataFrame(rows).sort_values('R²',ascending=False).reset_index(drop=True)
        res_df.index += 1
        st.dataframe(res_df, use_container_width=True)

        csv_buf = io.StringIO(); res_df.to_csv(csv_buf, index=False)
        st.download_button("⬇  Download Results CSV", csv_buf.getvalue(),
                           file_name=f"{display_name.replace(' ','_')}_results.csv", mime="text/csv")

        st.markdown('<div class="section-title">R² Comparison</div>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(12,4), facecolor='#0d1117')
        ax.set_facecolor('#0d1117')
        models=res_df['Model'].tolist(); r2_vals=res_df['R²'].tolist()
        bar_colors=['#3fb950' if v>=0.8 else '#d29922' if v>=0.6 else '#f85149' for v in r2_vals]
        bars=ax.bar(models,r2_vals,color=bar_colors,edgecolor='#30363d',linewidth=0.5)
        ax.axhline(y=0.8,color='#58a6ff',linestyle='--',linewidth=1,alpha=0.6,label='R²=0.8')
        ax.set_ylim(0,1.1); ax.set_ylabel('R²',color='#8b949e')
        ax.set_title(f'Model R² — {display_name}',color='#e6edf3')
        ax.tick_params(colors='#8b949e'); plt.xticks(rotation=45,ha='right',color='#8b949e')
        for bar,val in zip(bars,r2_vals):
            ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.01,f'{val:.3f}',ha='center',color='#e6edf3',fontsize=8)
        for sp in ax.spines.values(): sp.set_edgecolor('#30363d')
        ax.legend(facecolor='#161b22',edgecolor='#30363d',labelcolor='#8b949e')
        plt.tight_layout(); st.pyplot(fig, use_container_width=True); plt.close()

        # ── Actual vs Estimated PM2.5 Comparison ──────────────────────────
        st.markdown('<div class="section-title">Actual vs Estimated PM2.5 Comparison</div>',
                    unsafe_allow_html=True)

        y_test      = st.session_state['y_test']
        pred_store  = st.session_state['pred_store']
        X_test_idx  = st.session_state.get('X_test_index', [])

        # Model selector for comparison
        comp_model = st.selectbox(
            "Select model for comparison",
            list(pred_store.keys()),
            index=list(pred_store.keys()).index(best_name)
            if best_name in pred_store else 0,
            key="comp_model_select"
        )

        yp_comp = np.array(pred_store[comp_model]).flatten()
        y_actual = np.array(y_test).flatten()

        # Get dates for x-axis if available
        if 'Date' in df.columns and len(X_test_idx) == len(y_actual):
            dates = pd.to_datetime(df['Date']).iloc[X_test_idx].values
            has_dates = True
        else:
            dates = np.arange(len(y_actual))
            has_dates = False

        # Sort by date for clean time series
        sort_idx   = np.argsort(dates)
        dates_s    = dates[sort_idx]
        actual_s   = y_actual[sort_idx]
        predicted_s = yp_comp[sort_idx]

        # ── Time Series comparison plot ────────────────────────────────────
        fig, ax = plt.subplots(figsize=(13, 5), facecolor='#0d1117')
        ax.set_facecolor('#0d1117')
        ax.plot(dates_s, actual_s,    color='#58a6ff', linewidth=1.5,
                alpha=0.9, label='Actual PM2.5',    zorder=3)
        ax.plot(dates_s, predicted_s, color='#f85149', linewidth=1.5,
                alpha=0.85, linestyle='--', label=f'Estimated PM2.5 ({comp_model})', zorder=3)
        ax.fill_between(dates_s, actual_s, predicted_s,
                        alpha=0.08, color='#d29922', label='Difference')
        ax.set_xlabel('Date' if has_dates else 'Sample Index', color='#8b949e')
        ax.set_ylabel('PM2.5 (µg/m³)', color='#8b949e')
        ax.set_title(f'Actual vs Estimated PM2.5 — {display_name}  [{comp_model}]',
                     color='#e6edf3', fontsize=11)
        ax.tick_params(colors='#8b949e')
        ax.legend(facecolor='#161b22', edgecolor='#30363d', labelcolor='#e6edf3', fontsize=9)
        for sp in ax.spines.values(): sp.set_edgecolor('#30363d')
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close()

        # ── Summary stats for comparison ───────────────────────────────────
        diff        = actual_s - predicted_s
        mae         = round(float(np.mean(np.abs(diff))), 4)
        max_over    = round(float(np.max(predicted_s - actual_s)), 2)
        max_under   = round(float(np.min(predicted_s - actual_s)), 2)
        within_10   = round(float(np.mean(np.abs(diff) <= 10) * 100), 1)
        within_20   = round(float(np.mean(np.abs(diff) <= 20) * 100), 1)

        st.markdown('<div class="section-title">Estimation Accuracy Summary</div>',
                    unsafe_allow_html=True)
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        with sc1:
            st.markdown(f'''<div class="metric-card">
                <div class="metric-value" style="font-size:1.4rem">{mae}</div>
                <div class="metric-label">MAE (µg/m³)</div></div>''', unsafe_allow_html=True)
        with sc2:
            st.markdown(f'''<div class="metric-card">
                <div class="metric-value" style="font-size:1.4rem">{all_results[comp_model]["RMSE"]}</div>
                <div class="metric-label">RMSE (µg/m³)</div></div>''', unsafe_allow_html=True)
        with sc3:
            st.markdown(f'''<div class="metric-card">
                <div class="metric-value" style="font-size:1.4rem">{all_results[comp_model]["R2"]}</div>
                <div class="metric-label">R² Score</div></div>''', unsafe_allow_html=True)
        with sc4:
            st.markdown(f'''<div class="metric-card">
                <div class="metric-value" style="font-size:1.4rem">{within_10}%</div>
                <div class="metric-label">Within ±10 µg/m³</div></div>''', unsafe_allow_html=True)
        with sc5:
            st.markdown(f'''<div class="metric-card">
                <div class="metric-value" style="font-size:1.4rem">{within_20}%</div>
                <div class="metric-label">Within ±20 µg/m³</div></div>''', unsafe_allow_html=True)

        # ── Side by side table ─────────────────────────────────────────────
        st.markdown('<div class="section-title">Sample-by-Sample Comparison Table</div>',
                    unsafe_allow_html=True)

        comp_df = pd.DataFrame({
            'Date'            : pd.to_datetime(dates_s).strftime('%d %b %Y') if has_dates else dates_s,
            'Actual PM2.5'    : np.round(actual_s,    2),
            'Estimated PM2.5' : np.round(predicted_s, 2),
            'Difference'      : np.round(diff,        2),
            'Abs Error'       : np.round(np.abs(diff), 2),
            'AQI (Actual)'    : [pm25_to_aqi(v)[0] for v in actual_s],
            'AQI (Estimated)' : [pm25_to_aqi(v)[0] for v in predicted_s],
            'AQI Match'       : ['' if pm25_to_aqi(a)[0] == pm25_to_aqi(p)[0]
                                  else '❌' for a, p in zip(actual_s, predicted_s)],
        })

        st.dataframe(comp_df, use_container_width=True, hide_index=True)

        # Download comparison table
        comp_csv = io.StringIO()
        comp_df.to_csv(comp_csv, index=False)
        st.download_button(
            "  Download Comparison Table",
            comp_csv.getvalue(),
            file_name=f"{display_name.replace(' ','_')}_{comp_model}_comparison.csv",
            mime="text/csv"
        )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab_plots:
    if 'ran' not in st.session_state:
        st.info("Run the analysis to see plots.")
    else:
        y_test=st.session_state['y_test']; pred_store=st.session_state['pred_store']
        all_results=st.session_state['all_results']

        st.markdown('<div class="section-title">Feature Correlation Heatmap</div>', unsafe_allow_html=True)
        fig,ax=plt.subplots(figsize=(10,8),facecolor='#0d1117'); ax.set_facecolor('#0d1117')
        sns.heatmap(df[ALL_FEATURES+[TARGET]].corr(),annot=True,fmt='.2f',cmap='coolwarm',center=0,
                    ax=ax,linewidths=0.3,linecolor='#30363d',annot_kws={'size':8,'color':'white'})
        ax.set_title('Feature Correlation',color='#e6edf3'); ax.tick_params(colors='#e6edf3')
        plt.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close()

        st.markdown('<div class="section-title">Actual vs Predicted</div>', unsafe_allow_html=True)
        chosen=st.selectbox("Select Model",list(pred_store.keys()),index=0)
        yp=np.array(pred_store[chosen]).flatten()
        fig,ax=plt.subplots(figsize=(8,6),facecolor='#0d1117'); ax.set_facecolor('#0d1117')
        ax.scatter(y_test,yp,alpha=0.4,color='#58a6ff',s=20,edgecolors='none')
        mn=min(float(y_test.min()),float(yp.min())); mx=max(float(y_test.max()),float(yp.max()))
        ax.plot([mn,mx],[mn,mx],color='#f85149',linestyle='--',linewidth=1.5,label='Perfect fit')
        ax.set_xlabel('Actual PM2.5 (µg/m³)',color='#8b949e')
        ax.set_ylabel('Predicted PM2.5 (µg/m³)',color='#8b949e')
        ax.set_title(f'{chosen} — R²={all_results[chosen]["R2"]}',color='#e6edf3')
        ax.tick_params(colors='#8b949e')
        for sp in ax.spines.values(): sp.set_edgecolor('#30363d')
        ax.legend(facecolor='#161b22',edgecolor='#30363d',labelcolor='#8b949e')
        plt.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — AQI ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab_aqi:
    if 'ran' not in st.session_state:
        st.info("Run the analysis to see AQI results.")
    else:
        y_test=st.session_state['y_test']; pred_store=st.session_state['pred_store']
        cat_order=["Good","Moderate","Unhealthy for Sensitive Groups","Unhealthy","Very Unhealthy","Hazardous"]
        cat_hex=['#00e400','#ffff00','#ff7e00','#ff0000','#8f3f97','#7e0023']

        st.markdown('<div class="section-title">AQI Distribution (Actual)</div>', unsafe_allow_html=True)
        aqi_s=df[TARGET].apply(lambda v:pm25_to_aqi(v)[0])
        cc=aqi_s.value_counts().reindex([c for c in cat_order if c in aqi_s.unique()])
        fig,ax=plt.subplots(figsize=(10,4),facecolor='#0d1117'); ax.set_facecolor('#0d1117')
        bars=ax.bar(cc.index,cc.values,color=cat_hex[:len(cc)],edgecolor='#30363d',linewidth=0.5)
        ax.set_ylabel('Days',color='#8b949e'); ax.set_title(f'AQI Distribution — {display_name}',color='#e6edf3')
        ax.tick_params(colors='#8b949e'); plt.xticks(rotation=30,ha='right',color='#8b949e')
        for bar,val in zip(bars,cc.values): ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.3,str(val),ha='center',color='#e6edf3',fontsize=9)
        for sp in ax.spines.values(): sp.set_edgecolor('#30363d')
        plt.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close()

        st.markdown('<div class="section-title">AQI Prediction Accuracy</div>', unsafe_allow_html=True)
        sel=st.selectbox("Select Model",list(pred_store.keys()),key='aqi_sel')
        yp=np.array(pred_store[sel]).flatten()
        ac=[pm25_to_aqi(v)[0] for v in np.array(y_test).flatten()]
        pc=[pm25_to_aqi(v)[0] for v in yp]
        rows=[{'AQI Category':cat,'Actual Count':ac.count(cat),'Predicted Count':pc.count(cat),
               'Match %':round(sum(a==p==cat for a,p in zip(ac,pc))/max(ac.count(cat),1)*100,1)}
              for cat in cat_order if cat in ac or cat in pc]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

        from sklearn.metrics import f1_score as f1s
        f1v=f1s(ac,pc,average='weighted',zero_division=0)
        st.markdown(f'''<div class="metric-card" style="margin-top:1rem">
            <div class="metric-value">{f1v:.4f}</div>
            <div class="metric-label">Weighted F1-Score — {sel}</div></div>''', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — K-FOLD CV
# ══════════════════════════════════════════════════════════════════════════════
with tab_kfold:
    if 'ran' not in st.session_state or not st.session_state.get('kfold_results'):
        st.info("Enable K-Fold CV and run the analysis.")
    else:
        kfold_results=st.session_state['kfold_results']
        st.markdown('<div class="section-title">5-Fold Cross Validation Results</div>', unsafe_allow_html=True)
        kf_df=pd.DataFrame([{'Model':m,**v} for m,v in kfold_results.items()]).sort_values('Mean R2',ascending=False).reset_index(drop=True)
        kf_df.index+=1; st.dataframe(kf_df,use_container_width=True)

        fig,ax=plt.subplots(figsize=(10,5),facecolor='#0d1117'); ax.set_facecolor('#0d1117')
        models=kf_df['Model'].tolist(); r2m=kf_df['Mean R2'].tolist(); r2s=kf_df['Std R2'].tolist()
        x=np.arange(len(models))
        bars=ax.bar(x,r2m,yerr=r2s,capsize=5,color='#1f6feb',alpha=0.85,edgecolor='#30363d',linewidth=0.5)
        ax.set_xticks(x); ax.set_xticklabels(models,rotation=45,ha='right',color='#8b949e')
        ax.set_ylabel('Mean R² (± std)',color='#8b949e'); ax.set_title(f'5-Fold CV — {display_name}',color='#e6edf3')
        ax.set_ylim(0,1.15); ax.tick_params(colors='#8b949e')
        for sp in ax.spines.values(): sp.set_edgecolor('#30363d')
        for bar,val,std in zip(bars,r2m,r2s):
            ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+std+0.02,f'{val:.3f}',ha='center',color='#e6edf3',fontsize=8)
        plt.tight_layout(); st.pyplot(fig,use_container_width=True); plt.close()

        csv2=io.StringIO(); kf_df.to_csv(csv2,index=False)
        st.download_button("⬇️  Download K-Fold CSV",csv2.getvalue(),
                           file_name=f"{display_name.replace(' ','_')}_kfold.csv",mime="text/csv")
