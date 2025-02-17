import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit app layout
st.title('Agent Productivity Tracker')

# File upload widget
file = st.file_uploader("Upload your CSV file", type="csv")

if file is not None:
    # Read the CSV file
    my_data = pd.read_csv(file, encoding='ISO-8859-1')

    # Convert 'Date' column to datetime and keep only the date (no time)
    my_data['Date'] = pd.to_datetime(my_data['Date'], format='%d/%m/%Y').dt.date

    # Input fields for Agent name and date selection
    agent_name = st.selectbox('Select Agent Name', my_data['Agent name'].unique())

    # Calendar for date selection
    st.subheader("Select Dates for Productivity Analysis")
    selected_dates = st.multiselect(
        'Choose specific dates', 
        options=my_data['Date'].unique(), 
        default=my_data['Date'].unique()[:3]  # Default to first 3 dates
    )

    # Filter the data based on inputs
    filtered_data = my_data[(my_data['Agent name'] == agent_name) & 
                            (my_data['Date'].isin(selected_dates))]

    # Calculate 'Performance' column
    filtered_data['Target Achieved'] = filtered_data['Processed Lots'] >= filtered_data['Target Lots']

    # Display filtered data
    if filtered_data.empty:
        st.write("No data available for the selected agent and dates.")
    else:
        st.write(filtered_data[['Date', 'Queue', 'Processed Lots', 'Reasons', 'Target Achieved']])

        # Check if target was achieved for the selected dates
        if filtered_data['Target Achieved'].all():
            st.success('Target Achieved for all selected dates!')
        else:
            st.warning('Target Not Achieved for some dates')

        # 📊 Line Chart: Processed Lots Over Time (Enhanced Visualization)
        st.subheader("Processed Lots Over Time")
        fig_line = px.line(filtered_data, x='Date', y='Processed Lots', title='Processed Lots Trend')

        # Expand y-axis range for better visibility of small changes
        y_min = filtered_data['Processed Lots'].min() * 0.95  # 5% below min value
        y_max = filtered_data['Processed Lots'].max() * 1.05  # 5% above max value

        fig_line.update_yaxes(range=[y_min, y_max])  # Set custom y-axis range
        st.plotly_chart(fig_line)

        # 📊 Bar Chart: Processed vs. Target Lots
        st.subheader("Processed vs. Target Lots")
        fig_bar = px.bar(filtered_data, x='Date', y=['Processed Lots', 'Target Lots'], 
                         title='Processed vs. Target Lots', barmode='group')
        fig_bar.update_yaxes(range=[y_min, y_max])  # Ensure same scaling for consistency
        st.plotly_chart(fig_bar)

        # 📊 Pie Chart: Target Achievement Distribution
        st.subheader("Target Achievement Distribution")
        achievement_counts = filtered_data['Target Achieved'].value_counts().reset_index()
        achievement_counts.columns = ['Target Achieved', 'Count']
        fig_pie = px.pie(achievement_counts, names='Target Achieved', values='Count', 
                         title='Target Achievement Ratio', color='Target Achieved')
        st.plotly_chart(fig_pie)
