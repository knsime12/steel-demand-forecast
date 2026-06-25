import pandas as pd


REQUIRED_OUTPUT_COLUMNS = [
    "item_code",
    "planned_production",
    "current_stock",
    "target_stock",
    "market_share",
]


COLUMN_ALIASES = {
    "품목": "item_code",
    "품목코드": "item_code",
    "회사 생산계획": "planned_production",
    "회사 기존 생산계획": "planned_production",
    "생산계획": "planned_production",
    "회사 현재 재고": "current_stock",
    "현재 재고": "current_stock",
    "회사 목표 재고": "target_stock",
    "목표 재고": "target_stock",
    "회사 시장점유율": "market_share",
    "시장점유율": "market_share",
}


def load_plan_risk_inputs_from_excel(file_path):
    """
    운영 기준 입력 엑셀을 리스크 모니터링 입력값으로 변환

    계획/재고 입력 화면의 Excel 업로드 기능에서 사용
    """
    df = pd.read_excel(file_path)
    df = df.rename(columns=COLUMN_ALIASES)

    missing_columns = [
        col for col in REQUIRED_OUTPUT_COLUMNS
        if col not in df.columns
    ]
    if missing_columns:
        raise ValueError(f"필수 입력 컬럼이 없습니다: {missing_columns}")

    result_df = df[REQUIRED_OUTPUT_COLUMNS].copy()
    result_df = result_df.dropna(how="all")
    result_df = result_df[result_df["item_code"].notna()].copy()
    result_df["item_code"] = result_df["item_code"].astype(str).str.strip().str.upper()

    allowed_items = {"HR", "CR", "GI"}
    invalid_items = sorted(set(result_df["item_code"]) - allowed_items)
    if invalid_items:
        raise ValueError(f"지원하지 않는 품목 코드입니다: {invalid_items}")

    duplicated_items = result_df[result_df["item_code"].duplicated()]["item_code"].tolist()
    if duplicated_items:
        raise ValueError(f"중복된 품목 코드가 있습니다: {duplicated_items}")

    numeric_columns = [
        "planned_production",
        "current_stock",
        "target_stock",
        "market_share",
    ]
    for col in numeric_columns:
        result_df[col] = pd.to_numeric(result_df[col], errors="coerce")

    if result_df[numeric_columns].isna().any().any():
        raise ValueError("생산계획, 재고, 시장점유율은 숫자로 입력해야 합니다.")

    if (result_df["market_share"] < 0).any() or (result_df["market_share"] > 100).any():
        raise ValueError("시장점유율은 0 이상 100 이하로 입력해야 합니다.")

    return result_df.to_dict(orient="records")
