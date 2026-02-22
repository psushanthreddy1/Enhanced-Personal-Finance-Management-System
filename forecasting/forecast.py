def forecast_next_month(expense_history):
    """
    Placeholder forecasting module.
    Paper uses ARIMA + LSTM hybrid.
    """
    if not expense_history:
        return 0

    avg = sum(expense_history) / len(expense_history)
    return avg * 1.1   # predicted 10% increase
