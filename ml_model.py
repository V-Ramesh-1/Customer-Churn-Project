import pandas as pd

# Load dataset
df = pd.read_csv("churn_ml_dataset.csv")

print("Dataset loaded successfully")
print("Shape:", df.shape)
print("Columns:")
print(df.columns)
print("\nFirst 5 rows:")
print(df.head())

# ✅ Label / target (True/False → 1/0)
y = df["is_churned"].astype(int)

# ✅ Feature columns (use columns that exist in your file)
feature_cols = [
    "age",
    "tenure_months",
    "avg_monthly_minutes",
    "avg_monthly_data",
    "avg_monthly_sms",
    "total_payments",
    "avg_payment_amount",
    "num_complaints",
    "gender",
    "plan_type"
]

X = df[feature_cols].copy()

print("\nStep 3 complete")
print("X shape:", X.shape)
print("y shape:", y.shape)

print("\nTarget distribution (0 = not churn, 1 = churn):")
print(y.value_counts())
# ==============================
# STEP 4: Encode categorical features
# ==============================

print("\nBefore encoding:")
print(X.dtypes)

# One-hot encode categorical columns
X = pd.get_dummies(
    X,
    columns=["gender", "plan_type"],
    drop_first=True
)

print("\nAfter encoding:")
print(X.dtypes)

print("\nFinal feature columns:")
print(X.columns)
# ==============================
# STEP 5: Train-Test Split
# ==============================

from sklearn.model_selection import train_test_split

# Split data: 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nStep 5 complete")
print("X_train shape:", X_train.shape)
print("X_test shape:", X_test.shape)
print("y_train distribution:")
print(y_train.value_counts())
print("y_test distribution:")
print(y_test.value_counts())

# ==============================
# STEP 6: Train the model
# ==============================

from sklearn.linear_model import LogisticRegression

# Create the model
model = LogisticRegression(
    max_iter=1000,
    solver="liblinear"
)

# Train (fit) the model
model.fit(X_train, y_train)

print("\nStep 6 complete: Model trained")


# ==============================
# STEP 7: Evaluate the model
# ==============================

from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# Predict on test data
y_pred = model.predict(X_test)

# 1️⃣ Accuracy
accuracy = accuracy_score(y_test, y_pred)
print("\nModel Accuracy:")
print(round(accuracy, 3))

# 2️⃣ Confusion Matrix
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# 3️⃣ Precision, Recall, F1-score
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
# ==============================
# STEP 8: Predict churn probabilities
# ==============================

# Get churn probabilities
churn_probabilities = model.predict_proba(X_test)

# Probability of class 1 (churn)
churn_risk = churn_probabilities[:, 1]

# Create a dataframe to view results
results = X_test.copy()
results["actual_churn"] = y_test.values
results["churn_probability"] = churn_risk

print("\nSample churn risk predictions:")
print(results[["actual_churn", "churn_probability"]].head(10))

# Create churn risk categories
results["risk_level"] = pd.cut(
    results["churn_probability"],
    bins=[0, 0.3, 0.6, 1.0],
    labels=["Low Risk", "Medium Risk", "High Risk"]
)

print(results[["actual_churn", "churn_probability", "risk_level"]].head(10))

# ==============================
# STEP 9: Interpret model (feature impact)
# ==============================

coefficients = pd.DataFrame({
    "feature": X_train.columns,
    "coefficient": model.coef_[0]
}).sort_values(by="coefficient", ascending=False)

print("\nTop factors increasing churn:")
print(coefficients.head(10))

print("\nTop factors reducing churn:")
print(coefficients.tail(10))


# ==============================
# STEP 10: Export predictions for Power BI
# ==============================

# Predict churn probability for ALL customers (not just test set)
proba_all = model.predict_proba(X)[:, 1]  # probability of class 1 (churn)

# Create a results table with IDs + predictions
pred_df = pd.DataFrame({
    "customer_id": df["customer_id"],
    "churn_probability": proba_all
})

# Risk bands (simple and portfolio-friendly)
def risk_band(p):
    if p >= 0.35:
        return "High"
    elif p >= 0.20:
        return "Medium"
    else:
        return "Low"

pred_df["risk_level"] = pred_df["churn_probability"].apply(risk_band)

# Save for Power BI
pred_df.to_csv("churn_predictions_for_powerbi.csv", index=False)
print("\n✅ Saved: churn_predictions_for_powerbi.csv")


