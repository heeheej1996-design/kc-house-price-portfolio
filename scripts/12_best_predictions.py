"""튜닝된 XGBoost(최종 모델)의 예측이 실제값과 가장 가까웠던 5건을 찾아 저장한다.
오차가 가장 컸던 5건(06_error_analysis.py, 랜덤포레스트 기준)과 대조하기 위한 것.
"""
import json
import pandas as pd
from xgboost import XGBRegressor

train_df = pd.read_csv("outputs/day6/train_time.csv")
test_df = pd.read_csv("outputs/day6/test_time.csv")

DROP_COLS = ["id", "sqft_above", "date", "price"]
feature_cols = [c for c in train_df.columns if c not in DROP_COLS]

X_train = pd.get_dummies(train_df[feature_cols], columns=["zipcode"], drop_first=True)
X_test = pd.get_dummies(test_df[feature_cols], columns=["zipcode"], drop_first=True)
X_train, X_test = X_train.align(X_test, join="left", axis=1, fill_value=0)

y_train = train_df["price"]

with open("outputs/day6/tuning_best_params.json", encoding="utf-8") as f:
    best_params = json.load(f)["XGBoost"]

model = XGBRegressor(random_state=42, verbosity=0, **best_params)
model.fit(X_train, y_train)
pred = model.predict(X_test)

result = test_df.copy()
result["예측값"] = pred.round(0)
result["오차(예측-실제)"] = (result["예측값"] - result["price"]).round(0)
result["절대오차"] = result["오차(예측-실제)"].abs()

cols = ["price", "예측값", "오차(예측-실제)", "sqft_living", "grade", "bedrooms", "bathrooms",
        "waterfront", "view", "condition", "zipcode", "lat", "long", "yr_built", "date"]
best5 = result.sort_values("절대오차").head(5)

print(best5[cols].to_string(index=False))
best5[cols].to_csv("outputs/day6/best5_predictions.csv", index=False, encoding="utf-8-sig")
print()
print("저장 완료: outputs/day6/best5_predictions.csv")
