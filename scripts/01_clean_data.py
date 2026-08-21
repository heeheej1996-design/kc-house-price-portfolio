"""data/raw/kc_house_data.csv를 정제해 data/processed/kc_house_data_cleaned.csv로 저장한다.

삭제 기준 (docs/problem_definition.md v0 6번 참고):
- price 100만 달러 이상
- bedrooms == 33 (이상치)
- bedrooms == 0 또는 bathrooms == 0.0 (의심스러운 값)
"""
import pandas as pd

df = pd.read_csv("data/raw/kc_house_data.csv")
n0 = len(df)

mask_price = df["price"] >= 1_000_000
mask_bedrooms_outlier = df["bedrooms"] == 33
mask_zero = (df["bedrooms"] == 0) | (df["bathrooms"] == 0.0)
drop_mask = mask_price | mask_bedrooms_outlier | mask_zero

df_clean = df[~drop_mask].reset_index(drop=True)

print(f"원본 행 수: {n0}")
print(f"삭제된 행 수: {drop_mask.sum()} (price>=100만: {mask_price.sum()}, bedrooms=33: {mask_bedrooms_outlier.sum()}, bedrooms/bathrooms=0: {mask_zero.sum()})")
print(f"정제 후 행 수: {len(df_clean)}")

df_clean.to_csv("data/processed/kc_house_data_cleaned.csv", index=False)
print("저장 완료: data/processed/kc_house_data_cleaned.csv")
