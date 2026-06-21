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

- 열연강판(HR), 냉연강판(CR), 아연도강판(GI) 품목별 다음 달 수요 예측
- 품목별 최적 타겟 유형 적용 및 예측 수요량 복원
  - 실제 수요량(absolute)
  - 수요 증감량(diff)
  - 수요 증감률(rate)
- 실제 수요량과 예측 수요량 기반 차트 데이터 생성
- 전국 기준 현재 재고, 안전재고, 부족 예상 수량 계산
- 예측 수요와 재고 상태를 기반으로 리스크 등급 산출
- 주요 영향 산업 및 변수 중요도 제공
- 모델 성능 지표 제공
  - MAE, RMSE, R², MAPE
  - Hit Rate
  - Turnaround Hit Rate
  - Turnaround Match Rate
  - latest_metrics: 최근 검증 구간 성능(현재 12개월)
  - avg_metrics: 전체 교차검증 평균 성능
- 기업 시장점유율 또는 출하 이력 기반 기업 예상 수요 계산
- 기업별 안전재고, 목표재고, 부족 수량, 권장 생산량 계산
- 엑셀 업로드 기반 기업 출하/재고 데이터 입력 지원

---

## 프로젝트 기간

2026.06.01 ~ 진행중

## 프로젝트 인원

3명

## 담당 역할

- 데이터 수집 및 전처리
- 수요예측 모델 개발
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
- Ridge
- Lasso
- ElasticNet
- RandomForest
- XGBoost
- LightGBM

### Model Validation

- TimeSeriesSplit
- Cross Validation
- GridSearchCV

### Feature Engineering

- Lag Features
- Difference Features
- Moving Average Features
- Shock Dummy Features
- Calendar Dummy Features

### Model Evaluation

- MAE
- RMSE
- R²
- MAPE
- Hit Rate
- Turnaround Hit Rate
- Turnaround Match Rate
- Permutation Importance

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
다음 달 수요 예측
    ↓
target_type에 따라 예측 수요랑 복원
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

## 기능 상세

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

본 프로젝트는 품목별로 다음 달 수요를 예측합니다.

모델은 품목별 실험 결과에 따라 다음 세 가지 타겟 중 적합한 방식을 선택합니다.

| 타겟 유형 | 의미 |
|---|---|
| absolute | 다음 달 실제 수요량 |
| diff | 다음 달 수요량 - 현재 달 수요량 |
| rate | 다음 달 수요 증감률 |

예측 결과는 최종적으로 모두 다음 달 예측 수요량으로 복원됩니다.

예를 들어 'target_type = "diff"'인 경우 :

```python
forecast_demand = current_demand + predicted_diff
```

'target_type = "rate"'인 경우 :

```python
forecast_demand = current_demand * (1 + predicted_rate / 100)
```

---

## 모델 성능 지표

모델 성능은 TimeSeriesSplit 기반 교차검증으로 평가합니다.

`metrics.json`에는 두 종류의 성능이 저장됩니다.

| 구분 | 설명 |
|---|---|
| avg_metrics | 전체 fold 평균 성능 |
| latest_metrics | 가장 최근 fold 성능 |

웹서비스에서는 최근 시장 흐름을 반영하기 위해 `latest_metrics`를 대표 성능으로 표시하고, `avg_metrics`는 보조 지표로 제공합니다.

주요 지표는 다음과 같습니다.

| 지표 | 설명 |
|---|---|
| mae | 평균 절대 오차 |
| rmse | 평균 제곱근 오차 |
| r2 | 결정계수 |
| mape | 평균 절대 백분율 오차 |
| hit_rate | 수요 증가/감소 방향 적중률 |
| turnaround_hit_rate | 실제 전환점 중 예측 전환점 적중률 |
| turnaround_match_rate | 실제/예측 전환점 일치율 |

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
steel-demand-forecast/
├── configs/
│   └── items.yaml
├── data/
│   ├── raw/
│   │   └── steel_demand.csv
│   └── processed/
│       ├── HR/
│       │   ├── train_df.csv
│       │   ├── predictions.csv
│       │   ├── metrics.json
│       │   ├── feature_importances.csv
│       │   └── features.pkl
│       ├── CR/
│       └── GI/
├── models/
│   ├── HR/
│   │   └── model.pkl
│   ├── CR/
│   │   └── model.pkl
│   └── GI/
│       └── model.pkl
├── scripts/
│   ├── train_utils.py
│   ├── experiment.py
│   └── update_item_model.py
├── src/
│   ├── config_loader.py
│   ├── data_loader.py
│   ├── predict.py
│   ├── inventory.py
│   ├── risk_analysis.py
│   ├── company_plan.py
│   ├── chart.py
│   ├── upload_parser.py
│   ├── feature_names.py
│   └── service.py
├── main.py
├── data.xlsx
├── README.md
└── requirements.txt
```

---

## 핵심 모듈 설명

### configs/items.yaml

품목별 설정 파일입니다.

각 품목의 데이터 경로, 모델 경로, 성능 지표 경로, 예측 결과 경로, 수요/재고/생산 컬럼명을 관리합니다.

지원 품목 :

|코드|품목|
|---|---|
|HR|열연강판|
|CR|냉연강판|
|GI|아연도강판|

---

### src/config_loader.py

`configs/items.yaml`에서 품목별 설정 정보를 불러오는 모듈입니다.

서비스 함수에서 품목 코드를 입력받으면 해당 품목의 모델 경로, 데이터 경로, 컬럼명을 이 모듈을 통해 조회합니다.

---

### src/data_loader.py

원본 데이터와 학습용 데이터를 불러오는 모듈입니다.

- `data/raw/steel_demand.csv`
- `data/processed/{item_code}/train_df.csv`

위 데이터를 읽어 서비스 로직에서 사용할 수 있도록 제공합니다.

---

### src/predict.py

저장된 모델을 불러와 다음 달 전국 수요를 예측하는 모듈입니다.

주요 역할:

- `models/{item_code}/model.pkl` 로드
- `data/processed/{item_code}/features.pkl` 로드
- 최신 월 데이터를 기반으로 다음 달 예측값 산출
- `target_type`에 따라 예측값을 실제 수요량으로 복원

타겟 복원 방식:

| target_type | 복원 방식 |
|---|---|
| absolute | 예측값을 다음 달 수요량으로 사용 |
| diff | 현재 수요량 + 예측 증감량 |
| rate | 현재 수요량 × (1 + 예측 증감률 / 100) |

---

### src/inventory.py

전국 기준 재고 상태를 계산하는 모듈입니다.

주요 계산 항목:

- 현재 재고
- 최근 수요 변동성
- 안전재고
- 부족 예상 수량

예측 수요와 현재 재고를 비교해 재고 부족 여부를 판단하는 데 사용됩니다.

---

### src/risk_analysis.py

예측 수요와 재고 상태를 바탕으로 리스크 수준을 분석하는 모듈입니다.

주요 역할:

- 리스크 등급 산출
- 부족 예상 시점 계산
- 재고 유지 가능 개월 수 계산
- 주요 영향 산업 추출

리스크 등급은 대략 다음 기준으로 해석합니다.

| 등급 | 의미 |
|---|---|
| LOW | 재고 부족 위험이 낮음 |
| MEDIUM | 일정 기간 내 재고 부족 가능성 있음 |
| HIGH | 단기 재고 부족 위험 높음 |

---

### src/company_plan.py

기업별 생산/재고 가이드라인을 계산하는 모듈입니다.

전국 예측 수요를 기준으로 기업의 시장 점유율 또는 출하 이력을 반영해 기업의 예상 수요를 계산합니다.

주요 계산 항목 :

- 기업 예상 수요
- 기업 시장점유율
- 기업 안전재고
- 기업 목표재고
- 부족 수량
- 필요 생산량
- 권장 생산량
- 생산능력 초과 여부

---

### src/chart.py

웹 화면에서 사용할 차트 데이터를 생성하는 모듈입니다.

실제 수요량과 예측 수요량을 월별로 정리해 반환합니다.

반환 예시:

```python
[
    {
        "date": "2026-03",
        "actual_demand": 1365,
        "forecast_demand": 1366
    },
    {
        "date": "2026-04",
        "actual_demand": None,
        "forecast_demand": 1359
    }
]
```

---

### src/feature_names.py

모델 변수명을 사용자 친화적인 한글 표시명으로 변환하는 모듈입니다.

예 :

|원본 변수명|표시명|
|---|---|
|HR_demand_diff|열연강판 수요량(전월 대비 증감)|
|CR_inv_lag1|냉연강판 재고량(1개월 전|
|construction_order_amt_diff_shock90|건설 수주액 급변구간|

웹 서비스에서 변수 중요도를 보여줄 때 사용됩니다.

---

### src/upload_parser.py

기업이 업로드한 엑셀 파일에서 출하량과 재고 데이터를 읽는 모듈입니다.

사용 예시 :

```python
from src.upload_parser import load_company_shipments_from_excel

upload_data = load_company_shipments_from_excel("data.xlsx")
```

반환 데이터는 `get_company_guideline()` 의 입력값으로 사용할 수 있습니다.

---

### src/service.py

전체 서비스 결과를 조합하는 핵심 모듈입니다.

주요 함수 :

```python
get_item_result(item_code, start_date, end_date)
```

해당 함수는 다음 정보를 하나의 결과로 묶어 반환합니다.

- 다음 달 전국 수요 예측
- 재고 상태
- 리스크 분석
- 모델 성능 지표
- 변수 중요도
- 차트 데이터

반환 구조 :
```python
{
    "item_code": "HR",
    "item_name": "열연강판",
    "forecast_month": "2026-04",
    "national_forecast": {},
    "inventory_status": {},
    "risk_analysis": {},
    "model_info": {},
    "feature_importance": [],
    "chart_data": []
}
```

---

### scripts/train_utils.py

모델 학습, 검증, 저장 로직을 모아둔 학습 유틸리티 모듈입니다.

주요 역할 :

- 원본 데이터 전처리
- lag, diff, ma, shock_dummy 변수 생성
- 타겟 생성
- 모델 튜닝
- TimeSeriesSplit 검증
- MAE, RMSE, R², MAPE, Hit Rate, Turnaround 지표 계산
- 예측 이력 생성
- 모델 및 산출물 저장

생성되는 주요 산출물 :

```text
models/{item_code}/model.pkl
data/processed/{item_code}/train_df.csv
data/processed/{item_code}/features.pkl
data/processed/{item_code}/metrics.json
data/processed/{item_code}/predictions.csv
data/processed/{item_code}/feature_importances.csv
```

---

### scripts/experiment.py

품목별 변수 조합과 타겟 유형을 실험하는 파일입니다.

저장 없이 성능만 확인할 때 사용합니다.

```bash
python scripts/experiment.py
```

`features` 목록을 바꾸면서 변수의 조합과 타겟의 설정을 비교합니다.

---

### scripts/update_item_model.py

최종 선택한 변수 조합으로 모델을 학습하고 산출물을 저장하는 파일입니다.

```bash
python scripts/update_item_model.py
```

실험이 끝난 뒤 최종 모델을 갱신할 때 사용합니다.

저장되는 결과는 웹서비스의 `get_item_result()` 에서 사용됩니다.

---

### main.py

서비스 함수가 정상적으로 동작하는지 확인하기 위한 실행 파일입니다.

개발 중 테스트 용도로 사용합니다.

---

### data.xlsx

기업 출하량/재고 업로드 예시 파일입니다.

`upload_parser.py` 에서 읽어 기업별 생산/재고 가이드라인 계산에 사용할 수 있습니다.

---

## 실행 예시

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
  item_code = "HR",
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
※ 엑셀의 shipment 컬럼은 월별 출하 이력으로 읽혀 `shipment_history`에 전달됩니다.

---

## 기대효과

- 품목별 월별 수요 변동을 사전에 파악하여 재고 및 생산 계획 수립 지원
- 수요 예측 결과를 기반으로 재고 부족 가능성을 조기에 확인
- 안전 재고와 부족 예상 수량을 함께 제공하여 재고 관리 의사결정 보조
- 과잉 재고와 생산 부족으로 인한 비용 및 운영 리스크 완화
- 주요 영향 변수와 산업군 정보를 제공하여 예측 결과 해석 가능성 향상
- 기업의 시장 점유율 또는 출하 이력을 반영한 맞춤형 생산 가이드라인 제공
- 모델 성능 지표를 함께 제공하여 결과의 신뢰도 판단 지원
- 철강재 수요 예측, 재고 리스크 분석, 생산 계획을 하나의 서비스 흐름으로 연결

## 향후 개선 사항

- 예측 결과에 대한 신뢰구간 또는 예측 범위 제공
- 품목별 모델 성능 모니터링 및 주기적 재학습 자동화
- 신규 데이터 업로드 시 자동 학습/예측 파이프라인 구축
- ERP, MES, 재고관리 시스템과의 데이터 연동
- 재고 부족 위험 알림 기능 추가
- 품목별/기업별 대시보드 시각화 기능 강화
- 시나리오 분석 기능 추가
  - 수요 증가/감소 상황
  - 재고 수준 변화
  - 리드타임 변화
  - 생산능력 제한
- 더 많은 철강재 품목 및 외부 경제지표 추가
- 예측 오차가 큰 구간에 대한 원인 분석 기능 고도화
