"""랜덤포레스트/XGBoost 하이퍼파라미터를 GridSearchCV로 튜닝한다.

시간순으로 정렬된 train_time만 사용하고, 교차검증도 TimeSeriesSplit으로
과거→미래 순서를 지켜서 나눈다 (04번 스크립트와 같은 이유로 일반 랜덤 K-fold는 쓰지 않음).
튜닝 후 test_time에서 성능을 재평가해 튜닝 전(04번 결과)과 비교한다.
"""
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor

train_df = pd.read_csv("outputs/day6/train_time.csv")
test_df = pd.read_csv("outputs/day6/test_time.csv")

DROP_COLS = ["id", "sqft_above", "date", "price"]
feature_cols = [c for c in train_df.columns if c not in DROP_COLS]

X_train = pd.get_dummies(train_df[feature_cols], columns=["zipcode"], drop_first=True)
X_test = pd.get_dummies(test_df[feature_cols], columns=["zipcode"], drop_first=True)
X_train, X_test = X_train.align(X_test, join="left", axis=1, fill_value=0)

y_train = train_df["price"]
y_test = test_df["price"]

tscv = TimeSeriesSplit(n_splits=5)

param_grids = {
    "랜덤포레스트": (
        RandomForestRegressor(random_state=42, n_jobs=-1),
        {
            "n_estimators": [100, 300],
            "max_depth": [10, None],
            "min_samples_leaf": [1, 4],
        },
    ),
    "XGBoost": (
        XGBRegressor(random_state=42, verbosity=0),
        {
            "n_estimators": [100, 300],
            "max_depth": [3, 6],
            "learning_rate": [0.05, 0.1],
        },
    ),
}

# 튜닝 전(04번 스크립트) 결과 — 비교용
prev = pd.read_csv("outputs/day6/model_comparison.csv").set_index("모델")

rows = []
best_params_all = {}

for name, (estimator, grid) in param_grids.items():
    search = GridSearchCV(
        estimator, grid, cv=tscv,
        scoring="neg_root_mean_squared_error", n_jobs=-1,
    )
    search.fit(X_train, y_train)
    best_model = search.best_estimator_
    pred = best_model.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, pred))
    mae = mean_absolute_error(y_test, pred)
    r2 = r2_score(y_test, pred)

    best_params_all[name] = search.best_params_
    print(f"[{name}] best_params={search.best_params_}")
    print(f"  튜닝 전: RMSE={prev.loc[name, 'RMSE']:,.2f}  튜닝 후: RMSE={rmse:,.2f}")

    rows.append({
        "모델": name,
        "RMSE_튜닝전": prev.loc[name, "RMSE"],
        "RMSE_튜닝후": round(rmse, 2),
        "MAE_튜닝전": prev.loc[name, "MAE"],
        "MAE_튜닝후": round(mae, 2),
        "R2_튜닝전": prev.loc[name, "R2"],
        "R2_튜닝후": round(r2, 4),
        "best_params": json.dumps(search.best_params_, ensure_ascii=False),
    })

result_df = pd.DataFrame(rows)
result_df.to_csv("outputs/day6/tuning_before_after.csv", index=False, encoding="utf-8-sig")

with open("outputs/day6/tuning_best_params.json", "w", encoding="utf-8") as f:
    json.dump(best_params_all, f, ensure_ascii=False, indent=2)

print()
print(result_df.to_string(index=False))
print()
print("저장 완료: outputs/day6/tuning_before_after.csv, outputs/day6/tuning_best_params.json")
