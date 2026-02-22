import pandas as pd
import random
from datetime import datetime

class BankTransactionFetcher:
    def fetch_transactions(self):

        merchants = ["Amazon", "Uber", "Netflix", "Rent", "Starbucks"]

        transactions = []
        for i in range(8):
            transactions.append({
                "amount": round(random.uniform(100, 5000), 2),
                "merchant": random.choice(merchants),
                "date": datetime.today().strftime("%Y-%m-%d")
            })

        return pd.DataFrame(transactions)
