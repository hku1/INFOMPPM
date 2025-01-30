# Necessary imports for the application functionality
import streamlit as st  # Streamlit library for creating web apps
from random import random  # For generating random numbers
import json  # Library for working with JSON data
import datetime  # For handling dates and times

# Function to save user activities to a JSON file
def save_activities():
    with open('activities.json', 'w') as outfile:
        # Dumping the session state activities into the file with pretty printing
        json.dump(st.session_state['activities'], outfile, indent=4)

# Function to handle an activity such as selecting an episode or a season
def activity(id, activity):
    # Creating a data dictionary with activity details
    data = {
        'content_id': id,
        'activity': activity,
        'user_id': st.session_state['username'],
        'datetime': str(datetime.datetime.now())  # Capturing the current datetime
    }
    # Adding the activity to the session state
    st.session_state['activities'].append(data)
    # Saving the activities after adding the new activity
    save_activities()

# Function to set the selected episode in the session state
def select_episode(e):
    st.session_state['episode'] = e
    # Logging the 'Select Episode' activity
    activity(e, 'Select Episode')

# Function to set the selected season in the session state
def select_season(s):
    st.session_state['season'] = s
    # Logging the 'Select Season' activity
    activity(int(s), 'Select Season')

# Function to display an item (episode or season) in a given column
def tile_item(column, item):
    with column:
        # Displaying the item image, title, and a short summary
        st.image(item['image'], use_column_width='always')
        st.markdown(item['title'])
        st.caption(item['summary'][:50] + (item['summary'][50:] and '..'))  # Shortening the summary
        st.caption('Season ' + str(item['season']) + ' | episode ' + str(item['episode']) + ' | Rating ' + str(item['rating']) + ' | ' + str(item['votes']) + ' votes')
        # Button to select the episode, with a unique key to prevent conflicts
        st.button('▶', key=random(), on_click=select_episode, args=(item['id'], ))

# Function to display tiles for multiple items (episodes or seasons) from a DataFrame
def tiles(df):
    # Checking the number of items to display
    nbr_items = df.shape[0]
    cols = 6  # Setting the number of columns for display

    if nbr_items != 0:    
        # Creating a fixed number of columns
        columns = st.columns(cols)

        # Converting DataFrame rows to a list of dictionaries
        items = df.to_dict(orient='records')

        # Applying the tile_item function to each column-item tuple using zip
        any(tile_item(x[0], x[1]) for x in zip(columns, items))
