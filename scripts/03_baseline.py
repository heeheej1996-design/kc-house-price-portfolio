"""평가용 전부를 훈련용 price 평균값으로 예측했을 때의 기준선(baseline) 성능을 계산한다.

랜덤 분할 기준(baseline.json/csv)과 시간순 분할 기준(baseline_time.json/csv)
둘 다 계산한다. 최종 성공 기준은 시간순 분할 기준선(RMSE)이다.
"""
import json
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def compute_baseline(train_path, test_path, split_desc):
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    y_train, y_test = train_df["price"], test_df["price"]

    train_mean = y_train.mean()
    y_pred = np.full_like(y_test, fill_value=train_mean, dtype=float)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    return {
        "설명": f"{split_desc} 기준, 평가용 전부를 훈련용 price 평균값으로 찍었을 때의 성능",
        "타깃": "price",
        "split": split_desc,
        "n_train": len(y_train),
        "n_test": len(y_test),
        "train_mean_price": round(train_mean, 2),
        "RMSE": round(rmse, 2),
        "MAE": round(mae, 2),
        "R2": round(r2, 6),
    }


# 랜덤 분할 기준선
result_random = compute_baseline("outputs/day6/train.csv", "outputs/day6/test.csv", "8:2 랜덤 (random_state=42)")
with open("outputs/day6/baseline.json", "w", encoding="utf-8") as f:
    json.dump(result_random, f, ensure_ascii=False, indent=2)
pd.DataFrame([result_random]).to_csv("outputs/day6/baseline.csv", index=False, encoding="utf-8-sig")
print("[랜덤 분할 기준선]", result_random)

# 시간순 분할 기준선 (최종 공식 기준)
result_time = compute_baseline("outputs/day6/train_time.csv", "outputs/day6/test_time.csv", "날짜순 정렬 후 앞 80%/뒤 20%")
with open("outputs/day6/baseline_time.json", "w", encoding="utf-8") as f:
    json.dump(result_time, f, ensure_ascii=False, indent=2)
pd.DataFrame([result_time]).to_csv("outputs/day6/baseline_time.csv", index=False, encoding="utf-8-sig")
print("[시간순 분할 기준선 - 공식 기준]", result_time)
