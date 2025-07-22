import os
import random
import pandas as pd
import streamlit as st

# 📁 데이터 경로 설정
base_dir = os.path.dirname(__file__)
file_path = os.path.join(base_dir, "ltrcmd", "lotto_results.csv")

# 📊 데이터 불러오기
@st.cache_data
def load_lotto_data():
    if not os.path.exists(file_path):
        st.error(f"❌ CSV 파일이 존재하지 않습니다: {file_path}")
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    return df

df = load_lotto_data()

# 🚨 유효성 검사 함수
def validate_numbers(numbers, label):
    if any(n < 1 or n > 45 for n in numbers):
        st.error(f"❌ {label}는 1~45 범위의 숫자여야 합니다.")
        return False
    if len(set(numbers)) != len(numbers):
        st.error(f"❌ {label}에 중복된 숫자가 있습니다.")
        return False
    return True

# 🧠 번호 생성 함수들

# 1️⃣ 고정수/제외수 + 랜덤 추천
def generate_with_fixed_and_excluded(fixed_nums, exclude_nums):
    pool = [n for n in range(1, 46) if n not in fixed_nums and n not in exclude_nums]
    remaining = 6 - len(fixed_nums)
    if remaining < 0:
        st.error("고정수가 6개를 초과했습니다.")
        return None
    if remaining > len(pool):
        st.error("가능한 번호가 부족합니다.")
        return None
    return sorted(fixed_nums + random.sample(pool, remaining))

# 2️⃣ 최근 5회 패턴 기반 추천
def recent_pattern_based(df):
    recent_nums = df.iloc[-5:, 1:7].values.flatten()  # 번호1~6만 사용
    freq = pd.Series(recent_nums).value_counts()
    weighted = freq.index.tolist()
    while len(weighted) < 45:
        weighted.append(random.randint(1, 45))
    weighted = list(dict.fromkeys(weighted))  # 중복 제거 후 순서 유지
    return sorted(random.sample(weighted, 6))

# 3️⃣ 통계 필터 기반 추천 (홀짝, 고저, 합계 기준)
def stat_filter_recommend():
    while True:
        nums = random.sample(range(1, 46), 6)
        odd = sum(1 for n in nums if n % 2 == 1)
        high = sum(1 for n in nums if n >= 23)
        total = sum(nums)
        if 2 <= odd <= 4 and 2 <= high <= 4 and 100 <= total <= 200:
            return sorted(nums)

# 4️⃣ 무작위 추천
def pure_random():
    return sorted(random.sample(range(1, 46), 6))

# 🌐 Streamlit UI 구성
st.title("🎯 로또 번호 추천기")

option = st.selectbox("번호 생성 방식을 선택하세요", [
    "1. 고정수/제외수 지정 추천",
    "2. 최근 5회 당첨패턴 추천",
    "3. 통계 필터 추천 (홀짝, 고저, 합계)",
    "4. 무작위 추천"
])

# 옵션별 입력 및 실행
if option.startswith("1"):
    fixed = st.text_input("🔒 고정수 입력 (예: 3,12,21)").strip()
    exclude = st.text_input("🚫 제외수 입력 (예: 4,10)").strip()

    try:
        fixed_nums = sorted(set(map(int, fixed.split(",")))) if fixed else []
        exclude_nums = sorted(set(map(int, exclude.split(",")))) if exclude else []

        if validate_numbers(fixed_nums, "고정수") and validate_numbers(exclude_nums, "제외수"):
            if st.button("번호 생성"):
                st.markdown("🎯 **추천 번호 3세트:**")
                for i in range(3):
                    result = generate_with_fixed_and_excluded(fixed_nums, exclude_nums)
                    if result:
                        st.success(f"추천 {i+1}: {result}")
    except:
        st.error("숫자는 쉼표로 구분된 형식이어야 합니다. 예: 3,8,21")

elif option.startswith("2"):
    if st.button("번호 생성"):
        st.markdown("🎯 **추천 번호 3세트:**")
        for i in range(3):
            result = recent_pattern_based(df)
            st.success(f"추천 {i+1}: {result}")

elif option.startswith("3"):
    st.write("📊 기준: 홀짝 비율(2:4에서 4:2), 고저 비율(합계 100에서 200 사이)")
    if st.button("번호 생성"):
        st.markdown("🎯 **추천 번호 3세트:**")
        for i in range(3):
            result = stat_filter_recommend()
            st.success(f"추천 {i+1}: {result}")

elif option.startswith("4"):
    if st.button("번호 생성"):
        st.markdown("🎯 **추천 번호 3세트:**")
        for i in range(3):
            result = pure_random()
            st.success(f"추천 {i+1}: {result}")
