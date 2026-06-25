import os
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.inspection import permutation_importance

from src.feature_names import get_feature_display_name


def ensure_dirs(item_code):
    os.makedirs(f"models/{item_code}", exist_ok=True)
    os.makedirs(f"data/processed/{item_code}", exist_ok=True)


def clean_numeric_columns(df):
    df = df.copy()

    for col in df.columns:
        if col == "date":
            continue

        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .replace("nan", np.nan)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def add_common_features(df):
    df = df.copy()

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df = clean_numeric_columns(df)

    df["month"] = df["date"].dt.month

    generated_features = {}
    base_cols = [col for col in df.columns if col != "date"]

    for col in base_cols:
        generated_features[f"{col}_lag1"] = df[col].shift(1)
        generated_features[f"{col}_lag2"] = df[col].shift(2)
        generated_features[f"{col}_diff"] = df[col] - df[col].shift(1)
        generated_features[f"{col}_diff2"] = df[col] - df[col].shift(2)

    if generated_features:
        df = pd.concat([df, pd.DataFrame(generated_features, index=df.index)], axis=1)

    shock_features = {}
    diff_cols = [col for col in df.columns if col.endswith("_diff")]
    for col in diff_cols:
        threshold = df[col].abs().quantile(0.9)
        shock_features[f"{col}_shock90"] = (df[col].abs() > threshold).astype(int)

    if shock_features:
        df = pd.concat([df, pd.DataFrame(shock_features, index=df.index)], axis=1)

    ma_cols = [
        "HR_demand",
        "CR_demand",
        "G_demand",
        "HR_prod",
        "CR_prod",
        "G_prod"
    ]

    ma_features = {}
    for col in ma_cols:
        if col in df.columns:
            ma_features[f"{col}_ma3"] = df[col].rolling(3).mean()

    if ma_features:
        df = pd.concat([df, pd.DataFrame(ma_features, index=df.index)], axis=1)

    dummy_features = {}
    for month in [1, 12]:
        dummy_features[f"is_month_{month}"] = (df["month"] == month).astype(int)

    if dummy_features:
        df = pd.concat([df, pd.DataFrame(dummy_features, index=df.index)], axis=1)

    return df


def make_target(df, demand_col, target_type, forecast_horizon=1):
    next_demand = df[demand_col].shift(-forecast_horizon)
    current_demand = df[demand_col]

    if target_type == "absolute":
        return next_demand
    elif target_type == "diff":
        return next_demand - current_demand
    elif target_type == "rate":
        return ((next_demand / current_demand) - 1) * 100
    else:
        raise ValueError("target_type은 'absolute', 'diff', 'rate' 중 하나여야 합니다.")


def restore_demand(current_demand, y_true, y_pred, target_type):
    if target_type == "absolute":
        actual_demand = y_true
        forecast_demand = y_pred
        actual_diff = actual_demand - current_demand
        forecast_diff = forecast_demand - current_demand

    elif target_type == "diff":
        actual_demand = current_demand + y_true
        forecast_demand = current_demand + y_pred
        actual_diff = y_true
        forecast_diff = y_pred

    elif target_type == "rate":
        actual_demand = current_demand * (1 + y_true / 100)
        forecast_demand = current_demand * (1 + y_pred / 100)
        actual_diff = y_true
        forecast_diff = y_pred

    else:
        raise ValueError("target_type은 'absolute', 'diff', 'rate' 중 하나여야 합니다.")

    return actual_demand, forecast_demand, actual_diff, forecast_diff


def make_item_dataset(df, demand_col, features, target_type, forecast_horizon=1):
    df = df.copy()

    df["target"] = make_target(df, demand_col, target_type, forecast_horizon)

    use_features = [col for col in features if col in df.columns]

    model_df = (
        df
        .dropna(subset=use_features + ["target"])
        .reset_index(drop=True)
    )

    X = model_df[use_features]
    y = model_df["target"]
    dates = model_df["date"]

    return model_df, X, y, dates, use_features


def get_model_grids():
    return {
        "Ridge": {
            "pipeline": Pipeline([
                ("scaler", StandardScaler()),
                ("model", Ridge())
            ]),
            "params": {
                "model__alpha": np.logspace(-4, 3, 80),
                "model__fit_intercept": [True, False]
            }
        },

        "Lasso": {
            "pipeline": Pipeline([
                ("scaler", StandardScaler()),
                ("model", Lasso(max_iter=100000))
            ]),
            "params": {
                "model__alpha": np.logspace(-4, 2, 80),
                "model__fit_intercept": [True, False]
            }
        },

        "ElasticNet": {
            "pipeline": Pipeline([
                ("scaler", StandardScaler()),
                ("model", ElasticNet(max_iter=100000, random_state = 42))
            ]),
            "params": {
                "model__alpha": np.logspace(-3, 2, 60),
                "model__l1_ratio": [0.1, 0.3, 0.5, 0.7],
                "model__fit_intercept": [True, False]
            }
        }
    }


def tune_models(X, y, tscv):
    results = []

    for model_name, info in get_model_grids().items():
        print(f"\n========== {model_name} 튜닝 시작 ==========")

        grid = GridSearchCV(
            estimator=info["pipeline"],
            param_grid=info["params"],
            cv=tscv,
            scoring="neg_mean_absolute_error",
            n_jobs=-1
        )

        grid.fit(X, y)

        results.append({
            "model_name": model_name,
            "best_model": grid.best_estimator_,
            "best_params": grid.best_params_,
            "best_mae": -grid.best_score_
        })

        print("Best Params:", grid.best_params_)
        print(f"Best MAE: {-grid.best_score_:.4f}")

    return sorted(results, key=lambda x: x["best_mae"])


def evaluate_baseline(X, y, dates, tscv):
    scores = []

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X), start=1):
        y_test = y.iloc[test_idx]
        forecast_diff = np.zeros(len(y_test))

        scores.append({
            "fold": fold,
            "train_start": str(dates.iloc[train_idx].min().date()),
            "train_end": str(dates.iloc[train_idx].max().date()),
            "test_start": str(dates.iloc[test_idx].min().date()),
            "test_end": str(dates.iloc[test_idx].max().date()),
            "MAE": mean_absolute_error(y_test, forecast_diff),
            "RMSE": mean_squared_error(y_test, forecast_diff) ** 0.5,
            "Test_R2": r2_score(y_test, forecast_diff)
        })

    return pd.DataFrame(scores)


def calc_direction_metrics(pred_df):
    df = pred_df.copy().sort_values("forecast_month").reset_index(drop=True)

    df["actual_direction"] = np.sign(df["actual_diff"])
    df["forecast_direction"] = np.sign(df["forecast_diff"])

    valid_df = df[
        (df["actual_direction"] != 0) &
        (df["forecast_direction"] != 0)
    ].copy()

    hit_rate = (
        (valid_df["actual_direction"] == valid_df["forecast_direction"]).mean()
        * 100
    )

    df["actual_turnaround"] = (
        df["actual_direction"] != df["actual_direction"].shift(1)
    ).astype(int)

    df["forecast_turnaround"] = (
        df["forecast_direction"] != df["forecast_direction"].shift(1)
    ).astype(int)

    turn_df = df.iloc[1:].copy()

    # 실제 전환이 있었던 구간만 기준
    actual_turn_df = turn_df[turn_df["actual_turnaround"] == 1]

    turnaround_hit_rate = (
        actual_turn_df["forecast_turnaround"].mean() * 100
        if len(actual_turn_df) > 0
        else 0
    )

    # 전체 구간에서 전환/비전환 여부가 같은지 기준
    turnaround_match_rate = (
        (turn_df["actual_turnaround"] == turn_df["forecast_turnaround"]).mean()
        * 100
        if len(turn_df) > 0
        else 0
    )

    return {
        "hit_rate": round(float(hit_rate), 4),
        "turnaround_hit_rate": round(float(turnaround_hit_rate), 4),
        "turnaround_match_rate": round(float(turnaround_match_rate), 4)
    }


def evaluate_model(model, X, y, dates, model_df, demand_col, target_type, forecast_horizon, tscv):
    scores = []
    predictions = []
    importances = []

    for fold, (train_idx, test_idx) in enumerate(tscv.split(X), start=1):
        X_train = X.iloc[train_idx]
        X_test = X.iloc[test_idx]

        y_train = y.iloc[train_idx]
        y_test = y.iloc[test_idx]

        fold_model = clone(model)
        fold_model.fit(X_train, y_train)

        train_pred = fold_model.predict(X_train)
        forecast_target = fold_model.predict(X_test)

        current_demand = model_df.loc[test_idx, demand_col].values
        actual_demand, forecast_demand, actual_diff, forecast_diff = restore_demand(
            current_demand=current_demand,
            y_true=y_test.values,
            y_pred=forecast_target,
            target_type=target_type
        )

        abs_error = np.abs(actual_demand - forecast_demand)
        error_rate = abs_error / actual_demand * 100

        forecast_month = (
            pd.to_datetime(model_df.loc[test_idx, "date"])
            + pd.DateOffset(months=forecast_horizon)
        )

        fold_pred_df = pd.DataFrame({
            "fold": fold,
            "date": model_df.loc[test_idx, "date"].values,
            "forecast_month": forecast_month.values,
            "current_demand": current_demand,
            "actual_diff": actual_diff,
            "forecast_diff": forecast_diff,
            "actual_demand": actual_demand,
            "forecast_demand": forecast_demand,
            "error": actual_demand - forecast_demand,
            "abs_error": abs_error,
            "error_rate": error_rate
        })

        direction_metrics = calc_direction_metrics(fold_pred_df)

        scores.append({
            "fold": fold,
            "train_start": str(dates.iloc[train_idx].min().date()),
            "train_end": str(dates.iloc[train_idx].max().date()),
            "test_start": str(dates.iloc[test_idx].min().date()),
            "test_end": str(dates.iloc[test_idx].max().date()),

            "target_MAE": mean_absolute_error(y_test, forecast_diff),
            "target_RMSE": mean_squared_error(y_test, forecast_diff) ** 0.5,
            "target_Test_R2": r2_score(y_test, forecast_diff),

            "MAE": mean_absolute_error(actual_demand, forecast_demand),
            "RMSE": mean_squared_error(actual_demand, forecast_demand) ** 0.5,
            "MAPE": error_rate.mean(),
            "Train_R2": r2_score(y_train, train_pred),
            "Test_R2": r2_score(actual_demand, forecast_demand),

            "Hit_Rate": direction_metrics["hit_rate"],
            "Turnaround_Hit_Rate": direction_metrics["turnaround_hit_rate"],
            "Turnaround_Match_Rate": direction_metrics["turnaround_match_rate"]
        })

        predictions.append(fold_pred_df)

        perm = permutation_importance(
            fold_model,
            X_test,
            y_test,
            n_repeats=5,
            random_state=42,
            n_jobs=-1
        )

        importances.append(perm.importances_mean)

    score_df = pd.DataFrame(scores)
    pred_df = pd.concat(predictions, ignore_index=True)

    total_direction_metrics = calc_direction_metrics(pred_df)

    importance_df = pd.DataFrame({
    "feature": X.columns,
    "importance": np.mean(importances, axis=0)
    })

    importance_df["display_name"] = importance_df["feature"].apply(
        get_feature_display_name
    )

    importance_df = importance_df.sort_values(
        "importance",
        ascending=False
    ).reset_index(drop=True)

    return score_df, pred_df, importance_df, total_direction_metrics


def make_next_forecast(final_model, feature_df, features, demand_col, target_type, forecast_horizon):
    predict_df = feature_df.dropna(subset=features).reset_index(drop=True)

    latest_row = predict_df.iloc[[-1]].copy()
    latest_X = latest_row[features]

    pred_target = final_model.predict(latest_X)[0]

    current_demand = latest_row[demand_col].iloc[0]

    _, forecast_demand, _, forecast_diff = restore_demand(
        current_demand=np.array([current_demand]),
        y_true=np.array([0]),
        y_pred=np.array([pred_target]),
        target_type=target_type
    )

    forecast_month = latest_row["date"].iloc[0] + pd.DateOffset(months=forecast_horizon)

    return {
        "base_month": str(latest_row["date"].iloc[0].date()),
        "forecast_month": str(forecast_month.date()),
        "current_demand": round(float(current_demand), 4),
        "forecast_target": round(float(pred_target), 4),
        "forecast_diff": round(float(forecast_diff[0]), 4),
        "forecast_demand": round(float(forecast_demand[0]), 4)
    }


def make_final_prediction_history(
    final_model,
    model_df,
    X,
    y,
    demand_col,
    target_type,
    forecast_horizon,
    start_date="2017-01",
    end_date=None
):
    forecast_target = final_model.predict(X)
    current_demand = model_df[demand_col].values

    actual_demand, predicted_demand, _, _ = restore_demand(
        current_demand=current_demand,
        y_true=y.values,
        y_pred=forecast_target,
        target_type=target_type
    )

    prediction_df = pd.DataFrame({
        "date": pd.to_datetime(model_df["date"]) + pd.DateOffset(months=forecast_horizon),
        "actual_demand": actual_demand,
        "predicted_demand": predicted_demand
    })

    start_date = pd.to_datetime(start_date)
    if end_date is None:
        end_date = prediction_df["date"].max()
    else:
        end_date = pd.to_datetime(end_date)

    prediction_df = prediction_df[
        (prediction_df["date"] >= start_date) &
        (prediction_df["date"] <= end_date)
    ].copy()

    prediction_df["date"] = prediction_df["date"].dt.strftime("%Y-%m")

    return prediction_df.reset_index(drop=True)


def build_metrics(best_result, score_df, pred_df, direction_metrics, target_type, forecast_horizon, next_forecast):
    latest = score_df.iloc[-1]

    best_params = {
        key: float(value) if isinstance(value, (np.floating, np.integer)) else value
        for key, value in best_result["best_params"].items()
    }

    overall_r2 = r2_score(
        pred_df["actual_demand"],
        pred_df["forecast_demand"]
    )

    return {
        "model_name": best_result["model_name"],
        "target_type": target_type,
        "forecast_horizon": forecast_horizon,
        "best_params": best_params,

        "avg_metrics": {
            "mae": round(float(score_df["MAE"].mean()), 4),
            "rmse": round(float(score_df["RMSE"].mean()), 4),

            "r2": round(float(overall_r2), 4),

            "mape": round(float(score_df["MAPE"].mean()), 4),
            "hit_rate": direction_metrics["hit_rate"],
            "turnaround_hit_rate": direction_metrics["turnaround_hit_rate"],
            "turnaround_match_rate": direction_metrics["turnaround_match_rate"]
        },

        "latest_metrics": {
            "fold": int(latest["fold"]),
            "mae": round(float(latest["MAE"]), 4),
            "rmse": round(float(latest["RMSE"]), 4),
            "r2": round(float(latest["Test_R2"]), 4),
            "mape": round(float(latest["MAPE"]), 4),
            "hit_rate": round(float(latest["Hit_Rate"]), 4),
            "turnaround_hit_rate": round(float(latest["Turnaround_Hit_Rate"]), 4),
            "turnaround_match_rate": round(float(latest["Turnaround_Match_Rate"]), 4)
        },

        "next_forecast": next_forecast
    }


def save_artifacts(
    item_code,
    feature_df,
    final_model,
    features,
    metrics,
    prediction_history_df,
    importance_df
):
    model_dir = f"models/{item_code}"
    processed_dir = f"data/processed/{item_code}"

    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    joblib.dump(final_model, f"{model_dir}/model.pkl")
    joblib.dump(features, f"{processed_dir}/features.pkl")

    feature_df.to_csv(
        f"{processed_dir}/train_df.csv",
        index=False,
        encoding="utf-8-sig"
    )

    prediction_history_df.to_csv(
        f"{processed_dir}/predictions.csv",
        index=False,
        encoding="utf-8-sig"
    )

    importance_df.to_csv(
        f"{processed_dir}/feature_importances.csv",
        index=False,
        encoding="utf-8-sig"
    )

    with open(f"{processed_dir}/metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=4)

    print("\n========== 저장 완료 ==========")
    print(f"{model_dir}/model.pkl")
    print(f"{processed_dir}/train_df.csv")
    print(f"{processed_dir}/features.pkl")
    print(f"{processed_dir}/metrics.json")
    print(f"{processed_dir}/predictions.csv")
    print(f"{processed_dir}/feature_importances.csv")


def run_training_pipeline(
    item_code,
    demand_col,
    features,
    target_type,
    forecast_horizon=1,
    data_path="data/raw/steel_demand.csv",
    n_splits=4,
    test_size=15,
    save=False
):
    ensure_dirs(item_code)

    print("\n==============================")
    print(f"{item_code} 모델 학습 시작")
    print("==============================")

    raw_df = pd.read_csv(data_path)
    feature_df = add_common_features(raw_df)

    model_df, X, y, dates, used_features = make_item_dataset(
        df=feature_df,
        demand_col=demand_col,
        features=features,
        target_type=target_type,
        forecast_horizon=forecast_horizon
    )

    print("사용 Features:", used_features)
    print("학습 데이터 수:", len(model_df))

    tscv = TimeSeriesSplit(
        n_splits=n_splits,
        test_size=test_size
    )

    baseline_df = evaluate_baseline(X, y, dates, tscv)

    print(f"\n========== Baseline 성능{target_type} 기준 ==========")
    print(baseline_df[["fold", "MAE", "Test_R2"]])
    print(f"Baseline 평균 MAE: {baseline_df['MAE'].mean():.4f}")

    tuning_results = tune_models(X, y, tscv)
    best_result = tuning_results[0]
    best_model = best_result["best_model"]

    print("\n========== 최종 선택 모델 ==========")
    print(best_result["model_name"])
    print(best_result["best_params"])
    print(f"Best CV MAE{target_type} 기준: {best_result['best_mae']:.4f}")

    score_df, pred_df, importance_df, direction_metrics = evaluate_model(
        model=best_model,
        X=X,
        y=y,
        dates=dates,
        model_df=model_df,
        demand_col=demand_col,
        target_type=target_type,
        forecast_horizon=forecast_horizon,
        tscv=tscv
    )

    final_model = best_model
    final_model.fit(X, y)

    next_forecast = make_next_forecast(
        final_model=final_model,
        feature_df=feature_df,
        features=used_features,
        demand_col=demand_col,
        target_type=target_type,
        forecast_horizon=forecast_horizon
    )

    prediction_history_df = make_final_prediction_history(
        final_model=final_model,
        model_df=model_df,
        X=X,
        y=y,
        demand_col=demand_col,
        target_type=target_type,
        forecast_horizon=forecast_horizon,
        start_date="2017-01"
    )

    metrics = build_metrics(
        best_result=best_result,
        score_df=score_df,
        pred_df=pred_df,
        direction_metrics=direction_metrics,
        next_forecast=next_forecast,
        target_type=target_type,
        forecast_horizon=forecast_horizon
    )

    print("\n========== 복원 수요 기준 평균 성능 ==========")
    print(metrics["avg_metrics"])

    print("\n========== 최신 Fold 성능 ==========")
    print(metrics["latest_metrics"])

    print("\n========== 다음달 예측 ==========")
    print(next_forecast)

    if save:
        answer = input("\n이 결과를 서비스 파일로 저장할까요? (y/n): ").strip().lower()

        if answer == "y":
            save_artifacts(
                item_code=item_code,
                feature_df=feature_df,
                final_model=final_model,
                features=used_features,
                metrics=metrics,
                prediction_history_df=prediction_history_df,
                importance_df=importance_df
            )
        else:
            print("저장하지 않고 종료합니다.")
    else:
        print("\n실험 모드입니다. 파일을 저장하지 않았습니다.")

    return {
        "item_code": item_code,
        "features": used_features,
        "best_model": final_model,
        "feature_df": feature_df,
        "scores": score_df,
        "baseline": baseline_df,
        "predictions": prediction_history_df,
        "cv_predictions": pred_df,
        "importances": importance_df,
        "metrics": metrics
    }
