import streamlit as st
from st_pages import Page, show_pages

st.set_page_config(page_title='Ecospeaks', page_icon='🌿', layout='centered')
st.logo('assets/logo.png')

show_pages(
    [
        Page("app.py", "Home", "🏠"),
        Page("pages/news_digest.py", "Enviro-News Digest", ":newspaper:"),
        Page("pages/emission_calculator.py", "Calculate Emissions", ":footprints:"),
    ]
)
st.columns([2,3,1])[1].title('EcoSpeaks.ai')
aboutText = "EcoSpeak is an Azure OpenAI-powered web application to educate individuals on sustainability issues and guide them to reach their personalized sustainable goals."
st.columns([0.5,3,0.5])[1].success(aboutText, icon="🌿")


# Creating an empty row with three columns to center-align the tabs
_, center_col, _ = st.columns([0.2, 3, 0.3])

tabList = ["Navigate App Features", "YouTube Demo"]
with center_col:
    # Creating the tabs inside the center column
    tabs= st.tabs([s.center(28,"\u2001") for s in tabList])

    # Tab 1: App Features
    with tabs[0]:
        left_col, middle, right_col= st.columns([3, 0.5, 3])
        
        with left_col:
            with st.container():
                st.page_link(label="News Digest 🗞️", page="pages/news_digest.py", use_container_width=True)
                st.info(icon='ℹ️', body="Summarises your latest environmental news and prepares quizzes for you!")
        
        with right_col:
            with st.container():
                st.page_link(label="Calculate footprint 👣", page="pages/emission_calculator.py", use_container_width=True)
                st.info(icon='ℹ️', body="Calculate your total emissions for the day.")

    # Tab 2: YouTube Demo
    with tabs[1]:
        VIDEO_URL = "https://youtu.be/v0YE9YDY5ts"
        st.video(data=VIDEO_URL)
        
