from src.service import get_item_result
from src.upload_parser import load_company_shipments_from_excel
from src.service import get_company_guideline
import json

result_cr = get_item_result(
    item_code="CR",
    start_date="2024-01",
    end_date="2026-03"
)

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

print(json.dumps(result_cr, ensure_ascii = False, indent = 2))

