#Libraries
import pandas as pd
import folium
import random
import streamlit as st
from streamlit_folium import st_folium

# Load the dataframe in FishMap.py
df_updated = pd.read_csv("df_updated.csv")

map_center = [44.6939, -69.3815]
m = folium.Map(location=map_center, zoom_start=7)

# Function to update the map based on selected species, date filters (Spring/Fall), and search
def update_map(selected_species, show_spring, show_fall, search_term, min_qty):
    # Initialize the map centered around Maine

    # m_test = folium.Map(location=map_center, zoom_start=6)

    # Group data by water body, town, and county
    grouped = df_updated.groupby(['WATER', 'TOWN', 'COUNTY'])

    # Filter the grouped data based on the search term
    filtered_groups = []
    for (water_name, town_name, county_name), group in grouped:
        if (search_term.lower() in water_name.lower() or
            search_term.lower() in town_name.lower() or
            search_term.lower() in county_name.lower()):
            filtered_groups.append((water_name, town_name, county_name, group))

    # Add markers to the map for each unique water body, town, and county combination
    for (water_name, town_name, county_name, group) in filtered_groups:
        species_list = []
        qty_list = []
        size_list = []
        date_list = []

        # Loop through each row in the group and collect the data
        for _, row in group.iterrows():
            species_list.append(row['SPECIES'])
            qty_list.append(row['QTY'])
            size_list.append(row['SIZE (inch)'])
            date_list.append(row['DATE'])

        # Filter data by species and date (Spring/Fall)
        filtered_rows = []
        for species, qty, size, date in zip(species_list, qty_list, size_list, date_list):
            month = pd.to_datetime(date).month  # Get the month from the date
            if (show_spring and month <= 6) or (show_fall and month >= 7):
                if species in selected_species and qty >= min_qty:  # Filter by min_qty
                    filtered_rows.append((species, qty, size, date))

        # Only display markers if there is data to show after filtering
        if filtered_rows:
            popup_text = f"""
            <b>Water Body:</b> {water_name}<br>
            <b>Town:</b> {town_name}<br>
            <b>County:</b> {county_name}<br>
            <b>Stocking Data:</b><br>
            <ul>
            """
            for species, qty, size, date in filtered_rows:
                popup_text += f"""
                <li><b>{species}</b> - {qty} fish, Size: {size} inches, Date: {date}</li>
                """
            popup_text += "</ul>"

            # Use the average coordinates of the water body/town combination
            avg_x = group['X_coord'].mean()
            avg_y = group['Y_coord'].mean()

            # Offset coordinates slightly if there are multiple towns associated with the same water body
            offset_x = random.uniform(-0.001, 0.001)  # Random offset for longitude
            offset_y = random.uniform(-0.001, 0.001)  # Random offset for latitude

            # Add a single marker for the water body/town combo with grouped popup data
            folium.Marker(
                location=[avg_y + offset_y, avg_x + offset_x],  # Apply offset to average coordinates
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color='green')  # Popup with the grouped stocking data
            ).add_to(m)

    # Display the updated map using Streamlit
    #st_folium(m, width=800, height=600)

    #st_folium(m_test, width=500, height=500)

# List of unique species in your dataset
species_list = df_updated['SPECIES'].unique()

# Streamlit Widgets
st.title("Fish Stocking Data Visualization")

# map_center = [44.6939, -69.3815]
# m_test = folium.Map(location=map_center, zoom_start=6)

# st_folium(m_test, width=800, height=600)

# Create checkboxes for each species
selected_species = st.multiselect(
    'Select Species:', species_list, default=species_list.tolist())  # Start with all species selected

# Create checkboxes for Spring and Fall Stocking
show_spring = st.checkbox('Spring Stocking (Jan-Jun)', value=False)
show_fall = st.checkbox('Fall Stocking (Jul-Dec)', value=False)

# Create a search bar to filter by water body, town, or county
search_term = st.text_input('Search by Water Body, Town, or County:', '')

# Create a text box for users to enter the minimum quantity of fish
min_qty_text = st.text_input('Enter Minimum Quantity of Fish:', '0')  # Default to 0 if not entered

# Convert min_qty_text to integer, ensuring it's valid
try:
    min_qty = int(min_qty_text)
except ValueError:
    min_qty = 0  # If the input is not a number, default to 0

# Display the interactive map when user changes selections
#update_map(selected_species, show_spring, show_fall, search_term, min_qty)

# Cache and store previous input states to prevent unnecessary updates
if 'prev_selected_species' not in st.session_state:
    st.session_state.prev_selected_species = selected_species
if 'prev_show_spring' not in st.session_state:
    st.session_state.prev_show_spring = show_spring
if 'prev_show_fall' not in st.session_state:
    st.session_state.prev_show_fall = show_fall
if 'prev_search_term' not in st.session_state:
    st.session_state.prev_search_term = search_term
if 'prev_min_qty' not in st.session_state:
    st.session_state.prev_min_qty = min_qty

# Check if any widget value has changed
if (selected_species != st.session_state.prev_selected_species or
    show_spring != st.session_state.prev_show_spring or
    show_fall != st.session_state.prev_show_fall or
    search_term != st.session_state.prev_search_term or
    min_qty != st.session_state.prev_min_qty):


    # Update session state after map update to prevent unnecessary re-runs
    st.session_state.prev_selected_species = selected_species
    st.session_state.prev_show_spring = show_spring
    st.session_state.prev_show_fall = show_fall
    st.session_state.prev_search_term = search_term
    st.session_state.prev_min_qty = min_qty
    update_map(selected_species, show_spring, show_fall, search_term, min_qty)
# update_map(selected_species, show_spring, show_fall, search_term, min_qty)    
    
st_folium(m, width=800, height=600)


#st_folium(m, width=800, height=600)
