import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
import altair as alt

st.set_page_config(layout="wide")

# 데이터 불러오기
맛집 = gpd.read_file("tb_busan_stores_history.shp")
명소 = gpd.read_file("부산광역시_명소 정보.shp")
상권 = gpd.read_file("tb_commercial_counting.shp")

# 중심 좌표 계산 (평균 위치)
center = 명소.geometry.unary_union.centroid.coords[0]

# 입력값 받기
선택 = st.radio("추천 기준을 선택하세요", ["맛집", "명소", "상권", "전체"])

# 추천 점수 계산
if 선택 == "전체":
    # 전체 평균 점수 (간단히 세 데이터의 포인트 수 기준)
    맛집["추천점수"] = 1
    명소["추천점수"] = 1
    상권["추천점수"] = 1

    전체 = pd.concat([
        맛집[["geometry", "추천점수"]].copy(),
        명소[["geometry", "추천점수"]].copy(),
        상권[["geometry", "추천점수"]].copy()
    ])
else:
    if 선택 == "맛집":
        선택데이터 = 맛집
    elif 선택 == "명소":
        선택데이터 = 명소
    else:
        선택데이터 = 상권
    
    선택데이터["추천점수"] = 1  # 임시 점수 (데이터가 수치형이 아닐 경우)

    전체 = 선택데이터[["geometry", "추천점수"]]

# 지도 출력
m = folium.Map(location=[center[1], center[0]], zoom_start=11)

for _, row in 전체.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=5,
        color='blue',
        fill=True,
        fill_opacity=0.6
    ).add_to(m)

st.subheader("📍 추천 위치 지도")
st_folium(m, width=1000, height=600)

# 바 차트용 - 추천점수 높은 지역 추출 (이름 있는 경우만)
if 선택 == "전체":
    st.info("‘전체’는 점수 비교용 그래프가 제공되지 않습니다.")
else:
    if "명칭" in 선택데이터.columns:
        top = 선택데이터.nlargest(5, "추천점수")[["명칭", "추천점수"]]
        chart = alt.Chart(top).mark_bar().encode(
            x="추천점수:Q",
            y=alt.Y("명칭:N", sort='-x')
        )
        st.subheader("🏆 추천 장소 TOP 5")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("추천 장소 이름 컬럼('명칭')이 없어 차트를 출력할 수 없습니다.")
