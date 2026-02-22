def optimize_budget(predicted, income):
    total = sum(predicted.values())
    return {c: (v/total)*income for c,v in predicted.items()}
