import streamlit as st
import pandas as pd
import plotly.express as px

# Set up the Streamlit page
st.set_page_config(page_title="TCAS Executive Dashboard", page_icon="📈", layout="wide")

# Load data from Excel files (with caching for performance)
@st.cache_data
def load_data():
    return pd.read_excel("tcas_cleaned.xlsx"), pd.read_excel("tcas_no_fee.xlsx")

df, df_no_fee = load_data()

# Title and data source
st.title("🎓 Summary of Tuition Fees per Semester for Computer Engineering and AI Programs")
st.caption("Source: myTCAS system (latest year)")

# Create tabs for dashboard sections
tab1, tab2, tab3 = st.tabs([
    "📊 Overview",
    "🎓 University Selection",
    "🔍 Programs Without Fee Data"
])

# -------------------------------
# Tab 1: Overview
# -------------------------------
with tab1:
    # Show key metrics
    col1, col2, col3 = st.columns(3)
    avg_fee = df["ค่าใช้จ่ายต่อภาคการศึกษา"].mean()
    max_fee = df.loc[df["ค่าใช้จ่ายต่อภาคการศึกษา"].idxmax()]
    min_fee = df.loc[df["ค่าใช้จ่ายต่อภาคการศึกษา"].idxmin()]
    col1.metric("Average Fee per Semester", f"{avg_fee:,.0f} Bath")
    col2.metric("Highest Fee", f"{max_fee['ค่าใช้จ่ายต่อภาคการศึกษา']:,.0f} Bath", max_fee["ชื่อมหาวิทยาลัย"])
    col3.metric("Lowest Fee", f"{min_fee['ค่าใช้จ่ายต่อภาคการศึกษา']:,.0f} Bath", min_fee["ชื่อมหาวิทยาลัย"])

    # Bar chart: Number of programs by major
    st.subheader("📌 Number of Programs by Major")
    combined_df = pd.concat([df[["คำค้น"]], df_no_fee[["คำค้น"]]], ignore_index=True)
    count_by_major = combined_df["คำค้น"].value_counts().reset_index()
    count_by_major.columns = ["Major Name", "Number of Programs"]
    fig1 = px.bar(count_by_major, x="Major Name", y="Number of Programs", text="Number of Programs")
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)

    # Bar chart: Top universities by number of programs
    st.subheader("🏛️ Universities with Most Programs")
    top_uni = pd.concat([df[["ชื่อมหาวิทยาลัย"]], df_no_fee[["ชื่อมหาวิทยาลัย"]]])
    top_uni_count = top_uni.value_counts().reset_index()
    top_uni_count.columns = ["University Name", "Number of Programs"]
    fig2 = px.bar(top_uni_count.head(5), x="University Name", y="Number of Programs", text="Number of Programs")
    st.plotly_chart(fig2, use_container_width=True)

    # Bar chart: Number of programs by fee range
    st.subheader("📊 Number of Programs by Fee Range")
    bins = [0, 10000, 12000, 15000, 20000, 30000, 100000]
    labels = ["<10k", "10k-12k", "12k-15k", "15k-20k", "20k-30k", ">30k"]
    df["Fee Range"] = pd.cut(df["ค่าใช้จ่ายต่อภาคการศึกษา"], bins=bins, labels=labels)
    fee_dist = df["Fee Range"].value_counts().sort_index().reset_index()
    fee_dist.columns = ["Fee Range", "Number of Programs"]
    fig3 = px.bar(fee_dist, x="Fee Range", y="Number of Programs", text="Number of Programs")
    st.plotly_chart(fig3, use_container_width=True)

    # Info: Number of universities without fee data
    num_missing = df_no_fee["ชื่อมหาวิทยาลัย"].nunique()
    st.info(f"ℹ️ Found {num_missing} universities without fee data in the system.")


# -------------------------------
# Tab 2: University & Campus Selection
# -------------------------------
with tab2:
    st.subheader("🏫 Select University and Campus to View Programs")

    # Prepare data for display: merge numeric and non-numeric fee data
    df_num = df.copy()
    df_num["Display Fee"] = df_num["ค่าใช้จ่ายต่อภาคการศึกษา"].map(lambda x: f"{x:,.0f} Bath")

    df_text = df_no_fee.copy()
    df_text["Display Fee"] = df_text["ค่าใช้จ่าย"]

    # Ensure both DataFrames have the same columns
    for col in df.columns:
        if col not in df_text.columns:
            df_text[col] = None
    for col in df_text.columns:
        if col not in df_num.columns:
            df_num[col] = None

    # Combine both DataFrames
    df_all = pd.concat([df_num, df_text], ignore_index=True)

    # Dropdown for university selection
    uni_list = sorted(df_all["ชื่อมหาวิทยาลัย"].dropna().unique())
    selected_uni = st.selectbox("Select University", uni_list)

    # Dropdown for campus selection
    campus_list = sorted(df_all[df_all["ชื่อมหาวิทยาลัย"] == selected_uni]["วิทยาเขต"].dropna().unique())
    selected_campus = st.selectbox("Select Campus", campus_list)

    # Filter data by selected university and campus
    df_filtered = df_all[(df_all["ชื่อมหาวิทยาลัย"] == selected_uni) & (df_all["วิทยาเขต"] == selected_campus)]

    if not df_filtered.empty:
        st.markdown(f"### All Programs in {selected_uni} ({selected_campus})")

        # Show table of programs and fees
        show_df = df_filtered[["ชื่อหลักสูตร", "Display Fee"]].sort_values("ชื่อหลักสูตร")
        st.dataframe(show_df, use_container_width=True)

        # Filter for numeric fee data for chart
        df_numeric_only = df_filtered[pd.to_numeric(df_filtered["ค่าใช้จ่ายต่อภาคการศึกษา"], errors='coerce').notnull()]

        if not df_numeric_only.empty:
            # Bar chart: program fees
            fig = px.bar(
                df_numeric_only.sort_values("ค่าใช้จ่ายต่อภาคการศึกษา"),
                x="ชื่อหลักสูตร",
                y="ค่าใช้จ่ายต่อภาคการศึกษา",
                text="Display Fee",
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

            # Show min/max fee metrics
            min_fee = df_numeric_only["ค่าใช้จ่ายต่อภาคการศึกษา"].min()
            max_fee = df_numeric_only["ค่าใช้จ่ายต่อภาคการศึกษา"].max()
            col1, col2 = st.columns(2)
            col1.metric("Lowest Fee", f"{min_fee:,.0f} Bath")
            col2.metric("Highest Fee", f"{max_fee:,.0f} Bath")
        else:
            st.info("No programs with numeric fee data for charting.")
    else:
        st.warning("No data found for the selected university or campus.")

# -------------------------------
# Tab 3: Programs Without Fee Data
# -------------------------------
with tab3:
    st.subheader("🔍 Programs Without Fee Data")

    # Helper function to render link or message
    def render_link(text):
        if isinstance(text, str) and text.startswith("http"):
            return f"{text}"
        return "No fee data found"

    # Add detail column with link or message
    df_no_fee["Details"] = df_no_fee["ค่าใช้จ่าย"].apply(render_link)

    # Dropdown for university filter
    selected_uni = st.selectbox("Select University", ["All"] + sorted(df_no_fee["ชื่อมหาวิทยาลัย"].unique()))

    # Filter DataFrame by selected university
    filtered_df = df_no_fee.copy()
    if selected_uni != "All":
        filtered_df = filtered_df[filtered_df["ชื่อมหาวิทยาลัย"] == selected_uni]

    # Columns to show in the table
    show_cols = ["ชื่อมหาวิทยาลัย"]
    if "วิทยาเขต" in filtered_df.columns:
        show_cols.append("วิทยาเขต")
    show_cols += ["ชื่อหลักสูตร", "Details"]

    st.dataframe(filtered_df[show_cols], use_container_width=True)