# 작업로그

## 2026-08-21

**대상 데이터**: `data/raw/kc_house_data.csv` (King County 주택 매매 기록, 21,613행 x 21열)

### 진행 내용

1. **데이터 후보 검토**
   - `data/raw/breach_report.csv`(의료정보 유출 신고 데이터)를 먼저 검토했으나, 연속형 타겟 후보가 `Individuals Affected` 하나뿐이고 분포가 극단적으로 왜곡되어 있어 회귀 실습용으로 보류.
   - `data/raw/kc_house_data.csv`로 교체.

2. **구조 파악**
   - 행/열 수: 21,613행 x 21열
   - 컬럼별 자료형, 결측치 확인 → 전 컬럼 결측 0개
   - 수치형 컬럼 기초 통계, 범주형(`date`) 및 저카디널리티 정수 컬럼(`waterfront`, `view`, `condition`, `grade`, `zipcode` 등) 확인
   - 한 행의 의미: 주택 한 채의 매매 거래 1건

3. **회귀 가능 여부 판정 (6개 조건)**
   - 행 수(≥300), 컬럼 수(5~30), 연속형 타겟(`price`) 존재, 결측치(30% 초과 컬럼 없음), 날짜 컬럼(`date`) 존재 → 모두 통과
   - 타겟 누출 조건에서 `sqft_above + sqft_basement = sqft_living` (100% 일치, 파생 관계) 확인 → 변수 정리 필요 판정

4. **변수 정리**
   - `sqft_above` vs `sqft_basement` 비교: `sqft_above`는 `sqft_living`과 상관계수 0.877로 중복성 높음 → **`sqft_above` 제외, `sqft_basement` 유지**
   - `id`는 단순 행 식별자로 제외
   - `date`는 이번 회귀에서 미사용(추후 특성 가공 필요)

5. **베이스라인 회귀 실행**
   - `id`, `sqft_above`, `date` 제외, `zipcode`는 원-핫 인코딩 후 LinearRegression 실행 (8:2 분할, random_state=42)
   - 결과: R²(test) 0.8068 / R²(train) 0.8083 / RMSE 170,912 / MAE 98,749
   - train/test R² 유사하여 과적합 징후 없음
   - `bedrooms`, `sqft_basement` 계수 부호가 직관과 반대로 나와 다중공선성 의심 → 추후 확인 필요

6. **분석 주제 후보 5개 도출 후 1번 선정**
   - 후보: ① `price`←`sqft_living`,`grade`,`zipcode` ② `sqft_living`←`bedrooms`,`bathrooms`,`floors` ③ `sqft_living15`←`sqft_living`,`zipcode`,`grade` ④ `sqft_lot`←`zipcode`,`floors`,`condition` ⑤ `sqft_basement`←`sqft_living`,`yr_built`,`grade`
   - 오늘 안에 끝낼 수 있는 것으로 ①, ②를 추천(결측·왜곡·0값 폭탄 문제 없어 전처리 부담 적음)
   - 사용자가 **①번(`price` 예측)** 선택

7. **① 주제로 베이스라인 회귀 실행 (입력 3개만)**
   - `price ← sqft_living, grade, zipcode`(원-핫), 8:2 분할, random_state=42
   - 결과: R²(test) 0.7408 / R²(train) 0.7453 / RMSE 197,933 / MAE 111,175
   - 해석: `sqft_living` +1sqft당 가격 +198달러, `grade` +1단계당 +59,317달러
   - 과적합 징후 없음(train/test R² 유사)

8. **문제 정의 템플릿 작성**
   - 데이터: `kc_house_data.csv` / 타깃: `price` / 입력: `sqft_living`, `grade`, `zipcode`
   - 수혜자: 부동산 중개인·매수자
   - 성공 기준: **R² 0.7 이상, MAE가 중앙값 매매가(45만 달러)의 25% 이내(약 11만 달러 이내)** — 7번 결과가 이 기준을 이미 충족

9. **SOP 문서 작성**
   - `docs/SOP.md` 생성: "데이터 구조 파악" 5단계 절차(행/열, 자료형, 결측, 수치형 통계, 범주형 값종류)와 `kc_house_data.csv` 적용 결과를 표로 정리

10. **`docs/problem_definition.md` 작성 (v0, 오전)**
    - 데이터 선정 이유(3줄), 오늘 풀 문제(3줄), 확인해 볼 것 3가지, 후보 5개 중 ①번을 고른 이유를 문서화
    - 오후에 바뀔 수 있어 버전 표기(v0)를 문서 상단에 남김

11. **오늘 확인해 볼 것 3가지 도출**
    - price 극단치(최대 7,700,000달러)가 MAE를 얼마나 끌어올리는지
    - `sqft_living`-`price` 관계가 실제로 선형인지(산점도 확인 필요)
    - `zipcode`(71개 지역)별 가격 차이가 실제로 유의미한지
    - → `docs/problem_definition.md`의 3번 항목으로 저장, 아직 미실행

12. **EDA① — price 극단치가 오차에 미치는 영향 확인**
    - 100만 달러 이상 매물: 1,492건(6.90%) / 200만 달러 이상: 205건(0.95%) / 300만 달러 이상: 50건(0.23%)
    - test셋 전체 MAE 111,175달러 → 100만 달러 이상 매물 제외 시 MAE 89,983달러로 **약 19% 감소**
    - 결론: 전체의 7% 미만인 초고가 매물이 오차 평가를 크게 왜곡시키는 중 → 아직 아무 조치 안 함(확인만)

13. **EDA② — 값 단위 정밀 점검 (결측 위장값 / 문자로 읽힌 숫자 컬럼)**
    - 결측 위장값(`?`,`.`,`-`,`N/A`,`없음`,`미상`,빈칸) 전수 검사 → **21개 컬럼 전부 0건**, 위장 결측 없음
    - "0"의 의미가 컬럼마다 다름을 확인: `waterfront`/`view`/`yr_renovated`/`sqft_basement`의 0은 정상 인코딩("없음"의 의미)이지만, **`bedrooms`=0(13건)과 `bathrooms`=0.00(10건)은 의심스러움**(입력 누락 또는 비주거용 가능성) — 원인 미확인
    - 숫자→문자 오분류 컬럼: `date` 외에는 없음(20개 컬럼 전부 정상 숫자형, 쉼표·단위 섞임 없음)
    - **`price` 컬럼 표기 불일치 발견**: 원본 텍스트에 일반 숫자(`221900`)와 과학적 표기법(`1.225e+006`)이 섞여 있음(1,492건, 6.9%) — pandas는 둘 다 정상 파싱하지만, 이 비율이 "100만 달러 이상 매물 비율"과 정확히 일치 → 고가 매물일수록 지수 표기로 저장된 패턴으로 추정
    - 기타 희귀값 재확인: `bedrooms`=33(1건), `grade`=1(1건)/3(3건), `condition`=1(30건)
    - 결론: 아직 아무것도 수정 안 함(확인만), 위 발견들은 전처리 결정 시 참고

14. **타깃(`price`) 누출 컬럼 점검**
    - 기준 3가지로 검사: ① 타깃의 합계·차액·비율·등급으로 만들어진 컬럼 ② 타깃이 결정된 뒤에야 알 수 있는 컬럼 ③ 타깃과 상관계수 0.95 초과 컬럼
    - ① 해당 없음: `price`는 다른 컬럼의 합/차/비율로 계산되지 않음 (`sqft_above+sqft_basement=sqft_living` 관계는 입력변수끼리의 관계이지 `price`와 무관, 5번 항목에서 이미 확인)
    - ② 해당 없음: 거래 성사 이후에만 알 수 있는 컬럼(감정가, 수수료 등) 없음
    - ③ 해당 없음: 전 컬럼 중 `price`와 상관계수 최고는 `sqft_living`(0.702), 0.95 넘는 컬럼 0개
    - 결론: **명백한 타깃 누출 컬럼 없음** → 아무것도 제거하지 않음

15. **전처리 결정 및 적용 (사용자 최종 판단)**
    - 발견한 문제 5가지에 대해 삭제/채우기/그대로두기 장단점 제시 후 사용자가 최종 결정:
      1. price 극단치(100만 달러 이상) → **삭제**
      2. bedrooms=33 이상치 → **삭제**
      3. bedrooms=0 / bathrooms=0 → **삭제**
      4. price 표기 혼용(과학적 표기법) → **그대로 두기** (pandas가 이미 정상 처리 중이라 조치 불필요)
      5. grade/condition 희귀 카테고리 → **그대로 두기**
    - 적용 결과: 원본 21,613행 → 정제 후 **20,106행** (1,507건 삭제, 6.97%)
      - price>=100만 달러: 1,492건
      - bedrooms=33: 1건
      - bedrooms=0/bathrooms=0: 16건 (일부는 위 조건과 중복)
    - 정제 후 `price` 범위: 78,000~999,999달러(평균 467,116), `bedrooms` 1~11, `bathrooms` 최소 0.5
    - **원본(`data/raw/kc_house_data.csv`)은 수정하지 않음** — 정제 결과를 처음엔 `outputs/day6/kc_house_data_cleaned.csv`로 저장

16. **처리 전후 비교표 작성 + 저장 위치 정리**
    - 처리 전후 비교: 행 수 21,613→20,106(-6.97%), price 최대값 7,700,000→999,999, price 평균 540,088→467,116, price 표준편차 367,127→195,502(거의 절반), bedrooms 최대값 33→11, bedrooms 최소값 0→1, bathrooms 최소값 0.0→0.5
    - 정제 파일을 **`data/processed/kc_house_data_cleaned.csv`**로 재저장(신규 위치)
    - 기존에 있던 `outputs/day6/kc_house_data_cleaned.csv`는 중복이라 **삭제**
    - `data/` 폴더에 `processed`의 오타로 보이는 빈 폴더 `data/rocessed`가 원래부터 있었음을 확인 → 사용자 확인 후 **삭제**

17. **컬럼 제외 / 결측 처리 체크리스트 작성 → `docs/problem_definition.md` 5번 항목 추가**
    - 컬럼 제외: `id`, `sqft_above`, `date` — 이유는 각각 단순 식별자(무의미), `sqft_living`과 상관계수 0.877로 중복, 문자열이라 가공 없이 사용 불가
    - 결측 처리: **그대로 두었다(처리 안 함)** — 21개 컬럼 전부 결측 0개라 처리할 결측 자체가 없었음

18. **처리 전후 비교표를 `docs/problem_definition.md` 6번 항목으로 추가**
    - 16번에서 만든 비교표(행 수, price/bedrooms/bathrooms 전후 수치)를 그대로 옮김, 저장 위치(`data/processed/kc_house_data_cleaned.csv`) 명시

19. **문제정의 "확인해 볼 것 3가지" 그래프 3장 작성 (한글 폰트 AppleGothic)**
    - `outputs/day6/q1_outlier_effect_on_mae.png`: price 극단치 포함/제외 MAE 비교(111,175→65,069, 약 41% 감소, 원본 데이터로 재학습 기준) — 극단치 삭제 결정을 뒷받침
    - `outputs/day6/q2_sqft_living_vs_price.png`: sqft_living-price 선형 추세선 vs 구간별 실제 평균 — sqft_living 4,000까지는 선형 가정이 대체로 타당, 그 이후는 표본 부족
    - `outputs/day6/q3_price_by_zipcode.png`: zipcode별 price 중앙값 정렬 막대그래프 — 최저 235,000 ~ 최고 875,000달러(3.7배 차이), 지역 효과 뚜렷
    - 질문1은 순수 데이터 그래프보다 "모델 재학습 결과 비교"에 가까움을 사용자에게 안내, 대안(price 히스토그램+100만달러 기준선)도 제시

20. **타깃-변수 관계 그래프 3장 작성 (숫자/범주/상관관계, 정제본 기준)**
    - `outputs/day6/rel1_numeric_vs_price.png`: sqft_living/grade/bathrooms/sqft_living15 vs price 산점도
    - `outputs/day6/rel2_categorical_vs_price.png`: waterfront/view/condition별 price 박스플롯
    - `outputs/day6/rel3_correlation_heatmap.png`: 전체 숫자형 19개 변수 상관관계 히트맵
    - 상식과 맞는 패턴: 면적·등급·바다전망이 클/좋을수록 가격 상승
    - **의외인 패턴(하이라이트)**: `condition`(건물 상태 등급)이 price와 상관계수 거의 0 — "상태 좋으면 비쌀 것"이라는 직관과 어긋남. 이전 베이스라인 회귀의 `bedrooms` 음수 계수도 같은 계열의 이상 신호로 재확인

21. **평균값 기준선(baseline) 계산 및 저장**
    - 정제본(`data/processed/kc_house_data_cleaned.csv`)을 8:2(`random_state=42`)로 분할, 평가용 전부를 훈련용 `price` 평균(467,842달러)으로 예측했을 때 성능 계산
    - 결과: RMSE 195,080 / MAE 160,757 / R² -0.0003 (정의상 회귀모델의 하한선)
    - `outputs/day6/baseline.json`, `outputs/day6/baseline.csv`로 저장 → 앞으로 만들 모든 모델은 이 수치와 비교 예정

22. **베이스라인 계산에 쓴 train/test 분할을 파일로 저장**
    - `outputs/day6/train.csv`(16,084행), `outputs/day6/test.csv`(4,022행) — 8:2, `random_state=42`
    - 저장 이유: 코드로 매번 재분할해도 seed 고정이면 동일 결과지만, 라이브러리 버전 변화 등에 안전하게 대비하기 위해 고정 파일로도 남김

23. **`docs/problem_definition.md`를 v1으로 갱신 (v0는 보존, 아래에 추가)**
    - v0는 삭제하지 않고 그대로 둔 채 "v1 (오후에 바뀐 것)" 섹션을 하단에 추가
    - 바뀐 것: 사용 데이터(원본→정제본), 성공 기준(R² 0.7·MAE 11만달러 절대 기준 → 기준선 RMSE 195,080 대비 상대 기준)
    - 안 바뀐 것: 타깃(`price`), 입력변수(`sqft_living`,`grade`,`zipcode`), 수혜자
    - 바뀐 이유: 정제로 price 표준편차가 거의 절반(367,127→195,502)으로 줄어 오전에 정한 절대 숫자 기준이 더 이상 안 맞아서, "평균값보다 나은가"라는 상대 기준(baseline)으로 전환
    - 오늘의 성공 기준 한 줄: RMSE가 195,080보다 낮으면 성공

24. **날짜 컬럼을 반영한 시간순 분할로 교체 (랜덤 분할의 문제 설명 후 적용)**
    - 이유: 랜덤 8:2는 테스트 기간 전후 거래가 학습셋에 섞여 들어가 "미래를 보고 과거를 맞히는" 상황이 될 수 있음 — 1년(2014-05~2015-05) 동안 시세 변동이 있었다면 랜덤 분할 성능이 실제보다 낙관적으로 나올 위험
    - `date`를 파싱해 오름차순 정렬 후 앞 80%/뒤 20%로 분할
    - `outputs/day6/train_time.csv`(16,084행, 2014-05-02~2015-03-09), `outputs/day6/test_time.csv`(4,022행, 2015-03-09~2015-05-24) 저장
    - 기존 랜덤 분할 파일(`train.csv`,`test.csv`)은 유지, 시간순은 `_time` 접미사로 구분

25. **시간순 분할 기준으로 기준선(baseline) 재계산**
    - train_time 평균 price(464,388)로 test_time 전체를 예측 → RMSE 195,257 / MAE 158,506 / R² -0.0049
    - 랜덤 분할 기준선(RMSE 195,080)과 거의 비슷하지만 R²가 더 나쁨(-0.0049) → train/test 기간 간 시세 차이가 약간 있다는 신호
    - `outputs/day6/baseline_time.json`, `outputs/day6/baseline_time.csv`로 저장
    - `docs/problem_definition.md` v1의 성공 기준(RMSE 195,080)은 랜덤 분할 기준이라, 시간순 분할로 갈아탈 경우 195,257로 갱신 필요 — 사용자 확인 대기 중

26. **`docs/problem_definition.md`를 v2로 갱신 (v0·v1은 보존, 아래에 추가)**
    - 바뀐 것: train/test 분할 방식(랜덤→시간순), 기준선 RMSE(195,080→195,257)
    - 안 바뀐 것: 타깃, 입력변수, 수혜자, 사용 데이터(정제본)
    - 바뀐 이유: `date` 컬럼 존재를 재확인하면서 랜덤 분할의 미래 정보 누출 위험을 인지 → 시간순 분할로 교체, 기준선도 그에 맞춰 재계산
    - 오늘의 성공 기준 한 줄: 시간순 분할 기준 RMSE가 195,257보다 낮으면 성공

27. **정제본 + 시간순 분할로 3개 모델(선형회귀/랜덤포레스트/XGBoost) 학습 및 기준선 비교**
    - 입력 변수 17개(전체 컬럼 중 `id`, `sqft_above`, `date`, `price` 제외) — 각각 무의미한 식별자, `sqft_living`과 중복(상관 0.877), 미가공 문자열이라서 제외. 나머지는 결측·타깃누출 없어 전부 포함
    - 범주형 처리: `zipcode`(70개 지역)만 원-핫 인코딩, `waterfront`/`view`/`condition`/`grade`는 순서형이라 숫자 그대로 사용. 세 모델 모두 동일 피처셋 사용
    - `train_time.csv`/`test_time.csv`로 학습·평가, 기준선은 `baseline_time.json` 사용
    - 결과: 기준선 RMSE 195,257 → 선형회귀 88,477(R² 0.794) → XGBoost 82,574(R² 0.820) → **랜덤포레스트 81,472(R² 0.825, 최고 성능)**
    - `outputs/day6/model_comparison.csv`로 저장
    - 사용자가 기준선 수치가 이상해 보인다고 문의 → `model_comparison.csv`의 기준선 값이 `baseline_time.json`과 소수점까지 일치(195,256.84)함을 대조해 확인, 랜덤분할 기준선(`baseline.json`, 195,080.21)과 섞이지 않았음을 검증. 기준선 RMSE가 큰 것은 정상(평균 예측 RMSE ≈ price 표준편차 195,502와 거의 일치하는 게 수학적으로 당연)이라고 설명

28. **기준선 대비 개선율(%) 계산 + 실사용 가능성 평가**
    - RMSE 개선율: 선형회귀 54.7%↓, XGBoost 57.7%↓, 랜덤포레스트 58.3%↓ / MAE 개선율: 각각 58.9%, 62.5%, 63.3%↓
    - `outputs/day6/model_comparison_with_improvement.csv`로 저장
    - 실사용 가능성: 랜덤포레스트 MAE(58,176)가 price 평균의 12.5%, 중앙값의 13.4%, 전체 범위(92만달러)의 6.3% 수준 → v0 성공 기준(25% 이내)을 여유 있게 통과, "정확한 감정가는 아니지만 1차 스크리닝 용도로는 실무에 쓸 만한 수준"으로 결론
    - 체크리스트(4행 표/기준선보다 개선/변수 설명 첨부) 재확인 → 3개 항목 모두 충족, "기준선보다 확실히 좋다"로 판정

29. **가장 좋은 모델(랜덤포레스트)의 변수 중요도 그래프 작성**
    - `outputs/day6/rf_feature_importance.png` (한글 폰트 AppleGothic, zipcode 69개 더미는 합산해서 표시)
    - 순위: `lat`(0.386) > `sqft_living`(0.321) > `grade`(0.090) > `long`(0.046) > `sqft_living15`(0.031) ... `zipcode`합산은 0.021로 오히려 낮음
    - 사용자 질문에 답하며 해석: `lat`/`sqft_living`이 상식과 일치(위치+면적), `zipcode`보다 `lat`이 더 중요한 건 트리 모델이 연속형 변수를 더 세밀하게 분할할 수 있기 때문(인코딩 방식 차이일 뿐 결론은 동일: 위치가 중요). `bedrooms`/`condition`이 거의 바닥인 것도 이전 발견(20번 항목의 의외 패턴)과 일관됨을 재확인

30. **`lat`(위도) 중요도의 타당성 검증**
    - price-`lat` 상관계수 0.441 (grade, sqft_living 다음으로 높음)
    - 위도 8구간별 평균 price 계산: 남쪽(47.16~47.23) 295,134달러 → 북쪽(47.62~47.70) 603,394달러로 약 2배 상승 후 최북단에서 소폭 하락
    - `long`(경도) 상관계수는 0.08로 훨씬 약함 → 남북 방향(도심 근접도)이 동서보다 가격을 훨씬 잘 설명
    - 결론: 우연이 아니라 실제 지리적 패턴(시애틀·벨뷰 등 도심 근접 지역이 비쌈)을 반영한 결과

31. **지리 지식 없이도 이해할 수 있는 위치-가격 시각화 추가**
    - `outputs/day6/geo_price_map.png`: `long`(x축)·`lat`(y축)에 실제 위치대로 점을 찍고 `price`를 색으로 표현(밝을수록 비쌈)
    - 점을 찍기만 해도 킹 카운티 지형이 드러나고, 위도 47.5~47.7 부근(가운데 위쪽 띠)에 밝은 색이 몰려 있어 "위쪽 동네가 비싸다"를 한눈에 보여줌 — 30번의 표 결과를 그림 한 장으로 압축

32. **`geo_price_map.png`에 주요 도시 라벨 추가**
    - 시애틀, 벨뷰, 레드먼드, 렌턴, 켄트, 오번 6개 도시를 잘 알려진 위경도 좌표로 빨간 별(★) 표시하여 갱신 저장
    - 결과: 시애틀·벨뷰·레드먼드(북쪽, 밝은색=고가 지역)와 켄트·오번(남쪽, 어두운색=저가 지역)이 지도상에서 뚜렷하게 대비되어, 지리 지식 없이도 "북쪽이 비싸다"는 30번 결과를 직관적으로 확인 가능해짐

33. **예측 오차가 가장 큰 5건 분석**
    - 랜덤포레스트(`train_time`/`test_time`) 예측값-실제값 오차 계산, 절대오차 상위 5건을 `outputs/day6/top5_errors.csv`로 저장
    - 5건 전부 모델이 실제보다 훨씬 낮게 예측(저평가), 오차 -41만~-58만 달러
    - 공통점: sqft_living이 작고(1,080~1,850) 건축연도가 오래됨(1900~1945년)인데 실제가는 79.5만~97.5만 달러(테스트 중앙값의 약 2배); grade는 평균보다 낮음(5~7); waterfront/view 없음; zipcode가 전부 시애틀 도심권(98106·98107·98115·98117·98126)
    - 해석: 작고 낡았지만 시애틀 인기 동네의 땅값 프리미엄이 큰 집을, 모델이 `lat`/`long`으로 큰 지역효과는 잡아도 동네 단위의 미세한 프리미엄까지는 못 잡아내 체계적으로 저평가하는 경향 확인

34. **저평가 패턴(33번) 보완용 피처 4개 추가 시도**
    - 추가한 피처: `zipcode_mean_price`(train으로만 계산해 누출 방지), `house_age`(판매연도-건축연도), `living_lot_ratio`(sqft_living÷sqft_lot), `was_renovated`(리모델링 여부)
    - 전체 성능은 소폭 개선: RMSE 81,472→80,491(-1.2%), MAE 58,176→57,609, R² 0.8250→0.8292. `zipcode_mean_price`가 신규 1위 변수(중요도 0.445)로 등극
    - 그러나 33번에서 찾은 저평가 5건은 거의 개선되지 않음(오차가 비슷하거나 일부는 더 나빠짐)
    - 원인 확인: 이 5채는 **자기 동네 평균가 대비로도 1.58~2.54배** 비싼 극단적 이상치라, `zipcode_mean_price` 같은 동네 단위 집계 피처로는 설명이 안 됨 → 조망 디테일, 리모델링 수준, 스쿨존 등 현재 데이터에 없는 요인이 작용했을 가능성으로 결론
    - 결론: 전체 모델 성능 개선에는 도움 됐지만, 특정 지역 내 극단적 이상치 보정에는 한계 확인

35. **비전문가용 최종 리포트 작성**
    - `docs/problem_definition.md`(v0~v2)를 다시 읽고, `docs/WORKLOG.md` 전체 진행 내역을 바탕으로 `docs/REPORT.md` 작성
    - 구성: ①데이터 선정 이유 ②문제 정의(후보 선정 이유, v0→v1→v2 변화와 이유) ③발견한 문제와 판단(삭제/유지 근거) ④확인 질문 3가지 답변(상식 일치/의외/미확인 부분 포함) ⑤기준선 대비 성능(개선율, 실사용 가능성, 변수 중요도, 저평가 한계) ⑥다음 단계
    - 전문용어 최소화, 사용자가 실제로 내린 판단(삭제/유지, 기준 변경 이유 등)이 드러나도록 서술, 숫자는 전부 지금까지 계산된 실제 값만 사용(새로 지어내지 않음)

36. **`docs/REPORT.md`에서 breach_report 관련 서술 삭제**
    - 사용자 요청으로 1번 섹션의 "처음엔 breach_report.csv를 검토했으나…" 문단 삭제, 나머지 문장으로 자연스럽게 연결
    - `docs/WORKLOG.md`의 관련 기록(1번 항목)은 실제 있었던 일의 기록이라 그대로 유지하기로 함(사용자 확인)

37. **프로젝트 루트에 새 `README.md` 작성**
    - 기존 `docs/README.md`는 첫 번째 프로젝트(자전거 대여 수요 예측, bike-share-demand-portfolio)의 README가 그대로 잘못 들어와 있는 파일임을 사용자가 확인 — 그 파일은 건드리지 않고 별도로 프로젝트 루트에 `README.md` 신규 생성
    - 구성: 프로젝트 개요, 주요 문서 링크, 핵심 결과표(기준선 대비 개선율), **"이 프로젝트가 첫 번째와 다른 점"** 섹션
    - "다른 점" 섹션 내용: 첫 프로젝트는 강사가 데이터·순서를 지정, 이번엔 데이터 선정·문제 정의·전처리 판단을 직접 수행. 후보 5개 중 ①(집값 예측)을 고른 이유 명시. 직접 내린 판단 3가지를 근거와 함께 구체적으로 서술 — ①price 100만달러 이상 삭제(MAE 비교로 근거 확인 후 결정) ②랜덤→시간순 분할 전환(date 컬럼 인지 후 미래정보 누출 문제 판단) ③bedrooms/bathrooms=0 16건 삭제(원인 불명이나 소수라 판단)
    - 과장 없이 사실만 서술하라는 요청에 따라 지금까지 실제로 계산·결정된 내용만 기재

38. **재현 가능성 판정 (처음 보는 사람 관점)**
    - 판정: **재현 불가** — `scripts/`가 완전히 비어있어 오늘 실행한 코드가 파일로 하나도 안 남아있었음
    - "없어서 못 하는 것": 실행 가능한 스크립트, `requirements.txt`, 실행 방법 안내, 피처엔지니어링 실험(34번) 결과 파일
    - "README만 읽고 이해 안 되는 것": train.csv/test.csv vs train_time.csv/test_time.csv 구분, 랜덤포레스트 입력변수 17개 목록, `outputs/day6`의 "day6" 의미, model_comparison.csv와 model_comparison_with_improvement.csv 관계

39. **`scripts/`에 재현 가능한 파이프라인 10개 작성 및 실행 검증**
    - `01_clean_data.py`~`10_geo_price_map.py` 순서대로 작성 (정제→분할→기준선→모델학습→변수중요도→오차분석→분포/관계/지도 그래프)
    - 프로젝트 루트에 `requirements.txt` 추가 (pandas 2.3.3, numpy 2.0.2, scikit-learn 1.6.1, xgboost 2.1.4, matplotlib 3.9.4 — 현재 환경 버전 고정)
    - 10개 스크립트를 실제로 처음부터 끝까지 순서대로 실행해 검증 → 기존에 저장돼 있던 모든 수치(기준선 RMSE 195,256.84/195,080.21, 모델별 RMSE/MAE/R², top5 오차, 변수 중요도 순위 등)와 **완전히 동일하게 재현됨** 확인
    - `README.md`에 "재현 방법" 섹션 추가(설치·실행 명령어), 랜덤/시간순 분할 중 시간순이 공식 기준임을 명시, 입력 변수 17개 언급, AppleGothic 폰트가 macOS 전용임을 명시

40. **정리 작업 1단계 — 첫 번째 프로젝트 잔여 문서 삭제**
    - 오늘 밀린 "다음 할 일"을 3그룹(정리/원인미상 조사/성능개선)으로 정리해 사용자에게 리스트 제시, 1번(정리)부터 진행하기로 함
    - `docs/README.md`: 이미 사라진 상태라 삭제할 대상 없음. 대신 같은 내용(첫 프로젝트 자전거 대여 관련)인 `docs/CLAUDE_CODE_WORKFLOW.md` **삭제**
    - 점검 중 `docs/HOURLY_TO_DAILY_AGGREGATION.md`도 첫 프로젝트(워싱턴 D.C. 자전거 데이터) 전용 문서임을 추가 발견 → 사용자 확인 후 **삭제**
    - 결과: `docs/`에 이 프로젝트 관련 파일만 남음 (`problem_definition.md`, `REPORT.md`, `SOP.md`, `WORKLOG.md`)

41. **`outputs/day6` 명명 의미를 README에 추가**
    - 사용자 확인: "day6"은 수업 6차시를 뜻함
    - `README.md`에 "`day6`은 수업 6차시를 뜻함" 한 줄 추가

42. **`model_comparison.csv`와 `model_comparison_with_improvement.csv` 통합**
    - `scripts/04_train_models.py`를 수정해 개선율(%) 컬럼 2개를 `model_comparison.csv` 하나에 함께 저장하도록 변경, 별도 파일 생성 로직 제거
    - `outputs/day6/model_comparison_with_improvement.csv` 삭제, `04_train_models.py` 재실행으로 병합된 `model_comparison.csv` 재생성 및 수치 재검증(기존과 동일)
    - 이로써 "정리(1번)" 그룹 3개 항목(첫 프로젝트 잔여 문서 삭제, day6 의미 설명, 비교표 통합) 모두 완료

43. **GitHub 업로드 준비**
    - 사용자가 GitHub 공개 저장소에 올리기로 함. 데이터 출처: [Kaggle - King County House Sales Prediction](https://www.kaggle.com/datasets/harlfoxem/housesalesprediction)
    - 데이터 파일은 저장소에 올리지 않기로 결정 → `README.md`에 "데이터 출처" 섹션 추가(Kaggle 링크 + 받은 뒤 `data/raw/kc_house_data.csv`에 넣고 `01_clean_data.py` 실행하라는 안내), "데이터" 항목 문구를 "용량 문제로 미포함"으로 수정
    - `.gitignore` 생성: `data/raw/*.csv`, `data/processed/*.csv`, `outputs/day6/train*.csv`, `outputs/day6/test*.csv`, `.DS_Store` 제외 (결과 요약 CSV·그래프·스크립트·문서는 그대로 포함)
    - 저장소 이름 추천 요청에 `kc-house-price-portfolio` 등 3안 제시, 사용자가 `heeheej1996-design/kc-house-price-portfolio`로 생성

44. **GitHub 저장소에 최초 푸시**
    - `git init` → `.gitignore` 적용 확인(데이터 CSV 32개 파일 중 자동 제외됨) → 커밋(32개 파일) → `origin` 연결 → `main` 브랜치 push 완료
    - 저장소: https://github.com/heeheej1996-design/kc-house-price-portfolio
45. **GitHub 업로드 체크리스트 완료**
    - 브라우저 확장 미설치 상태라 WebFetch로 페이지 텍스트 기반 렌더링 확인(제목·표·링크·목록·코드블록 정상) 1차로 수행
    - 이후 사용자가 브라우저로 직접 열어 README 확인 완료(체크리스트 🔴 항목 해소)
    - 4개 체크리스트(저장소 생성/업로드/README 확인/데이터 출처 링크 대체) **전부 완료**

46. **README에 이미지 2장 추가**
    - `outputs/day6/rf_feature_importance.png`(핵심 결과 섹션), `outputs/day6/geo_price_map.png`(신규 "위치가 가격에 미치는 영향" 섹션) 추가
    - 나머지 7장(q1~q3, rel1~rel3, price_distribution)은 과정 중간 산출물 성격이라 README에서 제외, `docs/REPORT.md`에만 남김
    - 커밋 후 push 완료

47. **제출 체크리스트 6개 항목 점검**
    - 사용자가 제시한 6개 항목(EDA/기준선/train-test분할/3개모델회귀/하이퍼파라미터튜닝/리포트+깃헙) 중 5개는 이미 완료 확인, **"하이퍼파라미터 튜닝"만 누락** 상태였음을 보고

48. **랜덤포레스트·XGBoost 하이퍼파라미터 튜닝**
    - `scripts/11_tune_models.py` 작성: `GridSearchCV` + `TimeSeriesSplit(n_splits=5)`로 train_time만 사용해 튜닝(테스트셋 미사용, 교차검증도 날짜순 유지 — 04번과 같은 이유로 일반 랜덤 K-fold 대신 사용)
    - 랜덤포레스트 그리드: n_estimators[100,300], max_depth[10,None], min_samples_leaf[1,4] → 최적값이 기존 설정과 동일(max_depth=None, min_samples_leaf=1, n_estimators=300), 성능 변화 없음(RMSE 81,471.51 그대로)
    - XGBoost 그리드: n_estimators[100,300], max_depth[3,6], learning_rate[0.05,0.1] → 최적값 learning_rate=0.1, max_depth=6, n_estimators=300, **RMSE 82,573.53→79,008.21로 개선(4.3%↓)** → 튜닝 후 XGBoost가 전체 모델 중 최고 성능으로 등극(기준선 대비 59.5% 감소, R² 0.8355)
    - `outputs/day6/tuning_before_after.csv`, `outputs/day6/tuning_best_params.json` 저장

49. **README·REPORT를 튜닝 결과로 갱신**
    - `README.md` "핵심 결과" 표를 "XGBoost(튜닝 후, 최종) RMSE 79,008 / 59.5% 감소"로 갱신, 튜닝 방법(GridSearchCV+TimeSeriesSplit) 설명 추가, "재현 방법"에 `11_tune_models.py` 추가
    - `docs/REPORT.md` 5번 항목에 튜닝 전후 비교와 새 최고 모델(XGBoost) 반영, 6번 "다음 단계"에서 "하이퍼파라미터 튜닝 필요" 항목 제거(완료됨)
    - 커밋 후 GitHub push 완료

50. **잘 맞은 예측 사례(best5) 분석 — 오차 큰 5건(33번)과 대조**
    - `scripts/12_best_predictions.py` 작성: 튜닝된 XGBoost(최종 모델)로 test_time 예측, 절대오차가 가장 작은 5건 저장
    - 결과: 오차 6~58달러 수준으로 사실상 정확히 맞춤 (예: 실제 284,000달러 → 예측 284,006달러)
    - 오차 큰 5건(33번, 소형·구축·인기동네 이상치)과 달리, 이 5건은 면적·등급 등 일반적인 특징만으로 설명되는 평범한 매물로 보임 — 모델이 "전형적인 집"은 잘 맞히고 "예외적인 집"은 못 맞히는 경향을 대조로 확인
    - `outputs/day6/best5_predictions.csv` 저장, 커밋 후 GitHub push 예정

### 다음 할 일 (미착수)
- 34번 피처 엔지니어링 실험을 별도 스크립트(예: `13_feature_engineering_experiment.py`)로 정식 추가할지 결정
- `bedrooms`, `sqft_basement` 등 계수 부호 이상 원인 확인 (VIF 등 다중공선성 점검) — 21개 변수 풀모델(5번) 기준
- `date` 컬럼 가공(연/월 추출) 후 모델에 반영 여부 검토 — 34번에서 `house_age` 등 일부는 이미 시도, 중요도는 낮았음
- `condition`이 price와 무관한 이유 추가로 살펴볼지 결정 (의외 패턴 후속 조사)
- 34번 신규 피처(특히 `zipcode_mean_price`) 세트를 공식 모델 비교표(`model_comparison.csv`)에 반영할지 결정
- bedrooms/bathrooms=0인 16건의 원인 확인 (REPORT.md 6번에서도 미해결로 명시)
