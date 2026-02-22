def auto_category(merchant: str):
    merchant = merchant.lower()

    # ✅ Bills
    if "recharge" in merchant or "jio" in merchant or "airtel" in merchant:
        return "TV, phone and internet", "Bills"

    if "current" in merchant or "electricity" in merchant:
        return "Utilities", "Bills"

    # ✅ Needs
    if "mart" in merchant or "grocery" in merchant or "supermarket" in merchant:
        return "Groceries", "Needs"

    if "bus" in merchant or "uber" in merchant or "train" in merchant:
        return "Transportation", "Needs"

    # ✅ Wants
    if "amazon" in merchant or "shopping" in merchant:
        return "Shopping", "Wants"

    if "travel" in merchant or "flight" in merchant:
        return "Travel", "Wants"

    # ✅ Default
    return "Uncategorized", "Others"
