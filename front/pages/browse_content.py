import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"

st.title("Search for content and look at the comments!")
content_url = st.text_input("Enter URL to look at the comments for this content.")
if st.button("Search"):
    response = requests.get(f"{API_BASE_URL}/entities", params={"url": content_url})
    if response.status_code == 200:
        content_data = response.json()
        for entity in content_data["entities"]:
            with st.container():
                st.write("**Name**:", entity["name"])
                st.write("**Platform**:", entity["platform"])
                st.write("**URL**:", f"[Link]({entity['url']})")

        if len(content_data["entities"]):
            entity_id = content_data["entities"][0]["id"]
            comments_response = requests.get(f"{API_BASE_URL}/feedbacks/{entity_id}")
            comments_data = comments_response.json()
            st.write("Comments:", comments_data["feedbacks"])
    else:
        st.warning("No content found for this link...")
        st.page_link("pages/create_content.py", label="If you are logged in, you can create an entity for this content", icon="✍️")