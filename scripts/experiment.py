import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from train_utils import run_training_pipeline


ITEM_CODE = "HR"
DEMAND_COL = "HR_demand"

features = [
    "HR_demand_diff",
    "HR_demand",
    "month_diff",
    "steel_capacity_idx_diff",
    "CR_demand",
    "CR_demand_diff",
    "construction_order_amt_lag2",
    "month_lag2",
    "HR_inv_diff",
    "month_lag1",
    "HR_prod_ma3",
    "auto_domestic_ship",
    "construction_order_amt_diff_shock90",
    "auto_domestic_ship_diff_shock90",
    "is_month_12",
]

if __name__ == "__main__":
    result = run_training_pipeline(
        item_code=ITEM_CODE,
        demand_col=DEMAND_COL,
        features=features,
        target_type="diff",
        data_path="data/raw/steel_demand.csv",
        n_splits=4,
        test_size=10,
        save=False
    )