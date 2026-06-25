import json

import pandas as pd

from src.chart import make_chart_data, make_demand_change_chart_data
from src.config_loader import load_item_config
from src.data_loader import load_raw_data, load_train_data
from src.feature_names import get_feature_display_name, get_feature_group
from src.plan_risk import build_item_risk_result, build_risk_dashboard
from src.predict import forecast_next_month


ITEM_CODES = ["HR", "CR", "GI"]


def load_importance(config, top_n=5):
    importance_df = pd.read_csv(config["importance_path"])

    importance_df["display_name"] = importance_df["feature"].apply(
        get_feature_display_name
    )
    importance_df["group"] = importance_df["feature"].apply(get_feature_group)

    grouped_df = (
        importance_df.groupby("group", as_index=False)
        .agg(
            importance=("importance", "sum"),
            features=("display_name", lambda values: list(values)),
        )
    )
    grouped_df = grouped_df[grouped_df["importance"] > 0].copy()

    total_importance = grouped_df["importance"].sum()
    grouped_df["importance_pct"] = (
        grouped_df["importance"] / total_importance * 100
        if total_importance != 0
        else 0
    )

    grouped_df["display_name"] = grouped_df["group"]
    grouped_df["importance"] = grouped_df["importance"].round(2)
    grouped_df["importance_pct"] = grouped_df["importance_pct"].round(1)

    grouped_df = grouped_df.sort_values(
        by="importance",
        ascending=False,
    ).head(top_n)

    return grouped_df.to_dict(orient="records")


def load_metrics(config):
    with open(config["metrics_path"], "r", encoding="utf-8") as f:
        return json.load(f)


def get_item_result(item_code, start_date, end_date):
    """
    품목별 AI 수요예측 결과를 조회

    품목 상세 화면에서 전국 AI 예측, 모델 성능, 변수 중요도, 예측 차트를 보여주는 데 사용
    """
    config = load_item_config(item_code)
    train_df = load_train_data(config)
    raw_df = load_raw_data(config)

    forecast_result = forecast_next_month(config, train_df, raw_df)
    chart_data = make_chart_data(
        config=config,
        start_date=start_date,
        end_date=end_date,
        forecast_result=forecast_result,
    )

    return {
        "item_code": item_code,
        "item_name": config["name"],
        "forecast_month": forecast_result["forecast_month"],
        "national_forecast": forecast_result,
        "model_info": load_metrics(config),
        "feature_importance": load_importance(config),
        "chart_data": chart_data,
    }


def get_monitoring_context(item_codes=None):
    """
    계획/재고 입력 화면에 필요한 기준 월 정보를 생성

    최근 확정 데이터 월, AI 예측 월, 입력 대상 품목 목록을 표시하는 데 사용
    """
    item_codes = item_codes or ITEM_CODES
    config = load_item_config(item_codes[0])
    train_df = load_train_data(config)
    raw_df = load_raw_data(config)
    forecast_result = forecast_next_month(config, train_df, raw_df)

    latest_data_month = raw_df[config["date_col"]].max().strftime("%Y-%m")

    return {
        "latest_data_month": latest_data_month,
        "forecast_month": forecast_result["forecast_month"],
        "item_codes": item_codes,
    }


def run_plan_risk_monitoring(input_rows):
    """
    사용자 입력값으로 생산 및 재고 리스크 모니터링을 실행

    검산 결과 대시보드와 품목별 상세 검토 화면에 사용할 결과를 생성
    """
    item_results = []

    for row in input_rows:
        item_code = row["item_code"].upper()
        config = load_item_config(item_code)
        train_df = load_train_data(config)
        raw_df = load_raw_data(config)
        forecast_result = forecast_next_month(config, train_df, raw_df)
        latest_data_month = raw_df[config["date_col"]].max().strftime("%Y-%m")

        item_result = build_item_risk_result(
            item_code=item_code,
            item_name=config["name"],
            forecast_month=forecast_result["forecast_month"],
            latest_data_month=latest_data_month,
            national_ai_demand=forecast_result["national_forecast_demand"],
            market_share=float(row["market_share"]),
            planned_production=float(row["planned_production"]),
            current_stock=float(row["current_stock"]),
            target_stock=float(row["target_stock"]),
            raw_df=raw_df,
            demand_col=config["demand_col"],
        )
        item_results.append(item_result)

    return build_risk_dashboard(item_results)


def get_item_risk_detail(item_code, monitoring_result, recent_months=12):
    """
    리스크 모니터링 결과 중 특정 품목의 상세 데이터를 조회

    품목 상세 화면에서 판단 근거, 계산값, 수요 변화 차트를 보여주는 데 사용
    """
    item_code = item_code.upper()
    item_result = next(
        (row for row in monitoring_result["items"] if row["item_code"] == item_code),
        None,
    )

    if item_result is None:
        raise ValueError(f"{item_code} 품목의 모니터링 결과가 없습니다.")

    config = load_item_config(item_code)
    chart_data = make_demand_change_chart_data(
        config=config,
        item_risk=item_result,
        recent_months=recent_months,
    )

    return {
        "item": item_result,
        "chart_data": chart_data,
    }
