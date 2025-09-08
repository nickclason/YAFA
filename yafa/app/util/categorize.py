import re

CATEGORIES = {
    "Groceries": ["walmart", "kroger", "aldi", "whole foods", "trader joe", "costco", "grocery", "meijer", "grocer"],
    "Restaurants": ["mcdonald", "burger king", "pizza", "cafe", "restaurant", "chick-fil-a", "taco bell", "doordash"],
    "Transportation": ["uber", "lyft", "shell", "exxon", "gas", "chevron", "bp", "mobil", "fuel", "transport"],
    "Entertainment": ["netflix", "spotify", "hulu", "amc"],
    "Rent": ["landlord", "apartment", "rent", "leasing", "property management", "towne"],
}


def naive_categorize_transaction(payee: str, description: str) -> str:
    text = f"{payee} {description}".lower()
    for category, keywords in CATEGORIES.items():
        if any(re.search(rf"\b{kw}\b", text) for kw in keywords):
            return category
    return "Uncategorized"

# TODO: Do some AI ✨magic✨ here later