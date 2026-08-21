"""docs/problem_definition.md '확인해 볼 것 3가지'에 답하는 그래프 3장을 만든다.

질문1: price 극단치가 오차(MAE)를 얼마나 끌어올리는가 (원본 데이터, price~sqft_living+grade+zipcode 회귀 기준)
질문2: sqft_living-price 관계가 직선인가 (정제본)
질문3: zipcode별 가격 차이가 실제로 큰가 (정제본)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

# ---------- 질문 1 ----------
raw = pd.read_csv("data/raw/kc_house_data.csv")


def run_mae(data):
    X = pd.get_dummies(data[["sqft_living", "grade", "zipcode"]], columns=["zipcode"], drop_first=True)
    y = data["price"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)
    m = LinearRegression().fit(Xtr, ytr)
    return mean_absolute_error(yte, m.predict(Xte))


mae_all = run_mae(raw)
mae_ex = run_mae(raw[raw["price"] < 1_000_000])

fig, ax = plt.subplots(figsize=(6, 5))
bars = ax.bar(["극단치 포함\n(전체)", "극단치 제외\n(100만 달러 미만)"], [mae_all, mae_ex],
              color=["#C44E52", "#4C72B0"])
for b, v in zip(bars, [mae_all, mae_ex]):
    ax.text(b.get_x() + b.get_width() / 2, v + 2000, f"{v:,.0f}", ha="center")
ax.set_ylabel("MAE (달러)")
ax.set_title("[질문1] price 극단치가 예측 오차(MAE)에 미치는 영향\n(price ~ sqft_living+grade+zipcode 회귀 기준)")
plt.tight_layout()
plt.savefig("outputs/day6/q1_outlier_effect_on_mae.png", dpi=150)
plt.close()
print(f"Q1: mae_all={mae_all:,.0f}, mae_ex={mae_ex:,.0f}")

# ---------- 질문 2 ----------
clean = pd.read_csv("data/processed/kc_house_data_cleaned.csv")

fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(clean["sqft_living"], clean["price"], s=4, alpha=0.15, color="#4C72B0")

z = np.polyfit(clean["sqft_living"], clean["price"], 1)
xs = np.linspace(clean["sqft_living"].min(), clean["sqft_living"].max(), 100)
ax.plot(xs, np.polyval(z, xs), color="red", linewidth=2, label="선형 추세선")

bins = pd.cut(clean["sqft_living"], bins=20)
means = clean.groupby(bins, observed=True)["price"].mean()
mids = [interval.mid for interval in means.index]
ax.plot(mids, means.values, color="green", linewidth=2, linestyle="--", label="구간별 평균(실제 추세)")

ax.set_xlabel("sqft_living (실거주 면적)")
ax.set_ylabel("price (달러)")
ax.set_title("[질문2] sqft_living-price 관계가 직선인지 (정제본)")
ax.legend()
plt.tight_layout()
plt.savefig("outputs/day6/q2_sqft_living_vs_price.png", dpi=150)
plt.close()
print("Q2 저장 완료")

# ---------- 질문 3 ----------
med_by_zip = clean.groupby("zipcode")["price"].median().sort_values()

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(range(len(med_by_zip)), med_by_zip.values, color="#4C72B0")
ax.set_xlabel("zipcode (중앙값 가격 오름차순 정렬, 70개 지역)")
ax.set_ylabel("지역별 price 중앙값 (달러)")
ax.set_title("[질문3] zipcode(지역)별 가격 차이가 실제로 큰지 (정제본)")
ax.set_xticks([])
plt.tight_layout()
plt.savefig("outputs/day6/q3_price_by_zipcode.png", dpi=150)
plt.close()
print(f"Q3: 최저={med_by_zip.min():,.0f}, 최고={med_by_zip.max():,.0f}, 배율={med_by_zip.max()/med_by_zip.min():.1f}배")
