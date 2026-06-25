from src.service import get_item_risk_detail, get_monitoring_context, run_plan_risk_monitoring
import json


context = get_monitoring_context()

print("========== 기준 월 정보 ==========")
print(json.dumps(context, ensure_ascii=False, indent=2))


input_rows = [
    {
        "item_code": "HR",
        "planned_production": 130,
        "current_stock": 40,
        "target_stock": 30,
        "market_share": 10,
    },
    {
        "item_code": "CR",
        "planned_production": 65,
        "current_stock": 8,
        "target_stock": 7,
        "market_share": 10,
    },
    {
        "item_code": "GI",
        "planned_production": 70,
        "current_stock": 12,
        "target_stock": 10,
        "market_share": 9,
    },
]


result = run_plan_risk_monitoring(input_rows)

print("\n========== 리스크 대시보드 요약 ==========")
print(json.dumps(result["summary"], ensure_ascii=False, indent=2))

print("\n========== 품목별 리스크 결과 ==========")
for item in result["items"]:
    print(
        item["priority_rank"],
        item["item_code"],
        "전국 AI 예측 수요:",
        item["national_ai_demand"],
        "회사 AI 예측 수요:",
        item["company_ai_demand"],
        "최근 평균 대비 증감률:",
        f'{item["demand_change_rate"]}%',
        "기존 계획:",
        item["planned_production"],
        "계획 차이:",
        item["plan_gap"],
        "현재 재고:",
        item["current_stock"],
        "예상 월말 재고:",
        item["expected_ending_stock"],
        "재고 차이:",
        item["stock_gap"],
        "리스크 점수:",
        item["risk_score"],
        "주요 신호:",
        ", ".join(item["risk_signals"]),
        "검토 방향:",
        item["review_direction"],
    )


detail = get_item_risk_detail("CR", result)

print("\n========== CR 상세 결과 ==========")
print(json.dumps(detail, ensure_ascii=False, indent=2))
