import json

import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"

st.title("Search for content and look at the comments!")
content_url = st.text_input("Enter URL to look at the comments for this content.")

if 'clicked_search' not in st.session_state:
    st.session_state.clicked_search = False
if 'clicked_comment' not in st.session_state:
    st.session_state.clicked_comment = False
if 'entity_id' not in st.session_state:
    st.session_state.entity_id = -1


def click_search():
    st.session_state.clicked_search = True


def clicked_comment():
    st.session_state.clicked_comment = True


st.button("Search", on_click=click_search)
if st.session_state.clicked_search:
    response = requests.get(f"{API_BASE_URL}/entities", params={"url": content_url})
    if response.status_code == 200:
        content_data = response.json()
        for entity in content_data["entities"]:
            with st.container():
                st.write("**Name**:", entity["name"])
                st.write("**Platform**:", entity["platform"])
                st.write("**URL**:", f"[Link]({entity['url']})")

        if content_data["entities"]:
            st.session_state.entity_id = content_data["entities"][0]["id"]

            sort_order = st.selectbox("Sort comments by", ["asc", "desc"], index=0)
            filter_last_days = st.number_input("Filter comments based on the number of days (0 by default)", min_value=0,
                                               max_value=365, value=0, step=1)
            filter_last_days = None if filter_last_days == 0 else filter_last_days

            comments_response = requests.get(f"{API_BASE_URL}/feedbacks/{st.session_state.entity_id}")
            comments_data = comments_response.json()
            if not comments_data["feedbacks"]:
                st.write("*:blue[There are no comments yet!]*")
            for comment in comments_data["feedbacks"]:
                with st.container():
                    st.write("**Username**:", comment["username"])
                    st.write("**Text**:", comment["text"])
                    st.write("**Created at**:", comment["created_at"])
    else:
        st.warning("No content found for this link...")

if 'access_token' in st.session_state and st.session_state['access_token'] and st.session_state.entity_id != -1:
    st.button("Add comment", on_click=clicked_comment)
    comment_text = st.text_input("Comment text", placeholder="text")
    if st.session_state.clicked_comment and comment_text:
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        add_comment_data = {"text": comment_text}
        response = requests.post(f"{API_BASE_URL}/feedbacks/{st.session_state.entity_id}",
                                 data=json.dumps(add_comment_data), headers=headers)
        if response.status_code == 200:
            st.success("Comment added successfully!")
        else:
            st.error("Error when adding comment...")
