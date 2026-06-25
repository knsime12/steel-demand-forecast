import json

import joblib
import pandas as pd


def restore_forecast_demand(current_demand, forecast_target, target_type):
    if target_type == "absolute":
        forecast_demand = forecast_target
        forecast_diff = forecast_demand - current_demand
        forecast_change_rate = (forecast_diff / current_demand) * 100

    elif target_type == "diff":
        forecast_diff = forecast_target
        forecast_demand = current_demand + forecast_diff
        forecast_change_rate = (forecast_diff / current_demand) * 100

    elif target_type == "rate":
        forecast_change_rate = forecast_target
        forecast_demand = current_demand * (1 + forecast_change_rate / 100)
        forecast_diff = forecast_demand - current_demand

    else:
        raise ValueError("target_type must be one of: absolute, diff, rate")

    return forecast_demand, forecast_diff, forecast_change_rate


def load_metrics(config):
    with open(config["metrics_path"], "r", encoding="utf-8") as f:
        return json.load(f)


def forecast_next_month(config, train_df, raw_df):
    model = joblib.load(config["model_path"])
    features = joblib.load(config["features_path"])
    metrics = load_metrics(config)
    target_type = metrics.get("target_type", "rate")
    forecast_horizon = metrics.get("forecast_horizon", 1)

    latest_train = train_df.sort_values(config["date_col"]).iloc[[-1]]
    latest_raw = raw_df.sort_values(config["date_col"]).iloc[[-1]]

    missing_features = [col for col in features if col not in latest_train.columns]
    if missing_features:
        raise KeyError(
            "Missing prediction features after applying saved feature logic: "
            f"{missing_features}"
        )

    X_latest = latest_train[features]
    forecast_target = model.predict(X_latest)[0]

    national_current_demand = latest_raw[config["demand_col"]].iloc[0]

    (
        national_forecast_demand,
        national_forecast_diff,
        national_forecast_change_rate
    ) = restore_forecast_demand(
        current_demand=national_current_demand,
        forecast_target=forecast_target,
        target_type=target_type
    )

    forecast_month = (
        latest_raw[config["date_col"]].iloc[0]
        + pd.DateOffset(months=forecast_horizon)
    )

    return {
        "forecast_month": forecast_month.strftime("%Y-%m"),
        "target_type": target_type,
        "forecast_horizon": forecast_horizon,
        "national_forecast_target": round(float(forecast_target), 2),
        "national_forecast_diff": round(float(national_forecast_diff), 2),
        "national_forecast_change_rate": round(float(national_forecast_change_rate), 2),
        "national_forecast_demand": int(round(national_forecast_demand))
    }
