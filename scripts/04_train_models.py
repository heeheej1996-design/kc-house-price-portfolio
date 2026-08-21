"""정제본 + 시간순 분할(train_time/test_time)로 선형회귀/랜덤포레스트/XGBoost를 학습하고
기준선(baseline_time)과 함께 RMSE/MAE/R² 비교표를 만든다.

입력 변수: id, sqft_above, date, price를 제외한 나머지 전부.
  - id: 단순 행 식별자, 정보 없음
  - sqft_above: sqft_living과 상관계수 0.877로 거의 중복
  - date: 문자열이라 가공 없이는 사용 불가 (이번 모델에서는 미사용)
범주형 처리: zipcode(순서 없는 지역 범주)만 원-핫 인코딩.
  waterfront/view/condition/grade는 순서형이라 숫자 그대로 사용.
"""
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

train_df = pd.read_csv("outputs/day6/train_time.csv")
test_df = pd.read_csv("outputs/day6/test_time.csv")

DROP_COLS = ["id", "sqft_above", "date", "price"]
feature_cols = [c for c in train_df.columns if c not in DROP_COLS]

X_train = pd.get_dummies(train_df[feature_cols], columns=["zipcode"], drop_first=True)
X_test = pd.get_dummies(test_df[feature_cols], columns=["zipcode"], drop_first=True)
X_train, X_test = X_train.align(X_test, join="left", axis=1, fill_value=0)

y_train = train_df["price"]
y_test = test_df["price"]

print("입력 변수:", feature_cols)
print("피처 수 (zipcode 원핫 포함):", X_train.shape[1])

with open("outputs/day6/baseline_time.json", encoding="utf-8") as f:
    base = json.load(f)

rows = [{"모델": "기준선(평균값)", "RMSE": base["RMSE"], "MAE": base["MAE"], "R2": base["R2"]}]

models = {
    "선형회귀": LinearRegression(),
    "랜덤포레스트": RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1),
    "XGBoost": XGBRegressor(n_estimators=300, random_state=42, verbosity=0),
}

for name, model in models.items():
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    mae = mean_absolute_error(y_test, pred)
    r2 = r2_score(y_test, pred)
    rows.append({"모델": name, "RMSE": round(rmse, 2), "MAE": round(mae, 2), "R2": round(r2, 4)})
    print(f"{name}: RMSE={rmse:,.2f} MAE={mae:,.2f} R2={r2:.4f}")

result_df = pd.DataFrame(rows)

# 기준선 대비 개선율(%)
base_row = result_df[result_df["모델"] == "기준선(평균값)"].iloc[0]
result_df["RMSE_개선율(%)"] = ((base_row["RMSE"] - result_df["RMSE"]) / base_row["RMSE"] * 100).round(1)
result_df["MAE_개선율(%)"] = ((base_row["MAE"] - result_df["MAE"]) / base_row["MAE"] * 100).round(1)
result_df.loc[result_df["모델"] == "기준선(평균값)", ["RMSE_개선율(%)", "MAE_개선율(%)"]] = 0.0
result_df.to_csv("outputs/day6/model_comparison.csv", index=False, encoding="utf-8-sig")

print()
print(result_df.to_string(index=False))
print()
print("저장 완료: outputs/day6/model_comparison.csv")
