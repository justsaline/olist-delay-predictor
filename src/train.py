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
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score, f1_score
from xgboost import XGBClassifier

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

    rf_model = make_pipeline(
        RandomForestClassifier(
            n_estimators=200,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
    )

    rf_model.fit(X_train, y_train)
    rf_predictions = rf_model.predict(X_test)
    rf_probabilities = rf_model.predict_proba(X_test)[:,1]

    print("\n=== Random Forest ===")
    print(classification_report(
        y_test, rf_predictions, zero_division=0
    ))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, rf_predictions))
    print("ROC-AUC:", round(
        roc_auc_score(y_test, rf_probabilities), 4
    ))
    print("Random Forest probability summary:")
    print(pd.Series(rf_probabilities).describe(
    percentiles=[0.5, 0.9, 0.95, 0.99]
    ))

    for threshold in [0.5, 0.4, 0.3, 0.2, 0.1]:
        predictions = (rf_probabilities >= threshold).astype(int)

        precision = precision_score(
            y_test, predictions, zero_division=0
        )
        recall = recall_score(
            y_test, predictions, zero_division=0
        )
        f1 = f1_score(
            y_test, predictions, zero_division=0
        )
        print(
            f"Threshold: {threshold:.1f} | "
            f"Precision: {precision:.3f} | "
            f"Recall: {recall:.3f} | "
            f"F1: {f1:.3f}"
        )

    xgb_model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        scale_pos_weight=(y_train==0).sum() / (y_train==1).sum(),
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
    )

    xgb_model.fit(X_train, y_train)
    xgb_predictions = xgb_model.predict(X_test)
    xgb_probabilities = xgb_model.predict_proba(X_test)[:,1]

    print("\n=== XGBoost ===")
    print(classification_report(
        y_test, xgb_predictions, zero_division=0
    ))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, xgb_predictions))
    print("ROC-AUC:", round(
        roc_auc_score(y_test, xgb_probabilities), 4
    ))

    return model

if __name__ == "__main__":
    train_baseline()