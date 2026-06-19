# SteelForecast - 철강재 수요예측 플랫폼

AI-powered steel demand forecasting platform for inventory risk analysis and production planning

철강재의 월별 수요를 예측하고,
예측 결과를 기반으로 재고 부족 위험도와 자사 생산 가이드라인을 제공하는
AI 기반 원자재 수요예측 플랫폼입니다.

---

## 프로젝트 소개

철강재는 자동차, 건설, 가전 등 다양한 제조 산업에서 사용되는 핵심 원자재입니다.

본 프로젝트는 과거 철강 수요 데이터와 외부 산업 지표를 활용하여 다음 달 수요를 예측하고,
예측 결과를 재고 관리와 생산 계획에 연결하는 것을 목표로 구현하였습니다.

수요량만 예측하는 것이 아니라, 예측 수요를 기반으로
부족 예상 수량, 위험도, 재고 유지 가능기간, 자사 생산 권장량까지
제공하는 의사결정 지원 플랫폼입니다.

---

## 데이터셋

### 철강 데이터

- 열연강판, 냉연강판, 아연도강판 월별 데이터
- 생산량
- 재고량
- 출하량

### 외부 산업 지표

- 자동차 생산량
- 자동차 내수 출하량
- 자동차 수출 출하량
- 건설 수주액
- 가전 생산지수
- 가전 출하지수
- 철강 산업 생산능력지수
- 철강 산업 가동률지수
- 환율
- 경기종합지수
- 국고채금리
- 철광석 가격

### 자사 업로드 데이터 템플릿

- 월별 출하량
- 재고량
- 엑셀 업로드 기반 입력 지원

---

## 주요 기능

- 다음 달 철강재 수요 증감률 예측
- 예측 증감률 기반 예측 수요량 계산
- 전국 재고 부족량 및 안전재고 계산
- 위험도 분석
- 주요 영향 산업 분석
- 실제 수요 / 예측 수요 차트 데이터 생성
- 자사 시장점유율 기반 예상 수요 계산
- 자사 출하 이력 기반 시장점유율 추정
- 자사 생산 권장량 산출
- 엑셀 업로드 기반 자사 데이터 입력

---

## 프로젝트 기간

2026.06.01 ~ 진행중

## 프로젝트 인원

3명

## 담당 역할

- 데이터 수집 및 전처리
- 수요예측 모델 개발
- 다음 달 수요 증감률 로직 구현
- 재고 부족량 및 위험도 분석 로직 구현
- 자사 생산/재고 계산 및 가이드라인 제공 로직 구현
- 서비스 모듈 구조 설계 및 Python 코드 구현

---

## 사용 기술

### Language

- Python

### Data Processing

- Pandas
- NumPy

### Machine Learning

- Scikit-learn
- RandomForest
- XGBoost
- LightGBM

### Model Management

- Joblib

### Config / Data

- YAML
- CSV
- Excel

### Service Logic

- Python Module
- JSON Response

---

## 시스템 구조

### 전국 수요 예측

```text
품목 선택
    ↓
품목별 설정 로드
    ↓
원본 데이터 / 학습 데이터 로드
    ↓
학습된 모델 로드
    ↓
최근 월 데이터 입력
    ↓
다음 달 수요 증감률 예측
    ↓
다음 달 예측 수요량 계산
```

### 재고 위험도 분석

```text
다음 달 예측 수요
    ↓
현재 재고 조회
    ↓
최근 12개월 수요 표준편차 계산
    ↓
안전재고 계산
    ↓
부족 예상 수량 계산
    ↓
재고 유지 가능 기간 계산
    ↓
위험도 등급 산출
```

### 자사 가이드라인

```text
전국 예측 수요
    ↓
자사 시장 점유율 또는 출하 이력 입력
    ↓
자사 예상 수요 계산
    ↓
자사 안전재고 계산
    ↓
자사 부족 수량 계산
    ↓
수율 및 최소 생산단위 반영
    ↓
최종 권장 생산량 산출
```

---

## 주요 기능

### 1. 다음 달 수요 예측

최근 월 데이터를 기반으로 전국 기준 다음 달 수요 증감률을 예측합니다.

예측된 증감률은 최근 실제 수요량에 반영하여 다음 달 예측 수요량으로 변환합니다.

제공 정보

- 예측 대상 월
- 다음 달 수요 증감률
- 다음 달 전국 예측 수요량

예시

```text
{
    "forecast_month": "2026-04",
    "national_forecast_change_rate": 2.8,
    "national_forecast_demand": 731
}
```

---

### 2. 재고 상태 분석

예측 수요와 현재 재고를 비교하여 전국 기준 재고 상태를 분석합니다.

제공 정보

- 현재 재고량
- 안전 재고
- 부족 예상 수량

```text
{
    "national_current_stock": 603,
    "national_safety_stock": 88,
    "national_shortage_qty": 216
}
```

---

### 3. 위험도 분석

전국 예측 수요와 현재 재고를 기준으로 위험도를 산출합니다.
주요 영향 산업은 모델의 변수 중요도를 산업군별로 묶어,
예측 과정에서 중요하게 활용한 산업군의 상대적 중요도를 제공합니다.

위험도 기준

- HIGH: 재고 유지 가능 기간이 1개월 이하
- MEDIUM: 재고 유지 가능 기간이 3개월 이하
- LOW: 부족 위험이 낮은 상태

제공 정보

- 위험도 등급
- 부족 예상 수량
- 부족 예상 시점
- 재고 유지 가능 개월 수
- 산업명
- 산업별 중요도
- 산업별 영향 비중

예시

```text
{
    "risk_level": "HIGH",
    "national_shortage_qty": 216,
    "shortage_month": "2026년 04월",
    "available_months": 0.8,
    "main_industries": [
      {
        "industry": "자동차",
        "importance": 14.82,
        "importance_pct": 55.5
      },
      {
        "industry": "건설",
        "importance": 7.7,
        "importance_pct": 28.9
      },
      {
        "industry": "가전",
        "importance": 4.16,
        "importance_pct": 15.6
      }
    ]
}
```
※ 변수 중요도는 모델이 예측에 활용한 상대적 중요도를 의미하며, 실제 수요 변화의 직접적인 원인을 의미하지 않습니다.

---

### 4. 수요 예측 주요 영향 변수 제공

전국 수요 예측 모델의 변수 중요도를 기반으로,
모델이 다음 달 수요를 예측할 때 중요하게 활용한 요인을 제공합니다.

제공 정보

- 변수명
- 사용자용 표시 이름
- 예측 중요도

예시

```text
[
    {
      "feature": "CR_demand",
      "display_name": "최근 수요량",
      "importance": 0.11
    },
    {
      "feature": "month",
      "display_name": "월(계절성)",
      "importance": 0.11
    },
    {
      "feature": "CR_demand_ma3",
      "display_name": "최근 3개월 평균 수요량",
      "importance": 0.1
    }
]
```
※ 변수 중요도는 모델이 예측에 활용한 상대적 중요도를 의미하며, 실제 수요 변화의 직접적인 원인을 의미하지 않습니다.


---

### 5. 차트 데이터 생성

대시보드에서 실제 수요와 예측 수요를 시각화할 수 있도록 차트 데이터를 생성합니다.

제공 정보

- 날짜
- 월별 실제 수요
- 월별 예측 수요

예시

```text
[
  {
    "date": "2026-03",
    "actual_demand": 711,
    "forecast_demand": 708
  },
  {
    "date": "2026-04",
    "actual_demand": null,
    "forecast_demand": 731
  }
]
```

---

### 6. 자사 생산/재고 가이드라인

전국 예측 수요를 기반으로 자사 수요를 계산하고,
현재 재고와 리드타임 등을 고려하여 권장 생산량을 계산합니다.

제공 정보

- 자사 예상 수요
- 자사 시장점유율
- 자사 안전재고
- 자사 목표재고
- 자사 부족 수량
- 재고 위험 상태
- 필요 생산량
- 권장 생산량
- 생산능력 초과 여부

예시

```text
{
    "company_forecast_demand": 37,
    "company_market_share": 5.09,
    "company_safety_stock": 6,
    "company_target_stock": 44,
    "company_shortage_qty": 14,
    "company_risk_level": "부족",
    "company_required_production": 14,
    "company_recommended_production": 20,
    "company_capacity_status": "정상"
}
```

---

### 7. 엑셀 업로드 기반 자사 데이터 입력

사용자의 편의를 위해 월별 출하량과 재고를 엑셀 파일로 업로드 하는 입력 방법을 제공합니다.

지원 컬럼

|구분|컬럼명|
|----|----|
|날짜|date|
|출하량|shipment|
|재고량|stock|

---

## 모델링 방식

본 프로젝트에서는 다음 달 수요량을 직접 예측하는 방식이 아닌,
다음 달 수요 증감률을 예측한 뒤 최근 수요량에 반영하여 예측 수요량을 계산하는 방식을 사용했습니다.

```text
최근 실제 수요량
      ↓
다음 달 증감률 예측
      ↓
예측 수요량 변환
```

예측 수요 계산 방식

```python
forecast_demand = current_demand * (1 + forecast_change_rate / 100)
```

이 방식을 사용한 이유

- 월별 수요량의 절대값 변동이 큼
- 실제 서비스에서 "수요 증가/감소"를 직관적으로 보여줄 수 있음

---

## 모델 성능

열연강판 수요 예측 모델(RandomForest) 기준 성능입니다.

|구분|MAE(%p)|RMSE(%p)|R² Score|
|------|------|------|------|
|평균 성능|5.52|7.11|0.33|
|최신 검증 성능(Fold 4)|4.80|6.10|0.46|

※ MAE는 수요 증감률 예측 오차를 의미하며,
평균적으로 약 ±5.5%p 수준의 오차를 보였습니다.

---

## 프로젝트 결과

- 다음 달 철강재 별 수요 증감률 예측 기능 구현
- 예측 증감률 기반 예측 수요량 계산 기능 구현
- 전국 재고 부족량 및 안전재고 계산 기능 구현
- 전국 재고 부족 위험도 분석 기능 구현
- 변수 중요도 기반 주요 영향 산업 분석 기능 구현
- 실제 수요 / 예측 수요 차트 데이터 생성 기능 구현
- 자사 시장점유율 및 출하 이력 기반 생산 가이드라인 제공 기능 구현
- 엑셀 업로드 기반 자사 데이터 입력 기능 구현

---

## 프로젝트 서비스 파일 구조

```text
steel-forecast-demand/
├── configs/ 
│     └── items.yaml
│ 
├── data/
│     ├── raw/
|     |    └── steel_demand.csv
|     |
│     └── processed
│          ├── hr_train_df.csv
│          ├── cr_train_df.csv
│          └── gi_train_df.csv
│ 
├── models/
│     ├── HR/
|     |    ├── hr_feature_importances.csv
│     |    ├── hr_features.py
│     |    ├── hr_metrics.json
│     |    ├── hr_predictions.csv
│     |    └── hr_rf_model.pkl
|     |
│     ├── CR/
|     |    ├── cr_feature_importances.csv
│     |    ├── cr_features.py
│     |    ├── cr_metrics.json
│     |    ├── cr_predictions.csv
│     |    └── cr_rf_model.pkl
|     |
│     └── GI/
|          ├── gi_feature_importances.csv
│          ├── gi_features.py
│          ├── gi_metrics.json
│          ├── gi_predictions.csv
│          └── gi_rf_model.pkl
|     
├── src/
│     ├── config_loader.py
│     ├── data_loader.py
│     ├── predict.py
│     ├── inventory.py
│     ├── risk_analysis.py
│     ├── company_plan.py
│     ├── chart.py
│     ├── upload_parser.py
│     └── service.py
│
├── main.py
├── data.xlsx
├── README.md
└── requirements.txt
```

---

## 핵심 모듈 설명

### config_loader.py

- 품목별 설정 정보를 로드합니다.

### data_loader.py

- 원본 및 학습 데이터를 로드합니다.

### predict.py

- 학습된 모델을 불러와 다음 달 수요 증감률과 수요량을 계산합니다.

### inventory.py

- 현재 재고, 안전 재고, 부족 예상 수량을 계산합니다.

### risk_analysis.py

- 현재 재고, 예측 수요량, 부족 예상 수량을 기반으로 위험도를 분석합니다.

### company_plan.py

- 자사 점유율 기반으로 수요, 생산 권장량 등을 계산합니다.

### chart.py

- 대시보드 시각화를 위한 실제 수요 / 예측 수요 데이터를 생성합니다.

### upload_parser.py

- 엑셀 업로드 파일에서 월별 출하량과 재고량을 추출합니다.

### service.py

- 전체 기능을 통합하여 서비스 결과를 반환합니다.

### main.py

- 테스트 파일입니다.

### data.xlsx

- 엑셀 형식 템플릿입니다.

---

## 실행 방법

### 라이브러리 설치

```bash
pip install pandas numpy scikit-learn xgboost joblib pyyaml openpyxl
```

또는

```bash
pip install -r requirements.txt
```

### 전국 수요 예측 및 위험도 분석 실행 예시

```python
from src.service import get_item_result
import json

result = get_item_result(
  item_code = "CR",
  start_date = "2024-01",
  end_date = "2026-03"
)

print(json.dumps(result, ensure_ascii = False, indent = 2))
```

### 자사 가이드라인 실행 예시

- 데이터 수동 입력

```python
from src.service import get_company_guideline
import json

result = get_company_guideline(
  item_code = "CR",
  company_stock = 30,
  lead_time = 2,
  shipment_history = [32, 35, 38, 36, 40, 37],
  yield_rate = 95,
  service_level = 95,
  max_capacity = 100,
  lot_size = 10
)

print(json.dumps(result, ensure_ascii = False, indent = 2))
```

- 엑셀 데이터 업로드 활용

```python
from src.upload_parser import load_company_shipments_from_excel
from src.service import get_company_guideline
import json

upload_data = load_company_shipments_from_excel("data.xlsx")

result = get_company_guideline(
  item_code = "CR",
  company_stock = upload_data["current_stock"],
  lead_time = 2,
  shipment_history = upload_data["monthly_shipments"],
  yield_rate = 95,
  service_level = 95,
  max_capacity = 100,
  lot_size = 10
)

print(json.dumps(result, ensure_ascii = False, indent = 2))
```

---

## 기대효과

- 철강재 수요 변동에 대한 사전 대응 가능
- 재고 부족 위험을 조기에 파악
- 과잉 재고로 인한 보관비용 감소 효과
- 생산 부족 문제 완화
- 예측 결과를 실제 생산 계획에 연결
- 제조업 의사결정 지원 서비스 구현 경험 확보

## 향후 개선 사항

- 철강재 품목 추가
- 예측 결과 신뢰구간 제공
- 재고 부족 알림 기능 추가
- 실제 ERP / MES 데이터 연동
- 모델 성능 모니터링 및 주기적 재학습 파이프라인 구축
