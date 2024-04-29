import streamlit as st
import requests

st.title("Search for content and look at the comments!")
content_url = st.text_input("Enter URL to search content")
if st.button("Search"):
    response = requests.get(
        f"{API_BASE_URL}/content/{content_url}",
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code == 200:
        content_data = response.json()
        st.write("Content Found:", content_data["content"])
        st.write("Comments:", content_data["comments"])

        comment_text = st.text_area("Add your comment")
        if st.button("Add Comment") and comment_text:
            content_id = content_data["content"]["id"]
            response = requests.post(
                f"{API_BASE_URL}/comment",
                headers={"Authorization": f"Bearer {token}"},
                json={"content_id": content_id, "text": comment_text},
            )
            if response.status_code == 200:
                st.success("Comment added successfully!")
            else:
                st.error("Error adding comment")
    else:
        st.error("No entity found.")