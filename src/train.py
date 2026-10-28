import pandas as pd

from src.features import build_dataset, prepare_features
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

def split_data():
    df = build_dataset()

    df= df.sort_values("order_purchase_timestamp").reset_index(drop=True)

    X,y = prepare_features(df)
    split_index = int(len(df)*0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    return X_train, X_test, y_train, y_test

def train_baseline():
    X_train, X_test, y_train, y_test = split_data()

    dummy = DummyClassifier(strategy= "most_frequent")
    dummy.fit(X_train,y_train)
    dummy_predictions = dummy.predict(X_test)

    print("=== Dummy Classifier ===")
    print(classification_report(y_test, dummy_predictions, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, dummy_predictions))

    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(class_weight="balanced", max_iter=1000),
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    print("\n=== Logistic Regression ===")
    print(classification_report(y_test, predictions, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, predictions))
    print("ROC-AUC:", round(roc_auc_score(y_test, probabilities), 4))

    return model

if __name__ == "__main__":
    train_baseline()