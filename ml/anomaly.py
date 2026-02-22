from sklearn.ensemble import IsolationForest
iso = IsolationForest(contamination=0.05)

def detect(amount):
    score = iso.decision_function([[amount]])
    return score[0]
