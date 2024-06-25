import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
import plost
import pandas as pd
import os
import csv

st.set_page_config(page_title='Emissions', page_icon='🗞️', layout='centered')
st.logo('assets/logo.png')
st.markdown('''
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size:16px; font-weight: bold; text-align:center;
    }
</style>
''', unsafe_allow_html=True
)

############### INITILISATION #######
# initialise emissions list
if 'emission_list' not in st.session_state:
    st.session_state["emission_list"] = []

today = datetime.now().strftime("%Y-%m-%d")

# Define transport emissions dictionary
transport_emissions = {
    "Walk/Bicycle": 0,
    "MRT/LRT": {
        "0 mins": 0,
        "<30mins": 10,
        "30-45 mins": 15,
        "45-60 mins": 20,
        "1-2hrs": 40
    },
    "Bus": {
        "0 mins": 0,
        "<30mins": 33,
        "30-45 mins": 54,
        "45-60 mins": 71,
        "1-2hrs": 143
    },
    "Car": {
        "0 mins": 0,
        "<30mins": 146,
        "30-45 mins": 182,
        "45-60 mins": 291,
        "1-2hrs": 582
    }
}
diet_emissions = {
    "Beef": 24.4, "Eggs": 3.1, "Pork": 13.4, "Veg": 0.6, "Chicken": 3.5, "Duck": 4.2, "Fruits": 0.4,
    "Mutton": 16.5, "Rice": 2.4, "Wheat": 0.7, "Seafood": 5.5, "Dairy": 8
}
################# FUNCTION HELPERS ################
# calculating emissions
def calculate_emissions(transport_emissions, diet_emissions, transport_modes_times, diet_items, recycle_option):
    emissions = 0

    # calculating transport emissions
    for mode, time_spent in transport_modes_times.items():
        if mode == "Walk/Bicycle":
            emissions += transport_emissions[mode]
        else:
            emissions += transport_emissions[mode][time_spent]

    # calculating diet emissions
    for item in diet_items:
        emissions += diet_emissions[item]

    # calculating waste emissions
    if recycle_option == "No":
        emissions += 1

    return emissions

def write_to_csv(data):
    st.write(data)
    header = ["Date", "Total Emission", "Transport Emission", "Dietary Emission", "Recycling Emission"]
    file_path = 'overall_emissions.csv'
    
    file_exists = os.path.exists(file_path)
    with open(file_path, 'a+', newline='') as f:
        csv_writer = csv.writer(f)
        if not file_exists or os.stat(file_path).st_size == 0:  # Check if file is empty
            csv_writer.writerow(header)
        csv_writer.writerow([data['Date'], data['Total Emission'], data['Transport Emission'], data['Dietary Emission'], data['Recycling Emission']])

############ STREAMLIT UI ##############
# horizontal menu
selectedTab = option_menu(
    menu_title = None,
    options = ['Input Emissions', "Your Overall Emissions"],
    icons=["pen", "bar-chart"],
    orientation= "horizontal"
)

if selectedTab == "Input Emissions":
    st.caption('Answer the following questions to calculate your daily emissions.')
    with st.form("Daily Carbon Footprint Check-In"):
        tabList = ['Transportation 🚗', 'Diet 🍽️', 'Recycling ♻️', 'Results']
        tabs = st.tabs([s.center(15,"\u2001") for s in tabList])
        with tabs[0]:
            transport_modes_times = {}
            transport_modes = ["MRT/LRT", "Car", "Bus", "Walk/Bicycle"]
            time_spent_options = ["0 mins","<30mins", "30-45 mins", "45-60 mins", "1-2hrs"]
            for mode in transport_modes:
                time_spent = st.selectbox(f"{mode}:", time_spent_options, key=mode)
                transport_modes_times[mode] = time_spent
        with tabs[1]:
            st.write("Select your diet items:")
            col1, col2 = st.columns(2)
            with col1:
                diet_items = []
                if st.checkbox("Beef"):
                    diet_items.append("Beef")
                if st.checkbox("Eggs"):
                    diet_items.append("Eggs")
                if st.checkbox("Pork"):
                    diet_items.append("Pork")
                if st.checkbox("Veg"):
                    diet_items.append("Veg")
                if st.checkbox("Chicken"):
                    diet_items.append("Chicken")
                if st.checkbox("Duck"):
                    diet_items.append("Duck")
            with col2:
                if st.checkbox("Fruits"):
                    diet_items.append("Fruits")
                if st.checkbox("Mutton"):
                    diet_items.append("Mutton")
                if st.checkbox("Rice"):
                    diet_items.append("Rice")
                if st.checkbox("Wheat"):
                    diet_items.append("Wheat")
                if st.checkbox("Seafood"):
                    diet_items.append("Seafood")
                if st.checkbox("Dairy"):
                    diet_items.append("Dairy")
        
        with tabs[2]:
            recycle_option = st.radio("Do you recycle?", ["Yes", "No"])
        
        
        with tabs[3]:
            button = st.form_submit_button("See my total estimated emissions! 👣",type="primary")
        
            if button:
                today_emission = calculate_emissions(transport_emissions, diet_emissions, transport_modes_times, diet_items, recycle_option)
                
                st.info(f"Your Emissions: {round(today_emission, 2)} kg CO2")
                
                # Calculate emissions breakdown for donut chart
                transport_emission = float(sum(transport_emissions[mode][time_spent] for mode, time_spent in transport_modes_times.items() if mode != "Walk/Bicycle"))
                diet_emission = float(sum(diet_emissions[item] for item in diet_items))
                recycling_emission = 1 if recycle_option == "No" else 0
                # Write to CSV
                data_row = {
                    'Date': today,
                    'Total Emission': today_emission,
                    'Transport Emission': transport_emission,
                    'Dietary Emission': diet_emission,
                    'Recycling Emission': recycling_emission
                }
                write_to_csv(data_row)

                ## plot the donut chart here
                today_emission_data = {
                    'Aspect': ['Transport', 'Diet', 'Recycling'],
                    'Emission': [transport_emission, diet_emission, recycling_emission]
                }
                today_emission_df = pd.DataFrame(today_emission_data)
                plost.donut_chart(today_emission_df, theta='Emission', color='Aspect', title='Emissions Breakdown', legend='top')

                
            

if selectedTab == "Your Overall Emissions":

    overall_emissions_df = pd.read_csv('overall_emissions.csv')
    if len(overall_emissions_df)>0:
        with st.container(border=True):
            st.subheader('Emission changes compared to the day before')
            col1, col2, col3, col4 = st.columns([1,1,1,1])
            
            with col1:
                current_total = overall_emissions_df['Total Emission'].iloc[-1]
                # ways to display the metric
                if len(overall_emissions_df) == 1:
                    st.metric(label='Total Emissions', value=current_total)
                elif len(overall_emissions_df) > 1:
                    previous_total = overall_emissions_df['Total Emission'].iloc[-2]
                    st.metric(label='Total Emissions', value=current_total, delta=current_total-previous_total)

            with col2:
                current_transport = overall_emissions_df['Transport Emission'].iloc[-1]
                # ways to display the metric
                if len(overall_emissions_df) == 1:
                    st.metric(label='Transport Emissions', value=current_total)
                elif len(overall_emissions_df) > 1:
                    previous_transport = overall_emissions_df['Transport Emission'].iloc[-2]
                    st.metric(label='Transport Emissions', value=current_transport, delta=current_transport-previous_transport)
            
            with col3:
                current_dietary = overall_emissions_df['Dietary Emission'].iloc[-1]
                # ways to display the metric
                if len(overall_emissions_df) == 1:
                    st.metric(label='Dietary Emission', value=current_dietary)
                elif len(overall_emissions_df) > 1:
                    previous_dietary = overall_emissions_df['Dietary Emission'].iloc[-2]
                    st.metric(label='Dietary Emission', value=current_dietary, delta=current_dietary-previous_dietary)
            
            with col4:
                current_recycle = overall_emissions_df['Recycling Emission'].iloc[-1]
                # ways to display the metric
                if len(overall_emissions_df) == 1:
                    st.metric(label='Transport Emissions', value=current_recycle)
                elif len(overall_emissions_df) > 1:
                    previous_recycle = overall_emissions_df['Transport Emission'].iloc[-2]
                    st.metric(label='Transport Emissions', value=current_total, delta=current_recycle-previous_recycle)
            
            st.divider()
            st.subheader('Emissions Over Time')
            plost.line_chart(overall_emissions_df, 
                            x='Date', y=('Transport Emission', 'Dietary Emission', 'Recycling Emission'), 
                            legend='top', height=400)
    else:
        st.warning('No Data Present!')
