from src.service import get_item_result
import json

result = get_item_result(
    item_code = "HR",
    start_date = "2024-01",
    end_date = "2026-03"
)

print(json.dumps(result, ensure_ascii = False, indent = 2))