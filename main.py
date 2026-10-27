import streamlit as st
import pandas as pd
import plotly.express as px

# Page Setup
st.set_page_config(
    page_title="District Amenities Heatmap",
    layout="wide"
)

st.header("Objective 2: District-Level Basic Amenities Infrastructure Analysis 🚰", divider="gray")

# Load Cleaned Dataset
try:
    df_amenities = pd.read_excel('hh_access_amenities_cleaned.xlsx')
    st.success("Data loaded successfully!")
    df_amenities['date'] = pd.to_datetime(df_amenities['date'])
    df_amenities['year'] = df_amenities['date'].dt.year

    # State Selector
    selected_state = st.selectbox("Select State:", sorted(df_amenities['state'].unique()), index=0)
    
    # Filter out 'All Districts' to focus on individual districts
    state_amen = df_amenities[(df_amenities['state'] == selected_state) & (df_amenities['district'] != 'All Districts')]

    # Calculate Values for Summary Boxes
    latest_amen = state_amen[state_amen['year'] == 2024]
    avg_water = latest_amen['piped_water'].mean()
    avg_sanitation = latest_amen['sanitation'].mean()
    
    # District with lowest piped water access rate
    min_water_row = latest_amen.loc[latest_amen['piped_water'].idxmin()] if not latest_amen.empty else None
    min_water_dist = min_water_row['district'] if min_water_row is not None else "N/A"
    min_water_val = min_water_row['piped_water'] if min_water_row is not None else 0.0

    # Summary Boxes (4 Metrics)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Water Access (2024)", f"{avg_water:.1f}%", help="State Average Piped Water Access Rate in 2024", border=True)
    col2.metric("Avg Sanitation Access (2024)", f"{avg_sanitation:.1f}%", help="State Average Sanitation Access Rate in 2024", border=True)
    col3.metric("Lowest Water Access", f"{min_water_dist} ({min_water_val:.1f}%)", help="District with lowest piped water access in 2024", border=True)
    col4.metric("Total Districts", f"{len(latest_amen['district'].unique())}", help="Number of distinct districts analyzed", border=True)

    # Raw Data Preview
    st.subheader("Raw Data Preview")
    st.dataframe(state_amen[['year', 'district', 'piped_water', 'sanitation', 'electricity']])

    # Multi-District Heatmap
    st.subheader(f"Multi-District Infrastructure Access Heatmap ({selected_state})")
    
    amenity_choice = st.radio("Select Utility Metric:", ["Piped Water Access (%)", "Sanitation Access (%)"], horizontal=True)
    metric_col = 'piped_water' if amenity_choice == "Piped Water Access (%)" else 'sanitation'

    # Pivot table for Heatmap Matrix (Districts vs Years)
    pivot_df = state_amen.pivot(index='district', columns='year', values=metric_col)

    fig2 = px.imshow(
        pivot_df,
        labels=dict(x="Year", y="District", color="Access Rate (%)"),
        x=[str(y) for y in pivot_df.columns],
        y=pivot_df.index,
        color_continuous_scale="Blues" if metric_col == 'piped_water' else "Reds",
        zmin=80,
        zmax=100,
        text_auto=".1f",
        title=f"District-level {amenity_choice} matrix in {selected_state} (2019 - 2024)"
    )
    fig2.update_layout(height=max(400, len(pivot_df) * 35))

    st.plotly_chart(fig2, use_container_width=True)

    # Interpretation Section
    st.markdown("### 💬 Interpretation & Discussion")
    st.info(f"""
    * **Spatial Pattern:** The heatmap matrix illustrates access rates across districts in **{selected_state}**. Major urban centers exhibit near 100% saturation across all evaluation years.
    * **Disparity Identification:** Varied color intensities reveal specific rural or interior districts experiencing lower baseline access or slower infrastructure development over time.
    * **Policy Insight:** Heatmap visualizations allow local government planning units to immediately locate underdeveloped districts requiring priority funding for water pipeline and sanitation upgrades.
    """)

except Exception as e:
    st.error(f"Error loading or processing data: {e}")
