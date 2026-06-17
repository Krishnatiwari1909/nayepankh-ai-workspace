import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Impact Analytics | Dashboard", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .metric-card {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 1.2rem;
        border-radius: 0.6rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; }
    .metric-label { font-size: 0.9rem; opacity: 0.7; }
    [data-testid="stSidebarNav"] { padding-bottom: 0px; }
    div[data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }
    </style>
""", unsafe_allow_html=True)

# Connect and ingest
conn = sqlite3.connect('impact.db', check_same_thread=False)
df = pd.read_sql_query("SELECT * FROM activities", conn)

# --- DASHBOARD SIDEBAR (Interactive Filters) ---
with st.sidebar:
    st.markdown("### 🎛️ **Dashboard Controls**")
    st.caption("Filter the impact data dynamically.")
   
    
    if not df.empty:
        # Create a dropdown to filter by activity type
        activity_list = ["All Activities"] + list(df['activity_type'].unique())
        selected_filter = st.selectbox("Filter by Sector Focus", activity_list)
        
        # Apply the filter to the dataframe
        if selected_filter != "All Activities":
            df = df[df['activity_type'] == selected_filter]
            
        st.write("---")
        st.success(f"Currently viewing data for: **{selected_filter}**")
    else:
        st.warning("No data available to filter yet.")

# --- MAIN DASHBOARD AREA ---
st.title("📊 Operational Impact Analytics")
st.markdown("Real-time data synchronization across foundation operations and outreach campaigns.")


if df.empty:
    st.info("📊 No activities match this filter. Go to the Home page to log more activities!")
else:
    # Top Level Metrics (Now these update dynamically based on the filter!)
    total_impact = df['people_impacted'].sum()
    total_activities = len(df)
    unique_volunteers = df['volunteer_name'].nunique()
    
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>✨ {total_impact:,}</div><div class='metric-label'>Cumulative People Impacted</div></div>", unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>📋 {total_activities}</div><div class='metric-label'>Verified Actions Logged</div></div>", unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>🧑‍🤝‍🧑 {unique_volunteers}</div><div class='metric-label'>Active Volunteers</div></div>", unsafe_allow_html=True)
        
    st.write("##")
    st.write("---")
    
    # Visual Analytics Breakdown
    col_chart1, col_chart2 = st.columns([4, 6])
    with col_chart1:
        st.markdown("#### 📈 Distribution")
        impact_by_type = df.groupby('activity_type')['people_impacted'].sum()
        st.bar_chart(impact_by_type, use_container_width=True)
        
    with col_chart2:
        st.markdown("#### 🔍 Master Activity Ledger")
        st.dataframe(df.sort_values(by="date", ascending=False), use_container_width=True, hide_index=True)

    # Export functionality
    st.write("---")
    col_footer_left, col_footer_right = st.columns([8, 2])
    with col_footer_right:
        st.download_button(
            label="📥 Export Current View as CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='nayepankh_audited_impact_report.csv',
            mime='text/csv',
            use_container_width=True
        )
