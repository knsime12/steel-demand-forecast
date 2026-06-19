import numpy as np
import math

def get_z_value(service_level=95):
    z_map = {
        90: 1.28,
        95: 1.65,
        98: 2.05,
        99: 2.33
    }

    return z_map.get(service_level, 1.65)


# 전국 예측 수요를 자사 예측 수요로 환산
def calculate_company_forecast_demand(
    national_forecast_demand,
    national_demand_history=None,
    company_market_share=None,
    company_shipment_history=None,
    share_period=12
):
    # 1. 자사 시장점유율을 직접 입력한 경우
    if company_market_share is not None:
        company_demand_ratio = company_market_share / 100
        company_market_share_value = company_market_share

        demand_method = "market_share"
        demand_method_name = "시장점유율 직접 입력 기준"

    # 2. 자사 출하 이력과 전국 수요 이력으로 시장점유율을 추정하는 경우
    elif company_shipment_history is not None and len(company_shipment_history) > 0:

        if national_demand_history is None or len(national_demand_history) == 0:
            raise ValueError("출하량 기반 점유율 추정을 위해 전국 수요 이력이 필요합니다.")

        company_recent_shipments = company_shipment_history[-share_period:]
        national_recent_demands = national_demand_history[-share_period:]

        period = min(
            len(company_recent_shipments),
            len(national_recent_demands)
        )

        if period < 1:
            raise ValueError("점유율 추정에 사용할 데이터가 부족합니다.")

        company_recent_shipments = company_recent_shipments[-period:]
        national_recent_demands = national_recent_demands[-period:]

        company_total_shipment = np.sum(company_recent_shipments)
        national_total_demand = np.sum(national_recent_demands)

        if national_total_demand <= 0:
            raise ValueError("최근 전국 수요 합계가 0 이하입니다.")

        company_demand_ratio = company_total_shipment / national_total_demand
        company_market_share_value = company_demand_ratio * 100

        demand_method = "estimated_market_share"
        demand_method_name = f"최근 {period}개월 출하량 기반 점유율 추정"

    else:
        raise ValueError("시장점유율 또는 자사 출하 이력 중 하나는 필요합니다.")

    # 전국 예측 수요 × 자사 점유율 = 자사 예측 수요
    company_forecast_demand = (
        national_forecast_demand *
        company_demand_ratio
    )

    return (
        float(company_forecast_demand),
        demand_method,
        demand_method_name,
        float(company_demand_ratio),
        round(float(company_market_share_value), 2)
    )


# 자사 수요 변동성 계산
def calculate_company_demand_std(
    company_forecast_demand,
    company_shipment_history=None,
    company_demand_volatility_rate=None,
    company_demand_std=None,
    std_period=12
):
    # 1. 자사 수요 표준편차를 직접 입력한 경우
    if company_demand_std is not None:
        return (
            float(company_demand_std),
            "direct_input",
            "수요 변동성 직접 입력"
        )

    # 2. 자사 수요 변동성 비율을 입력한 경우
    if company_demand_volatility_rate is not None:
        company_std = (
            company_forecast_demand *
            (company_demand_volatility_rate / 100)
        )

        return (
            float(company_std),
            "volatility_rate",
            f"입력 수요변동성 {company_demand_volatility_rate}% 기준"
        )

    # 3. 자사 출하 이력이 부족한 경우
    if company_shipment_history is None or len(company_shipment_history) < 2:
        return (
            0.0,
            "not_provided",
            "수요 변동성 미입력"
        )

    # 4. 최근 자사 출하 이력 기준 표준편차 계산
    company_recent_shipments = company_shipment_history[-std_period:]

    if len(company_recent_shipments) < 2:
        return (
            0.0,
            "not_enough_data",
            "출하량 데이터 부족"
        )

    company_std = np.std(company_recent_shipments, ddof=1)

    return (
        float(company_std),
        f"recent_{len(company_recent_shipments)}months",
        f"최근 {len(company_recent_shipments)}개월 출하량 기준"
    )


# 자사 생산/재고 가이드라인 계산
def calculate_company_plan(
    national_forecast_demand,
    company_stock,
    lead_time,
    national_demand_history=None,
    company_market_share=None,
    company_shipment_history=None,
    company_demand_volatility_rate=None,
    company_demand_std=None,
    share_period=12,
    std_period=12,
    yield_rate=100,
    service_level=95,
    max_capacity=None,
    lot_size=None
):
    # 1. 전국 예측 수요를 자사 예측 수요로 환산
    (
        company_forecast_demand,
        demand_method,
        demand_method_name,
        company_demand_ratio,
        company_market_share_value
    ) = calculate_company_forecast_demand(
        national_forecast_demand=national_forecast_demand,
        national_demand_history=national_demand_history,
        company_market_share=company_market_share,
        company_shipment_history=company_shipment_history,
        share_period=share_period
    )

    # 2. 자사 수요 변동성 계산
    (
        company_demand_std_value,
        std_method,
        std_method_name
    ) = calculate_company_demand_std(
        company_forecast_demand=company_forecast_demand,
        company_shipment_history=company_shipment_history,
        company_demand_volatility_rate=company_demand_volatility_rate,
        company_demand_std=company_demand_std,
        std_period=std_period
    )

    # 3. 서비스율 기준 Z값
    z_value = get_z_value(service_level)

    # 4. 자사 안전재고 계산
    company_safety_stock = (
        z_value *
        company_demand_std_value *
        (lead_time ** 0.5)
    )

    # 5. 자사 목표 재고 = 자사 예측 수요 + 안전재고
    company_target_stock = (
        company_forecast_demand +
        company_safety_stock
    )

    # 6. 자사 부족 수량
    company_shortage_qty = max(
        company_target_stock - company_stock,
        0
    )

    # 7. 공정 수율 반영
    yield_rate_value = yield_rate / 100 if yield_rate is not None else 1

    if yield_rate_value <= 0:
        company_required_production = company_shortage_qty
    else:
        company_required_production = (
            company_shortage_qty /
            yield_rate_value
        )

    # 8. 최소 생산 단위 반영
    if lot_size is not None and lot_size > 0:
        company_recommended_production = (
            math.ceil(company_required_production / lot_size) *
            lot_size
        )
    else:
        company_recommended_production = company_required_production

    # 9. 생산능력 검증
    company_capacity_status = "미입력"
    company_capacity_over_qty = 0

    if max_capacity is not None and max_capacity > 0:
        if company_recommended_production > max_capacity:
            company_capacity_status = "생산능력 초과"
            company_capacity_over_qty = (
                company_recommended_production -
                max_capacity
            )
        else:
            company_capacity_status = "정상"

    # 10. 자사 재고 위험 상태
    company_risk_level = (
        "부족"
        if company_shortage_qty > 0
        else "정상"
    )

    return {
        "company_forecast_demand": int(round(company_forecast_demand)),
        "company_demand_ratio": round(company_demand_ratio, 4),
        "company_market_share": company_market_share_value,

        "company_stock": int(round(company_stock)),

        "demand_method": demand_method,
        "demand_method_name": demand_method_name,
        "share_period": share_period,

        "company_demand_std": round(float(company_demand_std_value), 2),
        "std_method": std_method,
        "std_method_name": std_method_name,
        "std_period": std_period,
        "company_demand_volatility_rate": company_demand_volatility_rate,

        "company_safety_stock": int(round(company_safety_stock)),
        "company_target_stock": int(round(company_target_stock)),
        "company_shortage_qty": int(round(company_shortage_qty)),
        "company_risk_level": company_risk_level,

        "company_required_production": int(round(company_required_production)),
        "company_recommended_production": int(round(company_recommended_production)),

        "company_capacity_status": company_capacity_status,
        "company_capacity_over_qty": int(round(company_capacity_over_qty)),

        "service_level": service_level,
        "lead_time": lead_time,
        "yield_rate": yield_rate,
        "max_capacity": max_capacity,
        "lot_size": lot_size
    }