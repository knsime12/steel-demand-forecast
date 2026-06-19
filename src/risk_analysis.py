import pandas as pd

# 산업별 중요도 추출
def extract_industry_importance(importance_path, top_n = 3) :
    importance_df = pd.read_csv(importance_path)

    industry_keywords = {
        "자동차": ["auto"],
        "건설": ["construction"],
        "가전": ["appliance"]
    }

    industry_scores = []

    for industry, keywords in industry_keywords.items() :
        score = importance_df[
            importance_df["feature"].apply(
                lambda x: any(keyword in x for keyword in keywords)
            )
        ]["importance"].sum()

        if score > 0 :
            industry_scores.append({
                "industry": industry,
                "importance": round(float(score * 100), 2)
            })

    industry_scores = sorted(
        industry_scores,
        key=lambda x: x["importance"],
        reverse = True
    )

    total_score = sum(
        item["importance"]
        for item in industry_scores
    )

    for item in industry_scores :
        item["importance_pct"] = round(
            item["importance"] / total_score * 100,
            1
        )

    return industry_scores[:top_n]

# 위험도 분석
def make_risk_analysis(
    forecast_month,
    national_current_stock,
    national_forecast_demand,
    national_shortage_qty,
    main_industries = None
) :
    """
    전국 예측 수요와 전국 재고를 기준으로 위험도 분석

    - national_current_stock: 전국 현재 재고
    - national_forecast_demand: 다음 달 전국 예측 수요
    - natonal_shortage_qty: 전국 부족량
    """
    # 재고 유지 가능기간
    if national_forecast_demand > 0 :
        available_months = national_current_stock / national_forecast_demand
    else :
        available_months = None

    # 부족 예상 시점
    if available_months is not None :
        shortage_date = pd.to_datetime(forecast_month) + pd.DateOffset(
            months = max(int(available_months), 0)
        )
        shortage_month = shortage_date.strftime("%Y년 %m월")
    else :
        shortage_month = None

    # 위험도 등급
    if national_shortage_qty > 0 :
        if available_months is not None and available_months <= 1 :
            risk_level = "HIGH"
        elif available_months is not None and available_months <= 3 :
            risk_level = "MEDIUM"
        else :
            risk_level = "LOW"

    else :
        risk_level = "LOW"

    return {
        "risk_level": risk_level,
        "national_shortage_qty": int(round(national_shortage_qty)),
        "shortage_month": shortage_month,
        "available_months": None if available_months is None else round(available_months, 1),
        "main_industries": main_industries or []
    }