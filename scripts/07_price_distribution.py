"""정제본에서 타깃(price)의 분포를 히스토그램+박스플롯으로 그리고 기초 통계를 출력한다."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv("data/processed/kc_house_data_cleaned.csv")
price = df["price"]

stats = {
    "평균": price.mean(),
    "중앙값": price.median(),
    "최소": price.min(),
    "최대": price.max(),
    "표준편차": price.std(),
}
for k, v in stats.items():
    print(f"{k}: {v:,.2f}")
print("skewness:", price.skew())

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(price, bins=60, color="#4C72B0", edgecolor="white")
axes[0].axvline(stats["평균"], color="red", linestyle="--", label=f"평균 {stats['평균']:,.0f}")
axes[0].axvline(stats["중앙값"], color="green", linestyle="--", label=f"중앙값 {stats['중앙값']:,.0f}")
axes[0].set_title("price 분포 (정제본)")
axes[0].set_xlabel("price (달러)")
axes[0].set_ylabel("빈도")
axes[0].legend()

axes[1].boxplot(price, vert=True)
axes[1].set_title("price 박스플롯 (정제본)")
axes[1].set_ylabel("price (달러)")

plt.tight_layout()
plt.savefig("outputs/day6/price_distribution.png", dpi=150)
plt.close()
print("저장 완료: outputs/day6/price_distribution.png")
