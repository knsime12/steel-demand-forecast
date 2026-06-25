import pandas as pd


def make_chart_data(config, start_date, end_date, forecast_result):
    """
    실제 수요와 AI 예측 수요 차트 데이터를 생성

    품목 상세 화면의 전국 기준 실제 수요 vs AI 예측 수요 그래프에 사용
    """
    pred_df = pd.read_csv(config["prediction_path"])
    pred_df["date"] = pd.to_datetime(pred_df["date"])

    chart_df = pred_df[
        (pred_df["date"] >= pd.to_datetime(start_date))
        & (pred_df["date"] <= pd.to_datetime(end_date))
    ].copy()

    chart_data = []

    for _, row in chart_df.iterrows():
        chart_data.append(
            {
                "date": row["date"].strftime("%Y-%m"),
                "actual_demand": (
                    None
                    if pd.isna(row["actual_demand"])
                    else round(row["actual_demand"], 2)
                ),
                "predicted_demand": round(row["predicted_demand"], 2),
            }
        )

    chart_data.append(
        {
            "date": forecast_result["forecast_month"],
            "actual_demand": None,
            "predicted_demand": round(
                forecast_result["national_forecast_demand"],
                2,
            ),
        }
    )

    return chart_data


def make_demand_change_chart_data(config, item_risk, recent_months=12):
    """
    품목별 수요 변화 확인용 차트 데이터를 생성

    리스크 상세 화면에서 최근 실제 수요 흐름과 AI 예측 수요를 비교하는 데 사용
    """
    pred_df = pd.read_csv(config["prediction_path"])
    pred_df["date"] = pd.to_datetime(pred_df["date"])

    chart_df = pred_df.dropna(subset=["actual_demand"]).tail(recent_months).copy()
    chart_data = []

    for _, row in chart_df.iterrows():
        chart_data.append(
            {
                "date": row["date"].strftime("%Y-%m"),
                "actual_demand": round(row["actual_demand"], 2),
                "predicted_demand": round(row["predicted_demand"], 2),
                "point_type": "history",
            }
        )

    chart_data.append(
        {
            "date": item_risk["forecast_month"],
            "actual_demand": None,
            "predicted_demand": item_risk["national_ai_demand"],
            "point_type": "forecast",
        }
    )

    return chart_data
