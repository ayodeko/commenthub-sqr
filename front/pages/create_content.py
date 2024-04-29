import streamlit as st


if not st.session_state['logged_in']:
    st.warning("You are not logged in, you do not have access to leaving a comment or creating a content entity, "
               "browse the content or log in.")
    st.page_link("pages/browse_content.py", label="Browse the content.", icon="👀")
    st.page_link("welcome_page.py", label="Go to log in.", icon="🖥️")

else:

# if st.button("Create"):
#     new_content_url = st.text_input("Add new content")
#     if new_content_url:
#         response = requests.post(
#             f"{API_BASE_URL}/content",
#             headers={"Authorization": f"Bearer {token}"},
#             json={"url": new_content_url},
#         )
#         if response.status_code == 200:
#             st.success("Content added successfully!")
#         else:
#             st.error("Error adding content")