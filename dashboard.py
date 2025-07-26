import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="TCAS ค่าใช้จ่าย",
    page_icon="💸",
    layout="wide"
)

# โหลดข้อมูล
@st.cache_data
def load_data():
    return pd.read_excel("tcas_cleaned.xlsx")

df = load_data()

# Sidebar - Filter สาขาวิชา
st.sidebar.header("🔍 ตัวกรอง")
major_list = sorted(df["ชื่อหลักสูตร"].dropna().unique())
selected_major = st.sidebar.selectbox("เลือกสาขาวิชา", ["ทั้งหมด"] + major_list)

# Filter ข้อมูล
if selected_major != "ทั้งหมด":
    df = df[df["ชื่อหลักสูตร"] == selected_major]

# Dashboard Title
st.title("📊 ค่าใช้จ่าย TCAS ต่อภาคการศึกษา")

# Bar Chart
if not df.empty:
    fig = px.bar(
        df.sort_values("ค่าใช้จ่ายต่อภาคการศึกษา", ascending=False),
        x="ชื่อมหาวิทยาลัย",
        y="ค่าใช้จ่ายต่อภาคการศึกษา",
        color="ชื่อมหาวิทยาลัย",
        title="ค่าใช้จ่ายต่อภาคการศึกษาตามมหาวิทยาลัย",
        text="ชื่อหลักสูตร"
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # Table
    st.subheader("📄 ข้อมูลทั้งหมด")
    st.dataframe(df, use_container_width=True)
else:
    st.warning("ไม่พบข้อมูลสำหรับสาขาวิชานี้")
