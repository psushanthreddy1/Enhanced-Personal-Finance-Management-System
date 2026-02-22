def generate_alert(amount):
    if amount > 5000:
        return "⚠ High-value transaction detected!"
    return "✅ Transaction normal"
