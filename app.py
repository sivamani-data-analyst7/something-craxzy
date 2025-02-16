import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit app layout
st.title('Agent Performance Tracker')

# File upload widget
file = st.file_uploader("Upload your CSV file", type="csv")

if file is not None:
    # Read the CSV file
    my_data = pd.read_csv(file, encoding='ISO-8859-1')

    # Convert 'Date' to datetime
    my_data['Date'] = pd.to_datetime(my_data['Date'], format='%d/%m/%Y')

    # Input fields for Agent name and date range
    agent_name = st.selectbox('Select Agent Name', my_data['Agent name'].unique())
    start_date = st.date_input('Start Date', min_value=my_data['Date'].min())
    end_date = st.date_input('End Date', min_value=start_date)

    # Filter the data based on inputs
    filtered_data = my_data[(my_data['Agent name'] == agent_name) & 
                            (my_data['Date'] >= pd.to_datetime(start_date))]

    # Only filter by 'end_date' if it's provided
    if end_date:
        filtered_data = filtered_data[filtered_data['Date'] <= pd.to_datetime(end_date)]

    # Calculate 'Performance' column
    filtered_data['Target Achieved'] = filtered_data['Processed Lots'] >= filtered_data['Target Lots']

    # Display filtered data
    if filtered_data.empty:
        st.write("No data available for the selected agent and date range.")
    else:
        st.write(filtered_data[['Date', 'Queue', 'Processed Lots', 'Reasons', 'Target Achieved']])

        # Check if target was achieved for the entire period
        if filtered_data['Target Achieved'].all():
            st.success('Target Achieved!')
        else:
            st.warning('Target Not Achieved')

        # 📊 Line Chart: Trend of processed lots over time
        st.subheader("Processed Lots Over Time")
        fig_line = px.line(filtered_data, x='Date', y='Processed Lots', title='Processed Lots Trend')
        st.plotly_chart(fig_line)

        # 📊 Bar Chart: Processed vs. Target Lots
        st.subheader("Processed vs. Target Lots")
        fig_bar = px.bar(filtered_data, x='Date', y=['Processed Lots', 'Target Lots'], 
                         title='Processed vs. Target Lots', barmode='group')
        st.plotly_chart(fig_bar)

        # 📊 Pie Chart: Target Achievement Distribution
        st.subheader("Target Achievement Distribution")
        achievement_counts = filtered_data['Target Achieved'].value_counts().reset_index()
        achievement_counts.columns = ['Target Achieved', 'Count']
        fig_pie = px.pie(achievement_counts, names='Target Achieved', values='Count', 
                         title='Target Achievement Ratio', color='Target Achieved')
        st.plotly_chart(fig_pie)
