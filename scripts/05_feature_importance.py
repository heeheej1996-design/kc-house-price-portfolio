"""가장 성능이 좋았던 랜덤포레스트의 변수 중요도를 계산해 그래프로 저장한다.
zipcode 원-핫 더미 69개는 하나로 합산해서 표시한다.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

train_df = pd.read_csv("outputs/day6/train_time.csv")
test_df = pd.read_csv("outputs/day6/test_time.csv")

DROP_COLS = ["id", "sqft_above", "date", "price"]
feature_cols = [c for c in train_df.columns if c not in DROP_COLS]

X_train = pd.get_dummies(train_df[feature_cols], columns=["zipcode"], drop_first=True)
y_train = train_df["price"]

model = RandomForestRegressor(n_estimators=300, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

imp = pd.Series(model.feature_importances_, index=X_train.columns)
zip_cols = [c for c in imp.index if c.startswith("zipcode_")]
core_importance = imp.drop(zip_cols)
core_importance["zipcode (지역, 69개 더미 합산)"] = imp[zip_cols].sum()

top = core_importance.sort_values(ascending=False).head(15)
print(top)

fig, ax = plt.subplots(figsize=(9, 7))
colors = ["#C44E52" if "zipcode" in n else "#4C72B0" for n in top.index]
ax.barh(top.index[::-1], top.values[::-1], color=colors[::-1])
ax.set_xlabel("중요도 (Feature Importance)")
ax.set_title("랜덤포레스트 변수 중요도 순위 (상위 15개)\nzipcode는 69개 더미를 합산한 값")
plt.tight_layout()
plt.savefig("outputs/day6/rf_feature_importance.png", dpi=150)
plt.close()
print("저장 완료: outputs/day6/rf_feature_importance.png")
