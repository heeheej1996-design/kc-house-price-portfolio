"""위도·경도에 실제 위치대로 점을 찍고 price를 색으로 표현한 지도를 만든다.
주요 도시(시애틀 등) 위치를 별표로 표시해 지리 지식 없이도 이해할 수 있게 한다.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False

df = pd.read_csv("data/processed/kc_house_data_cleaned.csv")

CITIES = {
    "시애틀": (47.6062, -122.3321),
    "벨뷰": (47.6101, -122.2015),
    "레드먼드": (47.6740, -122.1215),
    "렌턴": (47.4829, -122.2171),
    "켄트": (47.3809, -122.2348),
    "오번": (47.3073, -122.2285),
}

fig, ax = plt.subplots(figsize=(9, 8))
sc = ax.scatter(df["long"], df["lat"], c=df["price"], cmap="viridis",
                 s=6, alpha=0.6, vmin=df["price"].quantile(0.02), vmax=df["price"].quantile(0.98))
cbar = fig.colorbar(sc, ax=ax, shrink=0.8)
cbar.set_label("price (달러)")

for name, (lat, lon) in CITIES.items():
    ax.scatter(lon, lat, marker="*", s=220, color="red", edgecolor="black", linewidth=0.8, zorder=5)
    ax.annotate(name, (lon, lat), textcoords="offset points", xytext=(7, 5),
                fontsize=11, fontweight="bold", color="black",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7))

ax.set_xlabel("경도 long (동서 방향)")
ax.set_ylabel("위도 lat (남북 방향)")
ax.set_title("위치(위도·경도)에 따른 price 분포 + 주요 도시\n(밝은 색 = 비싼 지역, 어두운 색 = 저렴한 지역, ★ = 주요 도시)")
ax.set_aspect("equal")

plt.tight_layout()
plt.savefig("outputs/day6/geo_price_map.png", dpi=150)
plt.close()
print("저장 완료: outputs/day6/geo_price_map.png")
