import os
import logging
from datetime import date
import pandas as pd
from prophet import Prophet
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# -------------------------
# Configuration & Setup
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FORECAST_DIR = os.path.join(BASE_DIR, "forecasts")
PLOT_DIR = os.path.join(FORECAST_DIR, "plots")

os.makedirs(FORECAST_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)

# Logging
LOG_FILE = os.path.join(BASE_DIR, "forecasting.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logging.getLogger().addHandler(logging.StreamHandler())

# Load environment variables
load_dotenv(os.path.join(BASE_DIR, ".env"))

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "crisislens")

DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URI)

# -------------------------
# Database Functions
# -------------------------
def fetch_emergency_types(engine):
    query = "SELECT DISTINCT emergency_type FROM enriched_data"     
    with engine.connect() as conn:
        result = conn.execute(text(query))
        types = [row[0] for row in result if row[0]]
    return types

def fetch_daily_calls_by_type(engine, emergency_type: str | None = None):
    """Fetch aggregated daily calls for a given emergency type or overall."""
    if emergency_type:
        query = """
            SELECT DATE(timestamp) AS ds, COUNT(*) AS y
            FROM enriched_data
            WHERE emergency_type = :etype
            GROUP BY DATE(timestamp)
            ORDER BY ds
        """
        params = {"etype": emergency_type}
    else:
        query = """
            SELECT DATE(timestamp) AS ds, COUNT(*) AS y
            FROM enriched_data
            GROUP BY DATE(timestamp)
            ORDER BY ds
        """
        params = {}

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn, params=params)
    return df

def store_forecast(forecast_df, emergency_type: str | None, model_used: str):
    """Insert forecast results into forecasted_calls table."""
    insert_query = """
        INSERT INTO forecasted_calls
            (forecast_date, district, emergency_type, emergency_subtype,
             predicted_calls, lower_bound, upper_bound, model_used, source, generated_at)
        VALUES
            (:forecast_date, :district, :emergency_type, :emergency_subtype,
             :predicted_calls, :lower_bound, :upper_bound, :model_used, :source, NOW())
    """
    inserted_dates = []
    with engine.begin() as conn:
        for _, row in forecast_df.iterrows():
            conn.execute(
                text(insert_query),
                {
                    "forecast_date": row["forecast_date"],
                    "district": "All",  # No district-level forecast yet
                    "emergency_type": emergency_type,
                    "emergency_subtype": "General",
                    "predicted_calls": int(row["predicted_calls"]),
                    "lower_bound": int(row["lower_bound"]),
                    "upper_bound": int(row["upper_bound"]),
                    "model_used": model_used,
                    "source": "batch_forecast"
                }
            )
            inserted_dates.append(row["forecast_date"])
    return inserted_dates

# -------------------------
# Forecasting Functions
# -------------------------
def prophet_forecast(df, periods=14):
    """Generate forecast using Prophet."""
    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(df)

    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    forecast_df = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods).copy()
    forecast_df.rename(
        columns={"ds": "forecast_date", "yhat": "predicted_calls", "yhat_lower": "lower_bound", "yhat_upper": "upper_bound"},
        inplace=True
    )
    return forecast_df

def anchor_forecast_to_today(forecast_df: pd.DataFrame, last_hist_date) -> pd.DataFrame:
    today = date.today()
    if hasattr(last_hist_date, 'date'):
        last_hist_date = last_hist_date.date()
        
    delta_days = (today - last_hist_date).days
    if delta_days <= 0:
        return forecast_df

    logging.info(f"Anchoring forecast: shifting by {delta_days} days to align with today.")
    anchored = forecast_df.copy()
    anchored["forecast_date"] = anchored["forecast_date"].apply(lambda d: d + pd.Timedelta(days=delta_days))
    anchored["forecast_date"] = pd.to_datetime(anchored["forecast_date"]).dt.date
    return anchored

# -------------------------
# Visualization
# -------------------------
def plot_forecast(history_df, forecast_df, emergency_type: str | None):
    etype_label = emergency_type if emergency_type else "Overall"
    plt.figure(figsize=(12, 6))

    plt.plot(history_df["ds"], history_df["y"], label="Historical Calls", color="blue")
    plt.plot(forecast_df["forecast_date"], forecast_df["predicted_calls"], label="Forecast", color="red")
    plt.fill_between(
        forecast_df["forecast_date"],
        forecast_df["lower_bound"],
        forecast_df["upper_bound"],
        color="pink", alpha=0.3, label="Confidence Interval"
    )

    plt.title(f"Emergency Calls Forecast - {etype_label}")
    plt.xlabel("Date")
    plt.ylabel("Number of Calls")
    plt.legend()
    plt.tight_layout()

    filepath = os.path.join(PLOT_DIR, f"{etype_label.replace(' ', '_')}_forecast.png")
    plt.savefig(filepath)
    plt.close()
    logging.info(f"Saved forecast plot: {filepath}")

# -------------------------
# Main Forecasting Orchestrator
# -------------------------
def generate_forecast(engine, model="prophet", periods=14, anchor=True):
    all_inserted_dates = []

    types = fetch_emergency_types(engine)
    logging.info(f"Found emergency types: {types}")

    for etype in types:
        hist = fetch_daily_calls_by_type(engine, etype)
        if hist.empty:
            logging.warning(f"No historical data for type: {etype}")
            continue

        forecast_df = prophet_forecast(hist, periods=periods)
        if anchor:
            forecast_df = anchor_forecast_to_today(forecast_df, last_hist_date=hist["ds"].max())

        inserted_dates = store_forecast(forecast_df, emergency_type=etype, model_used=model.capitalize())
        all_inserted_dates.extend(inserted_dates)

        plot_forecast(hist, forecast_df, etype)

    hist_overall = fetch_daily_calls_by_type(engine, emergency_type=None)
    if not hist_overall.empty:
        forecast_df_overall = prophet_forecast(hist_overall, periods=periods)
        if anchor:
            forecast_df_overall = anchor_forecast_to_today(forecast_df_overall, last_hist_date=hist_overall["ds"].max())

        inserted_dates_overall = store_forecast(forecast_df_overall, emergency_type=None, model_used=model.capitalize())
        all_inserted_dates.extend(inserted_dates_overall)

        plot_forecast(hist_overall, forecast_df_overall, emergency_type=None)

    return all_inserted_dates

# -------------------------
# Entry Point
# -------------------------
if __name__ == "__main__":
    logging.info("Starting forecast generation...")
    inserted = generate_forecast(engine, model="prophet", periods=30, anchor=True)
    logging.info(f"Inserted forecast for dates: {inserted}")
