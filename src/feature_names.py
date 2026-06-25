FEATURE_NAME_MAP = {
    "HR_demand": "열연강판 수요량",
    "HR_prod": "열연강판 생산량",
    "HR_inv": "열연강판 재고량",

    "CR_demand": "냉연강판 수요량",
    "CR_prod": "냉연강판 생산량",
    "CR_inv": "냉연강판 재고량",

    "G_demand": "아연도강판 수요량",
    "G_prod": "아연도강판 생산량",
    "G_inv": "아연도강판 재고량",

    "auto_prod": "자동차 생산량",
    "auto_domestic_ship": "자동차 내수 출하량",
    "auto_export_ship": "자동차 수출 출하량",

    "construction_order_amt": "건설 수주액",

    "appliance_prod_idx": "가전 생산지수",
    "appliance_ship_idx": "가전 출하지수",

    "usdkrw_avg": "원/달러 평균 환율",
    "leading_idx": "경기선행지수",
    "gov_bond_3y_avg": "국고채 3년 평균금리",
    "iron_ore_price": "철광석 가격",
    "steel_capacity_idx": "철강 생산능력지수",
    "steel_operating_rate": "철강 가동률",

    "month": "월",
}


FEATURE_GROUP_MAP = {
    "HR": "HR 수요/생산/재고",
    "CR": "CR 수요/생산/재고",
    "G": "GI 수요/생산/재고",
    "auto": "자동차",
    "construction": "건설",
    "appliance": "가전",
    "usdkrw": "환율",
    "leading": "경기/금리",
    "gov_bond": "경기/금리",
    "iron_ore": "원자재",
    "steel_capacity": "철강 설비/가동",
    "steel_operating": "철강 설비/가동",
    "month": "계절성",
    "is_month": "계절성",
}


INDUSTRY_GROUPS = {
    "자동차": "자동차",
    "건설": "건설",
    "가전": "가전",
}


def get_feature_group(feature):
    for prefix, group_name in FEATURE_GROUP_MAP.items():
        if feature == prefix or feature.startswith(f"{prefix}_"):
            return group_name

    return "기타"


def get_feature_display_name(feature):
    suffix_map = {
        "_lag1": "(1개월 전)",
        "_lag2": "(2개월 전)",
        "_diff": "(전월 대비 증감)",
        "_diff2": "(2개월 대비 증감)",
        "_ma3": "(3개월 이동평균)"
    }

    for suffix, suffix_name in suffix_map.items():
        if feature.endswith(suffix):
            base_feature = feature[:-len(suffix)]
            base_name = FEATURE_NAME_MAP.get(base_feature, base_feature)
            return f"{base_name}{suffix_name}"

    if feature.startswith("is_month_"):
        month = feature.replace("is_month_", "")
        return f"{month}월 여부"

    return FEATURE_NAME_MAP.get(feature, feature)
