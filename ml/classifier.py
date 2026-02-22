rules = {
    "zomato": "Food",
    "uber": "Transport",
    "amazon": "Shopping",
    "electricity": "Bills"
}

def categorize(merchant):
    for key in rules:
        if key in merchant.lower():
            return rules[key]
    return "Other"
