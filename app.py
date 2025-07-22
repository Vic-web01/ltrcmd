import os
import random
import pandas as pd
import streamlit as st

# 📁 데이터 경로 설정
base_dir = os.path.dirname(__file__)
file_path = os.path.join(base_dir, "lotto_results.csv")

# 📊 데이터 불러오기
@st.cache_data
def load_lotto_data():
    if not os.path.exists(file_path):
        st.error(f"❌ CSV 파일이 존재하지 않습니다: {file_path}")
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    return df

df = load_lotto_data()

# 🚨 유효성 검사
def validate_numbers(numbers, label):
    if any(n < 1 or n > 45 for n in numbers):
        st.error(f"❌ {label}는 1~45 범위의 숫자여야 합니다.")
        return False
    if len(set(numbers)) != len(numbers):
        st.error(f"❌ {label}에 중복된 숫자가 있습니다.")
        return False
    return True

# 🧠 번호 생성 함수들
def generate_with_fixed_and_excluded(fixed_nums, exclude_nums):
    pool = [n for n in range(1, 46) if n not in fixed_nums and n not in exclude_nums]
    remaining = 6 - len(fixed_nums)
    if remaining < 0:
        st.error("❌ 고정수가 6개를 초과했습니다.")
        return None
    if remaining > len(pool):
        st.error("❌ 가능한 번호가 부족합니다.")
        return None
    return sorted(fixed_nums + random.sample(pool, remaining))

def recent_pattern_based(df):
    if df.empty:
        return []
    recent_nums = df.iloc[-5:, 1:7].values.flatten()
    freq = pd.Series(recent_nums).value_counts()
    weighted = freq.index.tolist()
    while len(weighted) < 45:
        weighted.append(random.randint(1, 45))
    weighted = list(dict.fromkeys(weighted))
    return sorted(random.sample(weighted, 6))

def stat_filter_recommend():
    while True:
        nums = random.sample(range(1, 46), 6)
        odd = sum(1 for n in nums if n % 2 == 1)
        high = sum(1 for n in nums if n >= 23)
        total = sum(nums)
        if 2 <= odd <= 4 and 2 <= high <= 4 and 100 <= total <= 200:
            return sorted(nums)

def pure_random():
    return sorted(random.sample(range(1, 46), 6))

# 🌐 외부 사이트 URL
external_url = "https://lotto.infostein.com/%eb%a1%9c%eb%98%90%eb%8b%b9%ec%b2%a8%eb%b2%88%ed%98%b8%ec%a1%b0%ed%9a%8c-%ec%a0%84%ec%b2%b4%eb%b3%b4%ea%b8%b0-%ed%91%9c%ed%98%95%ec%8b%9d/"  # ← 광고나 워드프레스 링크 입력

# 🎯 번호 생성 결과 & 광고창 열기 함수
def generate_and_display_numbers(func, *args):
    st.markdown("🎯 **추천 번호 3세트:**")
    for i in range(3):
        result = func(*args) if args else func()
        if result:
            st.success(f"추천 {i+1}: {result}")
    # 광고 페이지 새 창 열기
    if st.button("🌐 외부 페이지 열기"):
        # 외부 링크 새 창으로 열기 (사용자 클릭 필요)
        st.markdown(
            f'<meta http-equiv="refresh" content="1;URL=." />'
            f'<a href="{external_url}" target="_blank">👉 여기를 클릭하면 새 창에서 열립니다.</a>',
            unsafe_allow_html=True
        )
        st.info("1초 후 페이지가 자동 새로고침됩니다.")


# 🌐 Streamlit UI
st.title("🎯 로또 번호 추천기")

option = st.selectbox("번호 생성 방식을 선택하세요", [
    "1. 고정수/제외수 지정 추천",
    "2. 최근 5회 당첨패턴 추천",
    "3. 통계 필터 추천 (홀짝, 고저, 합계)",
    "4. 무작위 추천"
])

# 각 옵션 처리
if option.startswith("1"):
    fixed = st.text_input("🔒 고정수 입력 (예: 3,12,21)").strip()
    exclude = st.text_input("🚫 제외수 입력 (예: 4,10)").strip()

    try:
        fixed_nums = sorted(set(map(int, fixed.split(",")))) if fixed else []
        exclude_nums = sorted(set(map(int, exclude.split(",")))) if exclude else []

        if validate_numbers(fixed_nums, "고정수") and validate_numbers(exclude_nums, "제외수"):
            if st.button("번호 생성"):
                generate_and_display_numbers(generate_with_fixed_and_excluded, fixed_nums, exclude_nums)
    except:
        st.error("❌ 숫자는 쉼표로 구분된 형식이어야 합니다. 예: 3,8,21")

elif option.startswith("2"):
    if st.button("번호 생성"):
        generate_and_display_numbers(recent_pattern_based, df)

elif option.startswith("3"):
    st.write("📊 기준: 홀짝 비율(2:4,4:2), 고저 비율(합계 100부터 200사이)")
    if st.button("번호 생성"):
        generate_and_display_numbers(stat_filter_recommend)

elif option.startswith("4"):
    if st.button("번호 생성"):
        generate_and_display_numbers(pure_random)

# ℹ️ 유의사항 표시
st.markdown("---")
st.markdown("### 📌 유의사항")
st.markdown("""
1. 로또는 본질적으로 무작위성에 기반한 확률 게임임을 명심하시기 바랍니다.  
   어떠한 번호 조합도 당첨을 확실히 보장하지 않습니다.

2. 위에서 제시하는 번호 추천은 통계와 패턴 분석에 근거한 참고용 자료이며,  
   결과에 대한 법적/금전적 책임은 지지 않습니다.

3. 다양한 조합 시도와 꾸준한 구매가 당첨 확률을 높일 수 있으나,  
   투자 금액은 반드시 개인 재정 상황에 맞게 신중히 결정해야 합니다.

4. 로또 구매는 오락과 재미를 위한 행위로 생각하고,  
   과도한 기대나 무리한 지출은 피하시기 바랍니다.

5. 당첨 결과는 매 회차 완전히 독립적이며 예측 불가능성이 크므로,  
   추천 번호는 전략적 참고용임을 반드시 인지해야 합니다.

6. 로또 구매와 관련된 모든 책임은 구매자 본인에게 있으며,  
   본 웹사이트는 그에 따른 법적 또는 금전적 책임을 지지 않습니다.
""")
