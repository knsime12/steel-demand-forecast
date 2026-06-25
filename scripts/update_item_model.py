import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from train_utils import run_training_pipeline


ITEM_CODE = "GI"
DEMAND_COL = "G_demand"

FINAL_FEATURES = [
    "is_month_1",
    "month_diff",
    "G_demand",
    "G_demand_diff",
    "is_month_12",
    "month_lag1",
    "steel_capacity_idx_diff",
    "auto_export_ship_diff_shock90",
    "CR_demand_diff_shock90",
    "appliance_prod_idx_diff_shock90",
    "month",
    "appliance_ship_idx_lag1",
    "auto_prod_diff",
    "auto_export_ship",
    "auto_prod",
    "appliance_prod_idx_lag1",
    "auto_export_ship_lag2",
    "auto_prod_lag2",
    "auto_domestic_ship_diff_shock90",
    "HR_inv",
]


if __name__ == "__main__":
    result = run_training_pipeline(
        item_code=ITEM_CODE,
        demand_col=DEMAND_COL,
        features=FINAL_FEATURES,
        target_type = "rate",
        forecast_horizon=1,
        data_path="data/raw/steel_demand.csv",
        n_splits=4,
        test_size=10,
        save=True
    )
