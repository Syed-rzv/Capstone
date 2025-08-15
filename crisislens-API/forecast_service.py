#!/usr/bin/env python
"""
forecast_service.py
- Fetches daily call counts from emergency_data
- Trains Prophet (default) or other models (extendable)
- Stores 30-day forecast into forecast_calls table (with metadata)
- Usage: python forecast_service.py --periods 30 --model prophet --anchor
"""

import os
import logging
import argparse
from datetime import datetime, date
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import mysql.connector

# Optional imports (Prophet required for default flow)
try:
    from prophet import Prophet
except Exception:
    Prophet = None

# You can add ARIMA/LSTM imports later (conditionally)
# from statsmodels.tsa.arima.model import ARIMA

# -------------------------
# Config
# -------------------------
BASE_DIR = os.path.dirname(__file__)
dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

SQLALCHEMY_CONN = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# -------------------------
# Logging
# -------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# -------------------------
# Helpers
# -------------------------
def get_sqlalchemy_engine():
    return create_engine(SQLALCHEMY_CONN, echo=False)


def get_db_conn_mysqlconnector():
    """Return mysql.connector connection for DDL / inserts (safe for inserts)."""
    return mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)


# -------------------------
# Fetch historical daily counts
# -------------------------
def fetch_daily_calls(engine):
    query = """
        SELECT DATE(timestamp) AS ds, COUNT(*) as y
        FROM emergency_data
        GROUP BY DATE(timestamp)
        ORDER BY ds
    """
    df = pd.read_sql(query, engine)
    if df.empty:
        return df
    df['ds'] = pd.to_datetime(df['ds']).dt.date  # keep as date
    df['y'] = df['y'].astype(int)
    return df


# -------------------------
# Prophet forecasting
# -------------------------
def prophet_forecast(df, periods=30):
    if Prophet is None:
        raise RuntimeError("Prophet is not installed in this environment.")
    # Prophet expects ds (datetime) and y columns
    temp = df.copy()
    temp['ds'] = pd.to_datetime(temp['ds'])
    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(temp)

    future = model.make_future_dataframe(periods=periods, freq='D')
    forecast = model.predict(future)
    out = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods).copy()
    out.rename(columns={
        'ds': 'forecast_date',
        'yhat': 'predicted_calls',
        'yhat_lower': 'lower_bound',
        'yhat_upper': 'upper_bound'
    }, inplace=True)
    # convert forecast_date to date (no time)
    out['forecast_date'] = pd.to_datetime(out['forecast_date']).dt.date
    return out


# -------------------------
# Store forecast in DB
# -------------------------
def store_forecast(forecast_df, model_used='Prophet'):
    """
    forecast_df columns expected: forecast_date (date), predicted_calls, lower_bound, upper_bound
    """
    conn = get_db_conn_mysqlconnector()
    cursor = conn.cursor()

    # Create table if not exists (matches recommended schema)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecast_calls (
            forecast_date DATE PRIMARY KEY,
            predicted_calls INT,
            lower_bound INT,
            upper_bound INT,
            model_used VARCHAR(50),
            generated_at DATETIME
        )
    """)

    # Option: REPLACE INTO to upsert by primary key
    insert_sql = """
        REPLACE INTO forecast_calls
        (forecast_date, predicted_calls, lower_bound, upper_bound, model_used, generated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    for _, row in forecast_df.iterrows():
        cursor.execute(insert_sql, (
            row['forecast_date'],
            int(round(row['predicted_calls'])),
            int(round(row['lower_bound'])),
            int(round(row['upper_bound'])),
            model_used,
            datetime.now()
        ))

    conn.commit()
    cursor.close()
    conn.close()
    logging.info("✅ Forecast saved to forecast_calls")


# -------------------------
# Anchor helper (optional)
# -------------------------
def anchor_forecast_to_today(forecast_df, last_hist_date):
    """
    Shift forecast dates so that the first forecast date is tomorrow relative to today:
    This is a demo convenience only — it shifts dates by the delta between today and last_hist_date.
    """
    today = date.today()
    delta_days = (today - last_hist_date).days
    if delta_days == 0:
        return forecast_df
    logging.info(f"Anchoring forecast: shifting forecast by {delta_days} days to align with today.")
    forecast_df = forecast_df.copy()
    forecast_df['forecast_date'] = forecast_df['forecast_date'].apply(lambda d: d + pd.Timedelta(days=delta_days))
    return forecast_df


# -------------------------
# Main generator (modular)
# -------------------------
def generate_forecast(model='prophet', periods=30, anchor=False):
    engine = get_sqlalchemy_engine()
    df = fetch_daily_calls(engine)

    if df.empty:
        logging.error("No historical data found in emergency_data. Aborting forecast.")
        return

    min_date = df['ds'].min()
    max_date = df['ds'].max()
    logging.info(f"Historical data range: {min_date} -> {max_date} ({len(df)} days)")

    # Choose model
    model = model.lower()
    if model == 'prophet':
        forecast_df = prophet_forecast(df, periods=periods)
    elif model == 'arima':
        # Placeholder: implement ARIMA model here later.
        raise NotImplementedError("ARIMA option not implemented yet. Install statsmodels and add code.")
    else:
        raise ValueError("Unsupported model. Use 'prophet' (default) or implement ARIMA/LSTM.")

    # Optional anchor (demo-only)
    if anchor:
        forecast_df = anchor_forecast_to_today(forecast_df, last_hist_date=max_date)

    store_forecast(forecast_df, model_used=model.capitalize())
    logging.info("Forecast generation complete.")


# -------------------------
# CLI
# -------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and store call volume forecasts.")
    parser.add_argument("--model", choices=['prophet', 'arima'], default='prophet', help="Model to use")
    parser.add_argument("--periods", type=int, default=30, help="Days to forecast")
    parser.add_argument("--anchor", action="store_true", help="Anchor forecast dates to today (demo mode)")
    args = parser.parse_args()

    generate_forecast(model=args.model, periods=args.periods, anchor=args.anchor)
