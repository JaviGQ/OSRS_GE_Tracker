**Introduction**

This app allows a user to obtain current and historical pricing data on any item currently available in the popular game known as Old School Runescape ("OSRS"). A user can enter the name of an item and the app will pull the necessary data from OSRS's API and produce visual representation of the pricing data. In order to even allow users who do not know, or are less familiar, with the game to still engage with the app, a random item button is included that will load up the information for random items in the game for the user.

Ordinarily, the pricing data for this game is available only in-game at the marketplace known as the Grand Exchange. However, even in-game there is no historical data available to the player, which leads to a newer player being unaware of the pricing of item has spiked, making it more expensive than usual, as opposed to being roughly around its standard average price. This tool allows anyone, especially those who are new to the game, to ensure they are getting the best deal on any items they may purchase using the in-game gold system.

**Usability Goals**

Below are usability goals intended for this app and how each was achieved.


_Effectiveness_: Using the OSRS API the data for the items loaded are accurate and consistent. The data reflected on each page reflects the different settings, options, and layouts a user may choose to employ.

_Efficiency_: A single button click to select a random item to ensure any user can quickly and easily use the app. Item search bar is a single line that immediately loads all information without additional prompting. Drop-down for multiple items allows the selected item to immediately load without additional user input.

_Learnability_: Each tab is consistent in spacing and placement of data visualization features. Options for the user are in the left column, data is displayed on the right. Random button persists across all tabs so a user can generate a new item at any time. 

_Feedback_: Info message provided at the start to assist a new user in how to use the app. Successful item loads result in a success bubble, while failure to load an item provides an error bubble.

_Error Prevention_: Multiple checks and flags are used to ensure data is not loaded before a valid item is received from the API. Requests to the API are limited in order to minimize timeouts for loading the item data.

_User Satisfaction_: Data is cleanly portrayed. Item icons are displayed to ensure user can compare the item shown to the item they intended to search.

_Consistency_: Entire app shares color scheme. Default colors on all charts match initially.

**Design Process**

The initial app was intended to all take place in the same window. However, displaying the item icons, as they are received and loaded from the API proved hard to properly place and size in the main window. The design change was then made to implement the sidebar for the search and item images. As the main focus of the app is the pricing data, not the image of the icon, the sidebar is collapsable and allows the user to search for their item and then close the sidebar to focus on the data as needed.

Initially the return of multiple items chart was produced in the center. Aesthetically the interface made the most sense in the sidebar as well, as keeping all the user's search information collapsable was determined to be the most effective means of ensuring the focus of the app was the data.

Finally, the random button, following the above logic, was initially placed in the sidebar. However during initial testing, having to re-open the collapsed sidebar to generate a new random item broke up the user experience. Once moved to the main page the users were able to maintain the sidebar closed and still play and explore with the app. The button was initially placed below all the graphs and charts in the tabs, but the location was sometimes buried or lost, especially in the tables tab. It was determined users would want to hit the button and see the data change quickly so it was placed above the tabs so users can hit the button to change the data easily. 

**API Integration**

The first struggle was with the OSRS API having two separate APIs that obtain different information. The first provides the name, in-game ID, and icons for the items, while the second is what provides the historical pricing data. The problem that arises is that the first uses the item name to search while the second requires the item ID. This was resolved by using the first to get the ID and then using the ID to then generate a second URL for the ID-focused API.

Additionally, there was an issue initially in which if the API could not find the item provided, the app would crash since there would be no data to load. Instead of resorting to a default data set, an error would just be caught and a bubble would inform the user of the error.

**Widgets**

The random button widget makes a call to the API for a random item by selecting a random letter and finding an item with that letter to load for the user.

The text-input box allows a user to provide the name, or the start, of any item. This is then passed through the initial API request to get the remaining information for the user.

If a search returns with multiple potential matches, a select-box is generated for the user to select the correct item.

The tabs each lead to the various visualizations of the data. Within the line graph section, the color selector allows the user to pick a color for the graph, while the radio selector allows the user to determine which lines or lines to display.

Within the 3D map the checkbox allows the user to reverse the 3D map.

**HCI Principles**

_Visibility_: The control are obvious and clear for the user. All widgets and buttons are clearly labeled and appropriately colored for visibility. 

_Feedback_: Error and success bubbles pop up immediately based on the success on the response from the API.

_Consistency_: Each tab echoes the same layout, with user options on the left and the data on the right. 

_Flexibility_: Multiple tabs allow for different visualizations of the data. Choosing an item can be random, provided by user input, or chosen from a dropdown.

_Error Prevention_: Invalid user inputs result in an error as the API fails to produce a response. Failure to find an item, even with a valid input, results in an error bubble.

**Conclusion and Future Improvements**

The app performs as expected and the data is accurately obtained and visualized. As with most other data analytics, further use and applications can be added. For example, a simple prediction algorithm can use the data from the last 60, 30, and 7 days to make a prediction of how the price may fluctuate, independent of any extraneous effects, such as game updates.

Additionally, the UI can be visually improved. The icons of the images are the only semblance relating this app to RuneScape. Providing additional images that can be preloaded can make the app more aesthetically pleasing.

Finally, some research while preparing the assignment found that Streamlit has an external library that can be used to make charts and tables clickable. We were unable to include the library, but using this would allow the user to click the correct item which would be a more intuitive way of proceeding through the app. 