import json, os

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "qualified_expenses.json")

with open(DATA_PATH) as f:
    QUALIFIED = set(json.load(f)["categories"])  # e.g., ["pharmacy", "doctor"]

def is_qualified(category: str) -> bool:
    return category.lower() in QUALIFIED
