import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="TCAS Executive Dashboard", page_icon="📈", layout="wide")

# โหลดข้อมูล
@st.cache_data
def load_data():
    return pd.read_excel("tcas_cleaned.xlsx"), pd.read_excel("tcas_no_fee.xlsx")

df, df_no_fee = load_data()

st.title("🎓 สรุปค่าใช้จ่ายต่อภาคการศึกษา สำหรับหลักสูตรวิศวกรรมคอมพิวเตอร์และปัญญาประดิษฐ์")
st.caption("แหล่งข้อมูล: ระบบ myTCAS ปีล่าสุด")

tab1, tab2, tab3, tab4 = st.tabs(["📊 ภาพรวม", "🎓 นักเรียนเลือกสาขา", "💡 คำแนะนำ", "🔍 หลักสูตรที่ไม่มีข้อมูลค่าใช้จ่าย"])

# -------------------------------
# 📊 Tab 1: ภาพรวม
# -------------------------------
with tab1:
    col1, col2, col3 = st.columns(3)

    avg_fee = df["ค่าใช้จ่ายต่อภาคการศึกษา"].mean()
    max_fee = df.loc[df["ค่าใช้จ่ายต่อภาคการศึกษา"].idxmax()]
    min_fee = df.loc[df["ค่าใช้จ่ายต่อภาคการศึกษา"].idxmin()]

    col1.metric("ค่าใช้จ่ายเฉลี่ยต่อภาคการศึกษา", f"{avg_fee:,.0f} บาท")
    col2.metric("ค่าใช้จ่ายสูงสุด", f"{max_fee['ค่าใช้จ่ายต่อภาคการศึกษา']:,.0f} บาท", max_fee["ชื่อมหาวิทยาลัย"])
    col3.metric("ค่าใช้จ่ายต่ำสุด", f"{min_fee['ค่าใช้จ่ายต่อภาคการศึกษา']:,.0f} บาท", min_fee["ชื่อมหาวิทยาลัย"])

    st.subheader("📌 จำนวนหลักสูตรในแต่ละสาขาวิชา")
    combined_df = pd.concat([df[["คำค้น"]], df_no_fee[["คำค้น"]]], ignore_index=True)
    count_by_major = combined_df["คำค้น"].value_counts().reset_index()
    count_by_major.columns = ["ชื่อสาขาวิชา", "จำนวนหลักสูตร"]
    fig1 = px.bar(count_by_major, x="ชื่อสาขาวิชา", y="จำนวนหลักสูตร", text="จำนวนหลักสูตร")
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("🏛️ มหาวิทยาลัยที่มีหลักสูตรมากที่สุด")
    top_uni = pd.concat([df[["ชื่อมหาวิทยาลัย"]], df_no_fee[["ชื่อมหาวิทยาลัย"]]])
    top_uni_count = top_uni.value_counts().reset_index()
    top_uni_count.columns = ["ชื่อมหาวิทยาลัย", "จำนวนหลักสูตร"]
    fig2 = px.bar(top_uni_count.head(5), x="ชื่อมหาวิทยาลัย", y="จำนวนหลักสูตร", text="จำนวนหลักสูตร")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📊 จำนวนหลักสูตรตามช่วงค่าใช้จ่าย")
    bins = [0, 10000, 12000, 15000, 20000, 30000, 100000]
    labels = ["ต่ำกว่า 10k", "10k-12k", "12k-15k", "15k-20k", "20k-30k", "มากกว่า 30k"]
    df["ช่วงค่าใช้จ่าย"] = pd.cut(df["ค่าใช้จ่ายต่อภาคการศึกษา"], bins=bins, labels=labels)
    fee_dist = df["ช่วงค่าใช้จ่าย"].value_counts().sort_index().reset_index()
    fee_dist.columns = ["ช่วงค่าใช้จ่าย", "จำนวนหลักสูตร"]
    fig3 = px.bar(fee_dist, x="ช่วงค่าใช้จ่าย", y="จำนวนหลักสูตร", text="จำนวนหลักสูตร")
    st.plotly_chart(fig3, use_container_width=True)

    # แสดงจำนวนมหาวิทยาลัยที่ไม่มีข้อมูลค่าใช้จ่าย
    num_missing = df_no_fee["ชื่อมหาวิทยาลัย"].nunique()
    st.info(f"ℹ️ พบ {num_missing} มหาวิทยาลัยที่ไม่มีข้อมูลค่าใช้จ่ายระบุไว้ในระบบ")


# -------------------------------
# 🎓 Tab 2: สำหรับนักเรียน
# -------------------------------
with tab2:
    st.subheader("🎓 เลือกสาขาที่สนใจเพื่อดูมหาวิทยาลัยที่เปิดสอน")

    major_list = sorted(df["ชื่อหลักสูตร"].dropna().unique())
    selected_major = st.selectbox("เลือกสาขาวิชา", major_list)

    df_major = df[df["ชื่อหลักสูตร"] == selected_major]
    if not df_major.empty:
        st.markdown(f"### มีทั้งหมด {len(df_major)} มหาวิทยาลัยที่เปิดสอน {selected_major}")
        fig2 = px.bar(
            df_major.sort_values("ค่าใช้จ่ายต่อภาคการศึกษา"),
            x="ชื่อมหาวิทยาลัย",
            y="ค่าใช้จ่ายต่อภาคการศึกษา",
            color="ชื่อมหาวิทยาลัย",
            text="ค่าใช้จ่ายต่อภาคการศึกษา"
        )
        fig2.update_traces(texttemplate="%{text:,.0f} บาท", textposition="outside")
        fig2.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.warning("ไม่พบข้อมูลสำหรับสาขานี้")

    st.dataframe(df_major, use_container_width=True)

# -------------------------------
# 💡 Tab 3: คำแนะนำ (Insight)
# -------------------------------
with tab3:
    st.subheader("💡 หลักสูตรที่คุ้มค่า (Low Cost / High Choice)")

    avg_by_major = df.groupby("ชื่อหลักสูตร")["ค่าใช้จ่ายต่อภาคการศึกษา"].mean().reset_index()
    avg_by_major.columns = ["ชื่อหลักสูตร", "ค่าใช้จ่ายเฉลี่ย"]

    merged = df.merge(avg_by_major, on="ชื่อหลักสูตร")
    merged["ความคุ้มค่า"] = merged["ค่าใช้จ่ายเฉลี่ย"] - merged["ค่าใช้จ่ายต่อภาคการศึกษา"]
    merged = merged.sort_values("ความคุ้มค่า", ascending=False)

    st.markdown("#### หลักสูตรที่จ่ายน้อยกว่าค่าเฉลี่ยของกลุ่มเดียวกัน")
    st.dataframe(merged[["ชื่อมหาวิทยาลัย", "ชื่อหลักสูตร", "ค่าใช้จ่ายต่อภาคการศึกษา", "ค่าใช้จ่ายเฉลี่ย", "ความคุ้มค่า"]].head(10), use_container_width=True)

    fig3 = px.bar(
        merged.head(10),
        x="ชื่อมหาวิทยาลัย",
        y="ความคุ้มค่า",
        color="ชื่อหลักสูตร",
        title="Top 10 หลักสูตรที่คุ้มค่าที่สุด",
        text="ชื่อหลักสูตร"
    )
    fig3.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)

with tab4:
    st.subheader("🔍 รายการที่ไม่มีข้อมูลค่าใช้จ่าย")

    def render_link(text):
        if isinstance(text, str) and text.startswith("http"):
            return f"[คลิกดูรายละเอียด]({text})"
        return "ไม่พบข้อมูลค่าใช้จ่าย"

    df_no_fee["ดูรายละเอียด"] = df_no_fee["ค่าใช้จ่าย"].apply(render_link)
    st.dataframe(df_no_fee[["ชื่อมหาวิทยาลัย", "ชื่อหลักสูตร", "ดูรายละเอียด"]], use_container_width=True)