import pandas as pd


def calculate_company_ai_demand(national_ai_demand, market_share):
    """
    전국 기준 AI 예측 수요를 회사 기준 AI 예측 수요로 환산

    리스크 점검에서 회사 생산계획과 비교할 기준 수요로 사용

    회사 AI 예측 수요 = 전국 AI 예측 수요 * (회사 시장점유율 / 100)
    """
    return national_ai_demand * (market_share / 100)


def calculate_recent_company_avg(raw_df, demand_col, market_share, months=6):
    """
    최근 N개월 전국 실제 수요 평균을 회사 기준 평균 수요로 환산

    평소 회사 수요 수준을 추정하는 기준으로 사용

    최근 회사 평균 수요 = 최근 N개월 전국 평균 수요 * (회사 시장점유율 / 100)
    """
    recent_national_avg = (
        raw_df.sort_values("date")[demand_col]
        .dropna()
        .tail(months)
        .mean()
    )
    return recent_national_avg * (market_share / 100)


def calculate_demand_change_rate(company_ai_demand, recent_company_avg):
    """
    회사 AI 예측 수요가 최근 평균 대비 얼마나 증감했는지 계산

    수요 변화 신호를 탐지하는 데 사용

    수요 변화율 = (회사 AI 예측 수요 / 최근 회사 평균 수요 - 1) * 100
    """
    if recent_company_avg <= 0 or pd.isna(recent_company_avg):
        return 0

    return (company_ai_demand / recent_company_avg - 1) * 100


def calculate_plan_gap(planned_production, company_ai_demand):
    """
    회사 생산계획과 회사 AI 예측 수요의 차이를 계산

    계획이 예측 수요 대비 부족한지 많은지 판단하는 데 사용

    계획 차이 = 회사 생산계획 - 회사 AI 예측 수요
    """
    return planned_production - company_ai_demand


def calculate_expected_ending_stock(current_stock, planned_production, company_ai_demand):
    """
    생산계획 실행 후 예상 월말 재고를 계산

    목표 재고 대비 부족 또는 여유 리스크를 판단하는 기준값으로 사용

    예상 월말 재고 = 회사 현재 재고 + 회사 생산계획 - 회사 AI 예측 수요
    """
    return current_stock + planned_production - company_ai_demand


def calculate_stock_gap(expected_ending_stock, target_stock):
    """
    예상 월말 재고와 회사 목표 재고의 차이를 계산

    재고 부족 여부를 판단하고 리스크 점수에 반영하는 데 사용

    재고 차이 = 예상 월말 재고 - 회사 목표 재고
    """
    return expected_ending_stock - target_stock


def calculate_risk_score(
    demand_change_rate,
    plan_gap,
    company_ai_demand,
    stock_gap,
    target_stock,
):
    """
    수요 변화, 계획 차이, 재고 부족 신호를 종합해 리스크 점수를 계산

    품목별 검토 우선순위를 정렬하고 위험도를 분류하는 데 사용

    리스크 점수 = 수요 변화 점수 + 계획 차이 점수 + 재고 부족 점수
    """
    demand_change_score = min(abs(demand_change_rate) / 15 * 30, 30)

    plan_gap_rate = abs(plan_gap) / max(company_ai_demand, 1)
    plan_gap_score = min(plan_gap_rate / 0.15 * 30, 30)

    stock_shortage_rate = max(-stock_gap, 0) / max(target_stock, 1)
    stock_risk_score = min(stock_shortage_rate / 0.3 * 40, 40)

    return round(demand_change_score + plan_gap_score + stock_risk_score, 1)


def make_risk_signals(demand_change_rate, plan_gap, stock_gap):
    """
    계산된 수치를 사람이 이해하기 쉬운 리스크 신호로 변환

    대시보드의 주요 신호 컬럼과 상세 페이지 판단 근거로 사용

    주요 신호 = 수요 변화 + 계획 차이 + 재고 차이
    """
    signals = []

    if demand_change_rate >= 10:
        signals.append("수요 증가")
    elif demand_change_rate <= -10:
        signals.append("수요 감소")

    if plan_gap < 0:
        signals.append("계획 부족")
    elif plan_gap > 0:
        signals.append("계획 여유")

    if stock_gap < 0:
        signals.append("재고 부족")
    elif stock_gap > 0:
        signals.append("재고 여유")

    return signals


def make_review_direction(demand_change_rate, plan_gap, stock_gap):
    """
    수요 변화, 계획 차이, 재고 차이를 기준으로 검토 방향을 분류

    대시보드의 검토 방향 컬럼에 사용

    검토 방향 = 생산계획 상향 검토 / 재고 보강 검토 / 수요 변화 모니터링 / 모니터링
    """
    if stock_gap < 0 and plan_gap < 0:
        return "생산계획 상향 검토"

    if stock_gap < 0:
        return "재고 보강 검토"

    if demand_change_rate >= 10 and plan_gap < 0:
        return "수요 증가 모니터링"

    if demand_change_rate <= -10 and plan_gap > 0:
        return "과잉 가능성 확인"

    if abs(demand_change_rate) >= 10:
        return "수요 변화 모니터링"

    return "모니터링"


def make_priority_level(risk_score):
    """
    리스크 점수를 높음/보통/낮음 등급으로 변환

    대시보드와 품목 상세 페이지의 위험도 배지에 사용

    우선순위 등급 = 높음 / 보통 / 낮음
    """
    if risk_score >= 70:
        return "높음"

    if risk_score >= 40:
        return "보통"

    return "낮음"


def make_reason_text(item_code, stock_gap, signals):
    """
    품목별 리스크 판단 근거 문구를 생성

    품목 상세 페이지의 검토 사유와 대시보드 해석 문구에 사용

    판단 근거 = 주요 신호 + 재고 부족 여부 + 현업 검토 안내
    """
    messages = []

    if "수요 증가" in signals:
        messages.append(f"{item_code}는 최근 평균 대비 수요 증가 신호가 있습니다.")
    elif "수요 감소" in signals:
        messages.append(f"{item_code}는 최근 평균 대비 수요 감소 신호가 있습니다.")

    if "계획 부족" in signals:
        messages.append("현재 생산계획은 AI 예측 수요보다 낮습니다.")
    elif "계획 여유" in signals:
        messages.append("현재 생산계획은 AI 예측 수요보다 높습니다.")

    if stock_gap < 0:
        messages.append(f"예상 월말 재고가 목표 재고보다 {abs(stock_gap):.1f} 부족합니다.")
    else:
        messages.append("예상 월말 재고가 목표 재고를 충족합니다.")

    messages.append("현업 정보를 반영해 검토 우선순위를 판단하세요.")

    return " ".join(messages)


def build_item_risk_result(
    item_code,
    item_name,
    forecast_month,
    latest_data_month,
    national_ai_demand,
    market_share,
    planned_production,
    current_stock,
    target_stock,
    raw_df,
    demand_col,
    recent_months=6,
):
    """
    품목별 생산 및 재고 리스크 결과를 생성

    대시보드 테이블과 품목 상세 페이지에 전달할 품목별 결과 데이터 생성에 사용

    품목별 결과 = AI 예측 + 생산계획 + 재고 기준을 종합한 리스크 모니터링 결과
    """
    company_ai_demand = calculate_company_ai_demand(national_ai_demand, market_share)
    recent_company_avg = calculate_recent_company_avg(
        raw_df,
        demand_col,
        market_share,
        recent_months,
    )
    demand_change_rate = calculate_demand_change_rate(
        company_ai_demand,
        recent_company_avg,
    )
    plan_gap = calculate_plan_gap(planned_production, company_ai_demand)
    expected_ending_stock = calculate_expected_ending_stock(
        current_stock,
        planned_production,
        company_ai_demand,
    )
    stock_gap = calculate_stock_gap(expected_ending_stock, target_stock)
    risk_score = calculate_risk_score(
        demand_change_rate,
        plan_gap,
        company_ai_demand,
        stock_gap,
        target_stock,
    )
    signals = make_risk_signals(demand_change_rate, plan_gap, stock_gap)

    return {
        "item_code": item_code,
        "item_name": item_name,
        "latest_data_month": latest_data_month,
        "forecast_month": forecast_month,
        "national_ai_demand": round(national_ai_demand, 1),
        "market_share": round(market_share, 2),
        "company_ai_demand": round(company_ai_demand, 1),
        "recent_company_avg": round(recent_company_avg, 1),
        "demand_change_rate": round(demand_change_rate, 1),
        "planned_production": round(planned_production, 1),
        "plan_gap": round(plan_gap, 1),
        "current_stock": round(current_stock, 1),
        "target_stock": round(target_stock, 1),
        "expected_ending_stock": round(expected_ending_stock, 1),
        "stock_gap": round(stock_gap, 1),
        "risk_score": risk_score,
        "priority_level": make_priority_level(risk_score),
        "risk_signals": signals,
        "review_direction": make_review_direction(
            demand_change_rate,
            plan_gap,
            stock_gap,
        ),
        "reason": make_reason_text(item_code, stock_gap, signals),
    }


def build_risk_dashboard(item_results):
    """
    여러 품목의 리스크 결과를 대시보드 형태로 집계

    리스크 분석 결과 대시보드의 KPI 카드와 품목별 우선순위 테이블에 사용

    대시보드 = 요약 KPI + 리스크 점수순 품목 리스트
    """
    sorted_results = sorted(
        item_results,
        key=lambda row: row["risk_score"],
        reverse=True,
    )

    for idx, row in enumerate(sorted_results, start=1):
        row["priority_rank"] = idx

    return {
        "summary": {
            "total_items": len(sorted_results),
            "high_priority_count": sum(
                row["priority_level"] == "높음"
                for row in sorted_results
            ),
            "demand_signal_count": sum(
                "수요 증가" in row["risk_signals"]
                or "수요 감소" in row["risk_signals"]
                for row in sorted_results
            ),
            "stock_risk_count": sum(
                row["stock_gap"] < 0
                for row in sorted_results
            ),
            "normal_monitoring_count": sum(
                row["review_direction"] == "모니터링"
                for row in sorted_results
            ),
        },
        "items": sorted_results,
    }
