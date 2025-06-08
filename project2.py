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

def api_url(letter_, page_):
    return f"https://secure.runescape.com/m=itemdb_oldschool/api/catalogue/items.json?category=1&alpha={letter_}&page={page_}"      #API structure provided in the documentation

def id_url(id_):
    return f"https://services.runescape.com/m=itemdb_oldschool/api/graph/{id_}.json"

linePlot, maps, tables, roulette = st.tabs([
    "Line Chart",
    "Maps",
    "Tables",
    "Roulette"
])
osrs_item = ""
id_ = 0
if "osrs_item" not in st.session_state:
    st.session_state.osrs_item = ""

with roulette:
    select_random = st.button("Select random item")

    if select_random:
        random_letter = random.choice("abcdefghijklmnopqrstuvwxyz")
        osrs_url = api_url(random_letter, page_=1)
        response = requests.get(osrs_url).json()
        osrs_item = response["items"][0]["name"]
        st.session_state.osrs_item = osrs_item
        st.rerun()

user_input = st.sidebar.text_input("Enter item name")
valid = False

if user_input:
    osrs_item = user_input
    osrs_url = api_url(osrs_item.lower(), page_=1)       #API only recognizes lower case input
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


if response["items"]:           #If the item is found in the API request, produces the dataframe
    item_name = response["items"][0]["name"]

    item_df = pd.DataFrame(response["items"])
    id_ = response["items"][0]["id"]
    valid = True

    if len(response["items"]) > 1 and osrs_item:          #If multiple items return as a match for the input provides a list of all the items
        st.sidebar.subheader(f"Multiple items returned for \"{item_name}\". If incorrect item is shown, please enter full name of item.")
        st.sidebar.dataframe(
            item_df,
            hide_index=True,
            column_order=("icon", "name"),
            column_config={
                "icon": st.column_config.ImageColumn("Icon", width="small"),
                "name": st.column_config.Column("Name")
            }
        )

        item_name = st.sidebar.selectbox(
            "Choose the correct item:",
            options=[
                item["name"] for item in response["items"]
            ]
        )

        id_ = next(item for item in response["items"] if item["name"] == item_name)["id"]

    st.sidebar.success(f"Now displaying economic data for \"{item_name}\"")

    large_icon = next(item for item in response["items"] if item["name"] == item_name)["icon_large"]
    st.sidebar.image(large_icon, use_container_width=True, caption=item_name)

    id_url = id_url(id_)
    id_response = requests.get(id_url).json()
    #st.json(id_response)
    df = pd.DataFrame(id_response)
    df.reset_index(inplace=True, drop=True)

else:                           #If the item search returns an empty list catches the error
    st.sidebar.error(f"No item found named \"{osrs_item}\". Please try again.")
    valid = False

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