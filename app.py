import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(page_title="Agent Productivity Tracker", layout="wide")
st.title("Agent Productivity Tracker")

# File uploader
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    # Convert 'Date' to datetime.date
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y', errors='coerce').dt.date
    if df['Date'].isnull().any():
        st.warning("Some dates could not be parsed and were ignored.")

    # Agent selection
    agents = df['Agent Name'].dropna().unique()
    if len(agents) == 0:
        st.error("No agents found in the dataset.")
        st.stop()

    agent_name = st.selectbox("Select an Agent", sorted(agents))

    # Calendar for date range selection
    st.subheader("Select Date Range for Productivity Analysis")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input('From Date', min_value=my_data['Date'].min(), max_value=my_data['Date'].max())
    with col2:
        end_date = st.date_input('To Date', min_value=start_date, max_value=my_data['Date'].max())

    # Filter data
    filtered_data = df[
        (df['Agent Name'] == agent_name) &
        (df['Date'] >= start_date) &
        (df['Date'] <= end_date)
    ]

    if filtered_data.empty:
        st.warning("No data available for the selected agent and date range.")
        st.stop()

    # Calculate 'Target Achieved'
    filtered_data['Target Achieved'] = filtered_data['Processed Lots'] >= filtered_data['Target Lots']

    # Show filtered table
    st.subheader("Filtered Data")
    st.dataframe(filtered_data[['Date', 'Queue', 'Processed Lots','Target Lots', 'Reasons', 'Target Achieved']])

    # Summary statistics
    total_processed = filtered_data['Processed Lots'].sum()
    average_processed = filtered_data['Processed Lots'].mean()
    days_achieved = filtered_data['Target Achieved'].sum()
    total_days = len(filtered_data)

    st.subheader(f"Summary for {agent_name} from {start_date} to {end_date}")
    st.markdown(f"""
    - **Total Processed Lots:** {total_processed}
    - **Average Processed Lots per Day:** {average_processed:.2f}
    - **Days Target Achieved:** {days_achieved} out of {total_days}
    """)

    if filtered_data['Target Achieved'].all():
        st.success("Target Achieved for the entire range!")
    else:
        st.info("Target NOT Achieved on some dates.")

    # Plotting
    y_min = filtered_data['Processed Lots'].min() * 0.95
    y_max = filtered_data['Processed Lots'].max() * 1.05

    col1, col2 = st.columns(2)

    with col1:
        fig_line = px.line(filtered_data, x='Date', y='Processed Lots', title='Processed Lots Trend')
        fig_line.update_yaxes(range=[y_min, y_max])
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        fig_bar = px.bar(filtered_data, x='Date', y=['Processed Lots', 'Target Lots'],
                         title='Processed vs. Target Lots', barmode='group')
        fig_bar.update_yaxes(range=[y_min, y_max])
        st.plotly_chart(fig_bar, use_container_width=True)

    achievement_counts = filtered_data['Target Achieved'].value_counts().reset_index()
    achievement_counts.columns = ['Target Achieved', 'Count']
    fig_pie = px.pie(achievement_counts, names='Target Achieved', values='Count',
                     title='Target Achievement Ratio')
    st.plotly_chart(fig_pie, use_container_width=True)
