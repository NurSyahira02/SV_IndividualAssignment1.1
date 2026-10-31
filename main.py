import streamlit as st
import pandas as pd
import plotly.express as px

# Page Setup
st.set_page_config(
    page_title="District Amenities Heatmap",
    layout="wide"
)

st.header("District-Level Basic Amenities Infrastructure Analysis 🚰", divider="gray")

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
    avg_electricity = latest_amen['electricity'].mean()
    total_districts = len(latest_amen['district'].unique())
    
    # District with lowest piped water access rate
    min_water_row = latest_amen.loc[latest_amen['piped_water'].idxmin()] if not latest_amen.empty else None
    min_water_dist = min_water_row['district'] if min_water_row is not None else "N/A"
    min_water_val = min_water_row['piped_water'] if min_water_row is not None else 0.0

    # Summary Boxes (4 Metrics)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Piped Water Access", f"{avg_water:.1f}%", help="Average district piped water access rate across the 2019–2024 evaluation period", border=True)
    col2.metric("Sanitation Access", f"{avg_sanitation:.1f}%", help="Average district sanitation access rate across the 2019–2024 evaluation period", border=True)
    col3.metric("Electricity Access", f"{avg_electricity:.1f}%", help="Average district electricity access rate across the 2019–2024 evaluation period", border=True)
    col4.metric("Total Districts", f"{total_districts}", help="Total number of administrative districts analyzed across 2019–2024", border=True)

    # Raw Data Preview
    st.subheader("Raw Data Preview")
    st.dataframe(state_amen[['year', 'district', 'piped_water', 'sanitation', 'electricity']])

    # Multi-District Heatmap
    st.subheader(f"Multi-District Infrastructure Access Heatmap ({selected_state})")
    
    # Updated Radio Selector with Electricity Access (%)
    amenity_choice = st.radio(
        "Select Utility Metric:", 
        ["Piped Water Access (%)", "Sanitation Access (%)", "Electricity Access (%)"], 
        horizontal=True
    )
    
    # Map selection to dataset column
    column_mapping = {
        "Piped Water Access (%)": "piped_water",
        "Sanitation Access (%)": "sanitation",
        "Electricity Access (%)": "electricity"
    }
    metric_col = column_mapping[amenity_choice]

    # Pivot table for Heatmap Matrix (Districts vs Years)
    pivot_df = state_amen.pivot(index='district', columns='year', values=metric_col)

    fig2 = px.imshow(
        pivot_df,
        labels=dict(x="Year", y="District", color="Access Rate (%)"),
        x=[str(y) for y in pivot_df.columns],
        y=pivot_df.index,
        color_continuous_scale="RdYlGn",
        zmin=95,
        zmax=100,
        text_auto=".1f",
        aspect="auto",  # <-- Stretches heatmap to full container width
        title=f"District-level {amenity_choice} matrix in {selected_state} (2019 - 2024)"
    )
    
    fig2.update_xaxes(type='category', tickangle=0)
    fig2.update_traces(textfont_size=14)  # <-- Larger font for cell values
    fig2.update_layout(
        height=max(450, len(pivot_df) * 40),
        margin=dict(l=40, r=40, t=60, b=40)
    )

    st.plotly_chart(fig2, use_container_width=True)

    # Interpretation Section
    st.markdown("### 💬 Interpretation & Discussion")
    st.info(f"""
    * **Spatial Pattern:** The heatmap matrix illustrates access rates across districts in **{selected_state}**. Major urban centers exhibit near 100% saturation across all evaluation years.
    * **Disparity Identification:** Varied color intensities reveal specific rural or interior districts experiencing lower baseline access or slower infrastructure development over time.
    * **Policy Insight:** Heatmap visualizations allow local government planning units to immediately locate underdeveloped districts requiring priority funding for water pipeline, sanitation, and electrical grid upgrades.
    """)

except Exception as e:
    st.error(f"Error loading or processing data: {e}")
