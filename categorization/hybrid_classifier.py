def hybrid_predict(txn):
    """
    Hybrid Expense Categorization
    Rule-based + ML fallback (Base Paper Page 5)
    """

    merchant = txn["merchant"]

    rules = {
        "Rent": "Housing",
        "Netflix": "Entertainment",
        "Uber": "Travel",
        "Starbucks": "Food",
        "Amazon": "Shopping",
        "Electricity Bill": "Bills"
    }

    # Rule-based categorization
    if merchant in rules:
        return rules[merchant]

    # ML fallback (placeholder)
    return "Others"
