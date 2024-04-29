import json

import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"


if 'access_token' not in st.session_state or st.session_state['access_token'] is None:
    st.switch_page("welcome_page.py")

else:
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    new_content_url = st.text_input("Enter the URL to add a new entity for and press Enter.")
    if 'new_entity_data' not in st.session_state:
        st.session_state['new_entity_data'] = {
            "url": "",
            "name": "",
            "platform": ""
        }
    if new_content_url:
        if st.button("Try to fetch information from URL"):
            response_url_data = requests.get(f"{API_BASE_URL}/entities/fetch", headers=headers,
                                             params={"url": new_content_url})
            url_data = response_url_data.json()
            st.session_state['new_entity_data']["url"] = st.text_input("URL", value=url_data.get("url", ""))
            st.session_state['new_entity_data']["name"] = st.text_input("Name", value=url_data.get("name", ""))
            st.session_state['new_entity_data']["platform"] = st.text_input("Platform",
                                                                            value=url_data.get("platform", ""))

        if st.button("Create a new entity"):
            response = requests.post(f"{API_BASE_URL}/entities", headers=headers,
                                     data=json.dumps(st.session_state['new_entity_data']))

            if response.status_code == 200:
                st.success("Content added successfully!")
            else:
                st.error("Error when adding content...")
