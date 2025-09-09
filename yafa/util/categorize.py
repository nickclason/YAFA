import os
import json
# TODO: Do some AI ✨magic✨ here later
# TODO: Do some kind of fuzzy matching/option to remember previous transactions/categories and use for future matching


def naive_categorize_transaction(payee: str, description: str) -> str:
    default_category = "Uncategorized"
    default_categories = json.loads(os.environ.get("DEFAULT_CATEGORIES", None))
    if not default_categories:
        return default_category
    
    for type in default_categories:
        if type not in ["Income", "Expense"]:
            return default_category
        
        for name in default_categories[type]:
            if name == default_category:
                return default_category
            
            category_keywords = default_categories[type][name]
            if not category_keywords:
                continue

            text = f"{payee} {description}".lower()
            if any(kw in text for kw in category_keywords):
                return name
        
    return default_category
