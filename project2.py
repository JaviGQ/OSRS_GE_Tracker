import random
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
from streamlit import color_picker

st.set_page_config(page_title="Dashboard",
                   layout="wide",
                   page_icon=":bar_chart:")

st.title("Old School RuneScape Grand Exchange Monitor")
st.subheader("Visualization Tool for Items in the Grand Exchange Economy")

def api_url(letter_, page_):        #Used to grab the initial API that returns the item's core info, including image and in-game ID
    return f"https://secure.runescape.com/m=itemdb_oldschool/api/catalogue/items.json?category=1&alpha={letter_}&page={page_}"      #API structure provided in the documentation

def id_url(id_):                    #Uses the ID from the above function to then pull from a different API that has the economic data
    return f"https://services.runescape.com/m=itemdb_oldschool/api/graph/{id_}.json"

osrs_item = ""      #Initial declaration of item name, ID variables, and valid flag
id_ = 0
valid = False

if "osrs_item" not in st.session_state:     #In order to ensure the random item function works, we initialize a session state based on the name of the item
    st.session_state.osrs_item = ""

select_random = st.button("Select random item")         #Allows a user to have a random item sent through the API to use the app

if select_random:
    random_letter = random.choice("abcdefghijklmnopqrstuvwxyz")     #Selects a random letter and sends it through the API to generate an item
    osrs_url = api_url(random_letter, page_=1)
    response = requests.get(osrs_url).json()
    osrs_item = response["items"][0]["name"]
    st.session_state.osrs_item = osrs_item                          #Sets the session state's item to the random item
    st.session_state.user_input = ""                                #Ensures any user input is deleted to ensure no issues with data visualization
    st.rerun()

linePlot, maps, scatter, tables = st.tabs([
    "Line Chart",
    "3D Map",
    "Scatter Plot",
    "Tables"
])

user_input = st.sidebar.text_input("Enter item name", key="user_input")           #User can input an item name through the sidebar

if user_input:
    osrs_item = user_input
    osrs_url = api_url(osrs_item.lower(), page_=1)       #API only recognizes lower case input so all user input is cast to lowercase
    response = requests.get(osrs_url).json()
    #id_ = response["items"][0]["id"]
    st.session_state.osrs_item = ""

elif st.session_state.osrs_item:                         #If item session state exists, then the random button was selected
    osrs_item = st.session_state.osrs_item
    osrs_url = api_url(osrs_item.lower(), page_=1)
    response = requests.get(osrs_url).json()

else:
    st.sidebar.info(                                    #Default info bubble
         "Search for any item that can be found in the Grand Exchange. For example, search \"rune scimitar\"."

    )  # Not everyone has played OSRS, so this provides an example so users can at least see what the application can do

    osrs_url = api_url("bucket", page_=1)
    response = requests.get(osrs_url).json()


if response["items"]:                                          #If the input triggers a hit in the API request, produces the dataframe
    item_name = response["items"][0]["name"]

    item_df = pd.DataFrame(response["items"])
    id_ = response["items"][0]["id"]
    valid = True

    if len(response["items"]) > 1 and osrs_item:          #If multiple items return as a match for the input provides a list of all the items
        st.sidebar.subheader(f"Multiple items returned for \"{item_name}\". If incorrect item is shown, please enter full name of item.")
        st.sidebar.dataframe(                              #Displays all the matching items to allow the user to visualize what may be the one they were searching for
            item_df,
            hide_index=True,
            column_order=("icon", "name"),
            column_config={
                "icon": st.column_config.ImageColumn("Icon", width="small"),
                "name": st.column_config.Column("Name")
            }
        )

        item_name = st.sidebar.selectbox(               #Generates a dropdown to select the correct item
            "Choose the correct item:",
            options=[
                item["name"] for item in response["items"]
            ]
        )

        id_ = next(item for item in response["items"] if item["name"] == item_name)["id"]       #Grabs the ID of the item in the dropdown if the user selects one to populate the updated data

    st.sidebar.success(f"Now displaying economic data for \"{item_name}\"")

    large_icon = next(item for item in response["items"] if item["name"] == item_name)["icon_large"]        #For the chosen item, pulls the image from the API and shows it to the user
    st.sidebar.image(large_icon, use_container_width=True, caption=item_name)

    id_url = id_url(id_)
    id_response = requests.get(id_url).json()
    df = pd.DataFrame(id_response)
    df.reset_index(inplace=True, drop=True)

else:                           #If the item search returns an empty list catches the error
    st.sidebar.error(f"No item found named \"{osrs_item}\". Please try again.")
    valid = False               #Valid flag set to False in order ensure no data is attempted to be populated

if valid:
    with linePlot:
        st.subheader("Line Chart for Price Change Over Previous 180 days")
        st.subheader(f"Current price for {item_name}: {df['daily'].iloc[-1]:,} gold")

        col1, col2 = st.columns([2, 5])

        with col1:
            parameter = st.radio("Choose a parameter",
                                 options=["Daily", "Average", "Both"],
                                 key=f"parameter_{item_name}")  #Adds the item name to the state in order to refresh the radio when a new item is chosen
            if parameter != "Both":                             #Allows the user to choose the color for one or both of the lines, based on their chosen option
                color = st.color_picker(f"Choose a color for {parameter}", "#1D5CBD", key=f"color_{item_name}")
            else:
                color = st.color_picker(f"Choose a color for Daily", "#1D5CBD", key=f"color_daily_{item_name}")
                color2 = st.color_picker("Choose a color for Average", "#F8F8F8", key=f"color_avg_{item_name}")

        with col2:
            if parameter == "Both":                 #Graph with two lines drawn when user selects both in the radio
                parameter = ["daily", "average"]
                fig2 = px.line(
                    df,
                    x=df.index,
                    y=parameter,
                    title=f"Price of {item_name}"
                )
                fig2.update_traces(line_color=color, selector=dict(name="daily"))           #Update traces required for each line separately
                fig2.update_traces(line_color=color2, selector=dict(name="average"))
                fig2.update_layout(
                    xaxis=dict(title=dict(text="Days")),
                    yaxis=dict(title=dict(text="Price"))
                )
                st.plotly_chart(fig2)

            else:                                   #A single line graph is drawn when one of the individual parameters is chosen
                fig2 = px.line(
                    df,
                    x=df.index,
                    y=parameter.lower(),
                    title=f"{parameter} Price of {item_name}"
                )
                fig2.update_traces(line_color=color)
                fig2.update_layout(
                    xaxis=dict(title=dict(text="Days")),
                    yaxis=dict(title=dict(text="Price"))
                )
                st.plotly_chart(fig2)

    with maps:
        st.subheader(f"3D Mapping of Economic Data for {item_name}")
        col1, col2 = st.columns([0.1, .9], gap="small")
        with col1:
            reverse_3d = st.checkbox("Reverse 3D Map", key=f"reverse_{item_name}")      #As with the line graph radio, adding the item name to the key ensures it resets for each new item

        with col2:
            item_3d = px.scatter_3d(
                df,
                x="daily",
                y="average",
                z=df.index,
                color=df.index
            )
            item_3d.update_scenes(
                xaxis=dict(title=dict(text="Daily")),
                yaxis=dict(title=dict(text="Average")),
                zaxis=dict(title=dict(text="Days"))
            )

            if reverse_3d:
                item_3d.update_scenes(zaxis_autorange="reversed")

            st.plotly_chart(item_3d)

    with scatter:
        st.subheader(f"Scatter Chart for {item_name} Price")
        item_scatter = px.scatter(
            df,
            x="daily",
            y=df.index,
            title=f"Daily Scatter Chart for {item_name}",
            color="average"
        )

        st.plotly_chart(item_scatter    )

    with tables:                                              #Raw data of the tables shown
        st.subheader("Raw Data")
        st.dataframe(
            df,
            column_order=("daily","average"),
            column_config={
                "daily": st.column_config.NumberColumn("Daily"),        #Minor changes to the formatting for capitalization
                "average": st.column_config.NumberColumn("Average"),
            }
        )
        st.divider()
        st.subheader("Summary Statistics")
        st.write(df.describe())