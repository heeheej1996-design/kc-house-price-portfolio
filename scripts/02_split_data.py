"""정제본을 두 가지 방식으로 8:2 분할한다.

1) 랜덤 분할 (train.csv / test.csv) — 초기 탐색에 사용, 나중에 문제가 있다고 판단해 폐기.
2) 시간순 분할 (train_time.csv / test_time.csv) — date 기준 오름차순 정렬 후 앞 80%/뒤 20%.
   최종적으로 이 분할을 공식 기준으로 사용한다 (docs/problem_definition.md v2 참고).
"""
import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("data/processed/kc_house_data_cleaned.csv")

# 1) 랜덤 분할
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
train_df.to_csv("outputs/day6/train.csv", index=False)
test_df.to_csv("outputs/day6/test.csv", index=False)
print(f"[랜덤 분할] train {len(train_df)}행 / test {len(test_df)}행 저장 완료")

# 2) 시간순 분할
df_sorted = df.copy()
df_sorted["date_parsed"] = pd.to_datetime(df_sorted["date"], format="%Y%m%dT%H%M%S")
df_sorted = df_sorted.sort_values("date_parsed").reset_index(drop=True)

cut = int(len(df_sorted) * 0.8)
train_time_df = df_sorted.iloc[:cut].drop(columns=["date_parsed"])
test_time_df = df_sorted.iloc[cut:].drop(columns=["date_parsed"])

train_time_df.to_csv("outputs/day6/train_time.csv", index=False)
test_time_df.to_csv("outputs/day6/test_time.csv", index=False)
print(f"[시간순 분할] train {len(train_time_df)}행 / test {len(test_time_df)}행 저장 완료")
print(f"  train 기간: {df_sorted['date_parsed'].iloc[0].date()} ~ {df_sorted['date_parsed'].iloc[cut-1].date()}")
print(f"  test  기간: {df_sorted['date_parsed'].iloc[cut].date()} ~ {df_sorted['date_parsed'].iloc[-1].date()}")
