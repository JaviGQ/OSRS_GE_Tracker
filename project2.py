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

st.title("OSRS Grand Exchange Monitor")
st.subheader("Visualization Tool for OSRS's Grand Exchange Economy")

def api_url(letter_, page_):        #Used to grab the initial API that returns the item's core info, including image and in-game ID
    return f"https://secure.runescape.com/m=itemdb_oldschool/api/catalogue/items.json?category=1&alpha={letter_}&page={page_}"      #API structure provided in the documentation

def id_url(id_):                    #Uses the ID from the above function to then pull from a different API that has the economic data
    return f"https://services.runescape.com/m=itemdb_oldschool/api/graph/{id_}.json"

linePlot, maps, tables = st.tabs([
    "Line Chart",
    "Maps",
    "Tables"
])

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
    st.session_state.osrs_item = osrs_item
    st.rerun()

user_input = st.sidebar.text_input("Enter item name")           #User can input an item name through the sidebar

if user_input and not st.session_state.osrs_item:
    osrs_item = user_input
    osrs_url = api_url(osrs_item.lower(), page_=1)       #API only recognizes lower case input so all user input is cast to lowercase
    response = requests.get(osrs_url).json()
    #id_ = response["items"][0]["id"]
    st.session_state.osrs_item = ""

elif st.session_state.osrs_item:
    osrs_item = st.session_state.osrs_item
    osrs_url = api_url(osrs_item.lower(), page_=1)
    response = requests.get(osrs_url).json()

else:
    st.sidebar.info(
         "Search for any item that can be found in the Grand Exchange. For example, search \"rune scimitar\"."

    )  # Not everyone has played OSRS, so this provides an example so users can at least see what the application can do

    osrs_url = api_url("bucket", page_=1)
    response = requests.get(osrs_url).json()


if response["items"]:             #If the input triggers a hit in the API request, produces the dataframe
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

    large_icon = next(item for item in response["items"] if item["name"] == item_name)["icon_large"]
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

        col1, col2 = st.columns([2, 5])
        with col1:
            color = st.color_picker("Choose a color", "#FFD700")
            parameter = st.radio("Choose a parameter",
                                     options=["Daily", "Average"])

        with col2:
            fig2 = px.line(
                df,
                x=df.index,
                y=parameter.lower(),
                title=f"{parameter} Price of {item_name}"
            )
            fig2.update_traces(line_color=color)
            fig2.update_layout(
                xaxis=dict(
                    title=dict(
                        text="Days"
                    )
                ),
            yaxis = dict(
                title=dict(
                    text="Price"
                    )
                )
            )
            st.plotly_chart(fig2)

    with tables:
        st.subheader("Raw Data")
        st.dataframe(
            df,
            column_order=("daily","average"),
            column_config={
                "daily": st.column_config.NumberColumn("Daily"),
                "average": st.column_config.NumberColumn("Average"),
            }
        )
        st.divider()
        st.subheader("Summary Statistics")
        st.write(df.describe())