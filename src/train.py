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
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

def split_data():
    df = build_dataset()

    df = df.sort_values("order_purchase_timestamp").reset_index(drop=True)

    X, y = prepare_features(df)
    train_end = int(len(df) * 0.64)
    val_end = int(len(df) * 0.80)

    X_train, y_train = X.iloc[:train_end], y.iloc[:train_end]
    X_val, y_val = X.iloc[train_end:val_end], y.iloc[train_end:val_end]
    X_test, y_test = X.iloc[val_end:], y.iloc[val_end:]

    print(
        f"Split sizes -> Train: {len(X_train)} (late: {y_train.mean():.2%}) | "
        f"Val: {len(X_val)} (late: {y_val.mean():.2%}) | "
        f"Test: {len(X_test)} (late: {y_test.mean():.2%})\n"
    )

    return X_train, X_val, X_test, y_train, y_val, y_test

def train_baseline():
    X_train, X_val, X_test, y_train, y_val, y_test = split_data()

    categorical_features = ["customer_state", "seller_state"]
    numeric_features = [
        col for col in X_train.columns if col not in categorical_features
    ]

    linear_preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    tree_preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    dummy = DummyClassifier(strategy="most_frequent")
    dummy.fit(X_train, y_train)
    dummy_predictions = dummy.predict(X_val)

    print("=== Dummy Classifier ===")
    print(classification_report(y_val, dummy_predictions, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(y_val, dummy_predictions))

    model = make_pipeline(
        linear_preprocessor,
        LogisticRegression(class_weight="balanced", max_iter=1000),
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_val)
    probabilities = model.predict_proba(X_val)[:, 1]

    print("\n=== Logistic Regression ===")
    print(classification_report(y_val, predictions, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(y_val, predictions))
    train_probabilities = model.predict_proba(X_train)[:, 1]
    print("Train ROC-AUC:", round(roc_auc_score(y_train, train_probabilities), 4))
    print("Val ROC-AUC:", round(roc_auc_score(y_val, probabilities), 4))

    rf_model = make_pipeline(
        tree_preprocessor,
        RandomForestClassifier(
            n_estimators=200,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    )

    rf_model.fit(X_train, y_train)
    rf_predictions = rf_model.predict(X_val)
    rf_probabilities = rf_model.predict_proba(X_val)[:, 1]

    print("\n=== Random Forest ===")
    print(classification_report(y_val, rf_predictions, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(y_val, rf_predictions))
    rf_train_probabilities = rf_model.predict_proba(X_train)[:, 1]
    print("Train ROC-AUC:", round(roc_auc_score(y_train, rf_train_probabilities), 4))
    print("Val ROC-AUC:", round(roc_auc_score(y_val, rf_probabilities), 4))
    print("Random Forest probability summary:")
    print(pd.Series(rf_probabilities).describe(
        percentiles=[0.5, 0.9, 0.95, 0.99]
    ))

    for threshold in [0.5, 0.4, 0.3, 0.2, 0.1]:
        predictions = (rf_probabilities >= threshold).astype(int)
        precision = precision_score(y_val, predictions, zero_division=0)
        recall = recall_score(y_val, predictions, zero_division=0)
        f1 = f1_score(y_val, predictions, zero_division=0)
        print(
            f"Threshold: {threshold:.1f} | "
            f"Precision: {precision:.3f} | "
            f"Recall: {recall:.3f} | "
            f"F1: {f1:.3f}"
        )

    xgb_model = make_pipeline(
        tree_preprocessor,
        XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            scale_pos_weight=(y_train == 0).sum() / (y_train == 1).sum(),
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1,
        ),
    )

    xgb_model.fit(X_train, y_train)
    xgb_predictions = xgb_model.predict(X_val)
    xgb_probabilities = xgb_model.predict_proba(X_val)[:, 1]

    print("\n=== XGBoost ===")
    print(classification_report(y_val, xgb_predictions, zero_division=0))
    print("Confusion matrix:")
    print(confusion_matrix(y_val, xgb_predictions))
    xgb_train_probabilities = xgb_model.predict_proba(X_train)[:, 1]
    print("Train ROC-AUC:", round(roc_auc_score(y_train, xgb_train_probabilities), 4))
    print("Val ROC-AUC:", round(roc_auc_score(y_val, xgb_probabilities), 4))

    print("\nXGBoost probability summary:")
    print(pd.Series(xgb_probabilities).describe(
        percentiles=[0.5, 0.9, 0.95, 0.99]
    ))

    feature_names = model.named_steps["columntransformer"].get_feature_names_out()
    feature_summary = pd.DataFrame({
        "feature": feature_names,
        "logreg_coef": model.named_steps["logisticregression"].coef_[0],
        "rf_importance": rf_model.named_steps["randomforestclassifier"].feature_importances_,
        "xgb_importance": xgb_model.named_steps["xgbclassifier"].feature_importances_,
    }).sort_values("xgb_importance", ascending=False)

    print("\n=== Top 15 Features (by XGBoost importance) ===")
    print(feature_summary.head(15).to_string(index=False))

    return model

if __name__ == "__main__":
    train_baseline()