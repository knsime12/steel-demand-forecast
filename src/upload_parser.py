import pandas as pd


def load_company_shipments_from_excel(file_path):
    """
    엑셀 업로드 파일에서 월별 출하량과 현재 재고를 추출한다.

    필수 컬럼:
    - date
    - shipment

    선택 컬럼:
    - stock
    """

    df = pd.read_excel(file_path)

    # 컬럼명 공백 제거
    df.columns = df.columns.str.strip()

    # 한글 컬럼명도 허용
    df = df.rename(columns={
        "월": "date",
        "날짜": "date",
        "출하량": "shipment",
        "재고량": "stock",
        "현재재고": "stock"
    })

    required_cols = ["date", "shipment"]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"필수 컬럼이 없습니다: {col}")

    df["date"] = pd.to_datetime(df["date"])
    df["shipment"] = pd.to_numeric(df["shipment"], errors="coerce")

    if "stock" in df.columns:
        df["stock"] = pd.to_numeric(df["stock"], errors="coerce")

    df = df.dropna(subset=["date", "shipment"])
    df = df.sort_values("date")

    monthly_shipments = df["shipment"].tolist()

    current_stock = None

    if "stock" in df.columns:
        stock_df = df.dropna(subset=["stock"])

        if len(stock_df) > 0:
            current_stock = stock_df["stock"].iloc[-1]

    return {
        "monthly_shipments": monthly_shipments,
        "current_stock": None if current_stock is None else int(round(current_stock))
    }