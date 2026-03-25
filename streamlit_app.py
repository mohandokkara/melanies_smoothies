# Import python packages
import streamlit as st
import requests
import pandas as pd
 
# -------------------------------
# UI HEADER
# -------------------------------
st.title('Customize Your Smoothie')
st.write("Choose the fruits you want in your Smoothie!")
 
# -------------------------------
# USER INPUT
# -------------------------------
name_on_order = st.text_input('Name on Smoothie: ')
st.write('The name on your smoothie will be:', name_on_order)
 
# -------------------------------
# SNOWFLAKE CONNECTION
# -------------------------------
cnx = st.connection("snowflake")
session = cnx.session()
 
# -------------------------------
# FETCH DATA (IMPORTANT: include SEARCH_ON)
# -------------------------------
query = "SELECT FRUIT_NAME, SEARCH_ON FROM SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
pd_df = session.sql(query).to_pandas()
 
# Convert to list for UI
fruit_list = pd_df["FRUIT_NAME"].tolist()
 
# -------------------------------
# MULTISELECT (DEFINE FIRST)
# -------------------------------
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_list,
    max_selections=5
)
 
# -------------------------------
# PROCESS SELECTED FRUITS
# -------------------------------
if ingredients_list:
 
    # Clean string creation
    ingredients_string = " ".join(ingredients_list)
 
    for fruit_chosen in ingredients_list:
 
        # -------------------------------
        # GET SEARCH_ON VALUE
        # -------------------------------
        try:
            search_on = pd_df.loc[
                pd_df['FRUIT_NAME'] == fruit_chosen,
                'SEARCH_ON'
            ].iloc[0]
 
            st.success(f"The search value for {fruit_chosen} is {search_on}")
 
        except:
            st.error(f"Search value not found for {fruit_chosen}")
            continue
 
        # -------------------------------
        # DISPLAY SECTION HEADER
        # -------------------------------
        st.markdown("---")
        st.subheader(f"{fruit_chosen} Nutrition Information")
 
        # -------------------------------
        # API CALL USING SEARCH_ON
        # -------------------------------
        try:
            url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            response = requests.get(url)
 
            if response.status_code == 200:
                data = response.json()
 
                # Convert JSON → DataFrame
                df_api = pd.json_normalize(data)
 
                # Display nicely
                st.dataframe(df_api, use_container_width=True)
 
            else:
                st.warning(f"{fruit_chosen} not found in Smoothiefroot database")
 
        except Exception as e:
            st.error(f"Error fetching data for {fruit_chosen}")
 
    # -------------------------------
    # INSERT INTO SNOWFLAKE
    # -------------------------------
    if st.button('Submit Order'):
 
        try:
            insert_sql = f"""
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS(ingredients, name_on_order)
            VALUES('{ingredients_string}', '{name_on_order}')
            """
 
            session.sql(insert_sql).collect()
 
            st.success('Your smoothie is ordered!', icon="✅")
 
        except Exception as e:
            st.error("Failed to insert order")
