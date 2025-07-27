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

tab1, tab2, tab3 = st.tabs(["📊 ภาพรวม", "🎓 เลือกมหาวิทยาลัย", "🔍 หลักสูตรที่ไม่มีข้อมูลค่าใช้จ่าย"])

# -------------------------------
# 📊 Tab 1: ภาพรวม
# -------------------------------
with tab1:
    col1, col2, col3 = st.columns(3)

    avg_fee = df["ค่าใช้จ่ายต่อภาคการศึกษา"].mean()
    max_fee = df.loc[df["ค่าใช้จ่ายต่อภาคการศึกษา"].idxmax()]
    min_fee = df.loc[df["ค่าใช้จ่ายต่อภาคการศึกษา"].idxmin()]

    col1.metric("ค่าใช้จ่ายเฉลี่ยต่อภาคการศึกษาของ Data", f"{avg_fee:,.0f} บาท")
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
    st.subheader("🏫 เลือกมหาวิทยาลัยและวิทยาเขตเพื่อดูหลักสูตร")

    # รวมข้อมูล df และ df_no_fee ให้กลายเป็น df_all
    df_num = df.copy()
    df_num["ค่าใช้จ่ายแสดงผล"] = df_num["ค่าใช้จ่ายต่อภาคการศึกษา"].map(lambda x: f"{x:,.0f} บาท")

    df_text = df_no_fee.copy()
    df_text["ค่าใช้จ่ายแสดงผล"] = df_text["ค่าใช้จ่าย"]

    # สร้างคอลัมน์ที่ขาดหายไปให้ตรงกัน
    for col in df.columns:
        if col not in df_text.columns:
            df_text[col] = None
    for col in df_text.columns:
        if col not in df_num.columns:
            df_num[col] = None

    # รวมสอง DataFrame
    df_all = pd.concat([df_num, df_text], ignore_index=True)

    # Dropdowns
    uni_list = sorted(df_all["ชื่อมหาวิทยาลัย"].dropna().unique())
    selected_uni = st.selectbox("เลือกมหาวิทยาลัย", uni_list)

    campus_list = sorted(df_all[df_all["ชื่อมหาวิทยาลัย"] == selected_uni]["วิทยาเขต"].dropna().unique())
    selected_campus = st.selectbox("เลือกวิทยาเขต", campus_list)

    # กรองข้อมูลที่เกี่ยวข้อง
    df_filtered = df_all[(df_all["ชื่อมหาวิทยาลัย"] == selected_uni) & (df_all["วิทยาเขต"] == selected_campus)]

    if not df_filtered.empty:
        st.markdown(f"### หลักสูตรทั้งหมดใน {selected_uni} ({selected_campus})")

        # ตารางหลักสูตรพร้อมค่าใช้จ่ายแสดงผล
        show_df = df_filtered[["ชื่อหลักสูตร", "ค่าใช้จ่ายแสดงผล"]].sort_values("ชื่อหลักสูตร")
        st.dataframe(show_df, use_container_width=True)

        # แยกเฉพาะหลักสูตรที่มีค่าใช้จ่ายเป็นตัวเลขสำหรับกราฟ
        df_numeric_only = df_filtered[pd.to_numeric(df_filtered["ค่าใช้จ่ายต่อภาคการศึกษา"], errors='coerce').notnull()]
        
        if not df_numeric_only.empty:
            fig = px.bar(
                df_numeric_only.sort_values("ค่าใช้จ่ายต่อภาคการศึกษา"),
                x="ชื่อหลักสูตร",
                y="ค่าใช้จ่ายต่อภาคการศึกษา",
                text="ค่าใช้จ่ายแสดงผล",
                color="ชื่อหลักสูตร"
            )
            fig.update_traces(texttemplate="%{text}", textposition="outside")
            fig.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=[],
                    showline=True,
                    showgrid=True,
                ),
                height=500
                )
            st.plotly_chart(fig, use_container_width=True)

            # ค่าใช้จ่าย min/max
            min_fee = df_numeric_only["ค่าใช้จ่ายต่อภาคการศึกษา"].min()
            max_fee = df_numeric_only["ค่าใช้จ่ายต่อภาคการศึกษา"].max()
            col1, col2 = st.columns(2)
            col1.metric("ค่าใช้จ่ายต่ำสุด", f"{min_fee:,.0f} บาท")
            col2.metric("ค่าใช้จ่ายสูงสุด", f"{max_fee:,.0f} บาท")
        else:
            st.info("ไม่มีหลักสูตรที่ระบุค่าใช้จ่ายเป็นตัวเลขสำหรับการสร้างกราฟ")

    else:
        st.warning("ไม่พบข้อมูลสำหรับมหาวิทยาลัยหรือวิทยาเขตที่เลือก")

# -------------------------------
# 💡 Tab 3: คำแนะนำ (Insight)
# -------------------------------
with tab3:
    st.subheader("🔍 รายการที่ไม่มีข้อมูลค่าใช้จ่าย")

    def render_link(text):
        if isinstance(text, str) and text.startswith("http"):
            return f"{text}"
        return "ไม่พบข้อมูลค่าใช้จ่าย"

    df_no_fee["ดูรายละเอียด"] = df_no_fee["ค่าใช้จ่าย"].apply(render_link)

    selected_uni = st.selectbox("เลือกมหาวิทยาลัย", ["ทั้งหมด"] + sorted(df_no_fee["ชื่อมหาวิทยาลัย"].unique()))

    filtered_df = df_no_fee.copy()
    if selected_uni != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df["ชื่อมหาวิทยาลัย"] == selected_uni]

    show_cols = ["ชื่อมหาวิทยาลัย"]
    if "วิทยาเขต" in filtered_df.columns:
        show_cols.append("วิทยาเขต")
    show_cols += ["ชื่อหลักสูตร", "ดูรายละเอียด"]

    st.dataframe(filtered_df[show_cols], use_container_width=True)
