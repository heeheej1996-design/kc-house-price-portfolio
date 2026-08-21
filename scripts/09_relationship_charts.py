"""정제본에서 타깃(price)과 변수들의 관계 그래프 3장을 만든다.
1) 숫자 변수와의 관계, 2) 범주 변수별 차이, 3) 전체 상관관계 히트맵
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv("data/processed/kc_house_data_cleaned.csv")

# 1) 숫자 변수와의 관계
num_vars = ["sqft_living", "grade", "bathrooms", "sqft_living15"]
fig, axes = plt.subplots(2, 2, figsize=(11, 9))
for ax, col in zip(axes.flat, num_vars):
    ax.scatter(df[col], df["price"], s=4, alpha=0.15, color="#4C72B0")
    corr = df[col].corr(df["price"])
    ax.set_title(f"{col} (상관계수 {corr:.2f})")
    ax.set_xlabel(col)
    ax.set_ylabel("price (달러)")
fig.suptitle("price와 숫자 변수들의 관계 (정제본)", fontsize=14)
plt.tight_layout()
plt.savefig("outputs/day6/rel1_numeric_vs_price.png", dpi=150)
plt.close()
print("1) 저장 완료")

# 2) 범주 변수별 차이
cat_vars = [("waterfront", ["아니오", "예"]), ("view", None), ("condition", None)]
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, (col, labels) in zip(axes, cat_vars):
    groups = [df.loc[df[col] == v, "price"].values for v in sorted(df[col].unique())]
    tick_labels = labels if labels else sorted(df[col].unique())
    ax.boxplot(groups, tick_labels=tick_labels, showfliers=False)
    ax.set_title(f"{col}별 price 분포")
    ax.set_xlabel(col)
    ax.set_ylabel("price (달러)")
fig.suptitle("범주(등급) 변수별 price 차이 (정제본)", fontsize=14)
plt.tight_layout()
plt.savefig("outputs/day6/rel2_categorical_vs_price.png", dpi=150)
plt.close()
print("2) 저장 완료")

# 3) 전체 상관관계 히트맵
num_cols = [c for c in df.select_dtypes(include="number").columns if c != "id"]
corr_mat = df[num_cols].corr()

fig, ax = plt.subplots(figsize=(11, 9))
im = ax.imshow(corr_mat, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(num_cols)))
ax.set_yticks(range(len(num_cols)))
ax.set_xticklabels(num_cols, rotation=90)
ax.set_yticklabels(num_cols)
for i in range(len(num_cols)):
    for j in range(len(num_cols)):
        v = corr_mat.iloc[i, j]
        ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                fontsize=6, color="white" if abs(v) > 0.5 else "black")
fig.colorbar(im, ax=ax, shrink=0.8, label="상관계수")
ax.set_title("전체 숫자형 변수 상관관계 히트맵 (정제본)")
plt.tight_layout()
plt.savefig("outputs/day6/rel3_correlation_heatmap.png", dpi=150)
plt.close()
print("3) 저장 완료")
