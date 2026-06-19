# 철강 수요 예측 서비스 모듈

## 개요

냉연강판(CR) 등의 품목(추가 예정)에 대해 다음 기능을 제공합니다.

- 다음 달 수요 예측
- 현재 재고 조회
- 안전재고 계산
- 재고 부족 여부 판단
- 실제 수요량 / 예측 수요량 그래프 데이터

---

## 구조

```text
project/
├─ configs/
│  └─ items.yaml
│
├─ data/
│  ├─ raw/
│  │  └─ steel_demand.csv
│  └─ processed/
│     └─ cr_train_df.csv
│
├─ models/
│  └─ CR/
│     ├─ cr_rf_model.pkl
│     ├─ features.pkl
│     ├─ metrics.json
│     ├─ feature_importance.csv
│     └─ predictions.csv
│
├─ src/
│  ├─ config_loader.py
│  ├─ data_loader.py
│  ├─ predict.py
│  ├─ inventory.py
│  ├─ chart.py
│  └─ service.py
│
└─ requirements.txt
```

---

## 사용 방법

---

```python
from src.service import get_item_result

result = get_item_result(
    item_code="CR",
    start_date="2024-01",
    end_date="2026-03"
)
```

---

## 입력 파라미터

| 파라미터 		| 설명 			|
|-------------------	|-------------------	------	|
| item_code 	| 품목 코드 			|
| start_date 		| 그래프 시작 기간 	|
| end_date 		| 그래프 종료 기간 	|

### 품목 코드

| 코드 	| 품목 	|
|------------	|------------	|
| CR 		| 냉연강판 	|
| HR 		| 열연강판 	|
| GI 		| 아연도강판 |

---

## 반환 데이터

### 예시

```python
{
    "item_code": "CR",
    "item_name": "냉연강판",

    "forecast_month": "2026-04",

    "summary": {
        "forecast_month": "2026-04",
        "predicted_change_rate": 2.8,
        "predicted_demand": 731,
        "current_stock": 603,
        "safety_stock": 106,
        "shortage_qty": 234,
        "risk_level": "부족"
    },

    "model_info": {
        "model_name": "RandomForest",
        "avg_metrics": {
            "mae": 6.22,
            "rmse": 7.70,
            "r2": 0.22
        }
    },

    "chart_data": [
        {
            "date": "2024-01",
            "actual_demand": 746,
            "predicted_demand": 711
        }
    ]
}
```

---


## summary 설명

| 필드 			 | 설명 			|
|---------------------------|-------------------------|
| forecast_month		 | 예측 대상 월 		|
| predicted_change_rate | 예측 증감률 (%) 	|
| predicted_demand 	 | 다음달 예측 수요량	|
| current_stock 		 | 현재 재고	 		|
| safety_stock 		 | 안전재고 			|
| shortage_qty 		 | 예상 부족 수량 		|
| risk_level 			 | 정상 / 부족 		|

---

## chart_data 설명

| 필드 			| 설명 		|
|--------------------------|-------------------	|
| date 			| 기준 월 		|
| actual_demand 		| 실제 수요량 	|
| predicted_demand 	| 예측 수요량 	|

그래프 시각화 시

- actual_demand : 실제 수요 추이
- predicted_demand : 예측 수요 추이

로 사용합니다.

---

## 모델 성능

### 냉연강판(CR)

| 지표 		| 값 		|
|-------------------	|------------	|
| 평균 MAE 	| 6.22%p 	|
| 평균 RMSE 	| 7.70%p 	|
| 평균 R² 		| 0.22 	|

---

## 설치

```bash
pip install -r requirements.txt
```

### requirements.txt

```text
pandas
numpy
scikit-learn
joblib
pyyaml
xgboost
```

---

# 기업 생산·재고 가이드

사용자가 입력한 재고, 출하량, 시장점유율 정보를 기반으로 생산·재고 관리 가이드를 제공합니다.

## 사용 방법

```python
from src.service import get_company_guideline

result = get_company_guideline(
    item_code="CR",

    company_stock=30,

    monthly_shipments=[
        32,35,31,38,36,34,
        40,37,35,33,39,36
    ],

    lead_time=2,
    yield_rate=95,
    service_level=95,

    std_period=12,

    max_capacity=100,
    lot_size=10
)
```

---

## 입력 파라미터

| 파라미터 | 설명 | 필수 |
|----------|----------|----------|
| item_code | 품목 코드 | O |
| company_stock | 현재 재고량 | O |
| lead_time | 리드타임(월) | O |
| yield_rate | 공정 수율(%) | O |
| service_level | 서비스율(%) | O |
| market_share | 시장점유율(%) | 조건부 |
| monthly_shipments | 월별 출하량 리스트 | 조건부 |
| demand_std | 수요 표준편차 | 조건부 |
| std_period | 변동성 계산 기간(3/6/12개월) | X |
| max_capacity | 월 최대 생산능력 | X |
| lot_size | 최소 생산단위 | X |

---

## 입력 조건

다음 중 하나는 반드시 입력해야 합니다.

### 방법 1

```python
market_share=5
demand_std=4.5
```

### 방법 2

```python
monthly_shipments=[
    ...
]
```

---

## 반환 데이터 예시

```json
{
    "item_code": "CR",
    "item_name": "냉연강판",

    "forecast_month": "2026-04",

    "national_predicted_demand": 731,
    "national_predicted_change_rate": 2.8,

    "production_guideline": {

        "company_expected_demand": 36,

        "company_stock": 30,

        "company_safety_stock": 6,

        "company_shortage_qty": 12,

        "final_recommended_production": 20,

        "risk_level": "부족"
    }
}
```

---

# production_guideline 설명

| 필드 | 설명 |
|----------|----------|
| company_expected_demand | 자사 예상 수요량 |
| company_stock | 현재 재고량 |
| company_demand_std | 수요 표준편차 |
| company_safety_stock | 안전재고 |
| company_target_stock | 목표 재고 |
| company_shortage_qty | 부족 수량 |
| required_production | 수율 반영 전 필요 생산량 |
| final_recommended_production | 최종 권장 생산량 |
| risk_level | 정상 / 부족 |
| capacity_status | 생산능력 상태 |
| capacity_over_qty | 생산능력 초과 수량 |

---

# 계산식

## 안전재고

```text
안전재고 = Z값 × 수요 표준편차 × √리드타임
```

---

## 목표 재고

```text
목표 재고 = 예상 수요량 + 안전재고
```

---

## 부족 수량

```text
부족 수량 = 목표 재고 - 현재 재고
```

---

## 필요 생산량

```text
필요 생산량 = 부족 수량 ÷ 공정 수율
```

---

## 최종 권장 생산량

```text
최종 권장 생산량
=
최소 생산단위를 반영한 생산량
```

---

# 엑셀 업로드

## 템플릿 형식

```csv
date,shipment,stock
2025-04,32,25
2025-05,35,28
2025-06,31,24
2025-07,38,30
2025-08,36,27
2025-09,34,29
2025-10,40,35
2025-11,37,33
2025-12,35,31
2026-01,33,28
2026-02,39,34
2026-03,36,30
```

---

## 업로드 예시

```python
from src.upload_parser import (
    load_company_shipments_from_excel
)

upload_data = load_company_shipments_from_excel(
    "data.xlsx"
)

result = get_company_guideline(
    item_code="CR",

    company_stock=upload_data["current_stock"],

    monthly_shipments=upload_data["monthly_shipments"],

    lead_time=2,
    yield_rate=95,
    service_level=95
)
```

---

# 향후 확장 계획

- 열연강판(HR) 수요 예측
- 아연도강판(GI) 수요 예측
- 품목별 생산계획 비교
- 시나리오 분석
- 적정 재고량 시뮬레이션
- 재고 부족 알림 기능
- 발주 추천 기능