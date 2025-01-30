# Importing necessary libraries
import streamlit as st  # Streamlit library for creating web apps
import streamlit_authenticator as stauth  # Authentication module for Streamlit apps
import pandas as pd  # Pandas library for data manipulation
import template as t  # Custom module for specific functions used in the app
import json  # Library for working with JSON data
from itertools import cycle  # To cycle through a sequence of elements
from random import random  # For generating random numbers

import yaml  # YAML parser and emitter for Python
from yaml.loader import SafeLoader  # Loader class for safe YAML loading

# Setting the layout of the Streamlit page to wide format
st.set_page_config(layout="wide")

# Loading the configuration from a YAML file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    
# Initializing the authenticator with the configuration data
authenticator = stauth.Authenticate(
    config['credentials'],  # User credentials
    config['cookie']['name'],  # Cookie name for session management
    config['cookie']['key'],  # Key for cookie encryption
    config['cookie']['expiry_days'],  # Cookie expiry in days
    config['preauthorized']  # Preauthorized users
)

# Logging out any existing session
authenticator.logout()       

# Handling authentication status
if st.session_state["authentication_status"]:
    # User is authenticated, display a welcome message
    st.write(f'Welcome *{st.session_state["name"]}*')
    
    # Loading episodes data from a JSON file into a Pandas DataFrame
    df = pd.read_json('episodes.json')

    # Loading activities data from a JSON file
    with open('activities.json') as json_file:
        users_activities = json.load(json_file)

    # Initializing session state variables if they don't exist
    if 'season' not in st.session_state:
        st.session_state['season'] = 1
    if 'episode' not in st.session_state:
        st.session_state['episode'] = 'tt0348034'
    if 'activities' not in st.session_state:
        st.session_state['activities'] = users_activities

    # Extracting unique seasons and sorting them
    seasons = pd.unique(df['season'].sort_values(ascending=True))

    # Filtering DataFrame for the selected season and episode
    df_season = df[df['season'] == st.session_state['season']]
    df_episode = df[df['id'] == st.session_state['episode']]
    df_episode = df_episode.iloc[0]  # Getting the first row of the filtered DataFrame

    # Creating two columns layout
    col1, col2 = st.columns(2)

    with col1:
        # Displaying the episode image
        st.image(df_episode['image'], use_column_width='always')

    with col2:
        # Displaying episode details
        st.title(df_episode['title'])
        st.caption(df_episode['airdate'])
        st.markdown(df_episode['summary'])
        st.caption('Season ' + str(df_episode['season']) + ' | episode ' + str(df_episode['episode']) + ' | Rating ' + str(df_episode['rating']) + ' | ' + str(df_episode['votes']) + ' votes')

    # Expander for collecting implicit and explicit feedback
    with st.expander('Implicit and Explicit feedback'):
        # Buttons for like and dislike with random keys to prevent conflicts
        st.button('👍', key=random(), on_click=t.activity, args=(df_episode['id'], 'Like'))
        st.button('👎', key=random(), on_click=t.activity, args=(df_episode['id'], 'Dislike'))

    # Expander for selecting seasons
    with st.expander("Seasons"):
        cols = cycle(st.columns(14))  # Creating a cycle of 14 columns
        for season in seasons:
            next(cols).button(str(season), key=season, on_click=t.select_season, args=(season,))

    # Expander for showing random episodes from the selected season
    with st.expander("Random episodes in this season"):
        t.tiles(df_season.sample(6))  # Displaying 6 random episodes using a custom template function

elif st.session_state["authentication_status"] is False:
    # Authentication failed, display error message
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    # No authentication attempt made yet, display warning and login form
    st.warning('Please enter your username and password')
    authenticator.login()  # Displaying the login form