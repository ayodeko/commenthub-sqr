import json

import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"

st.title("Email verification")

verification_code = st.text_input("Enter the verification code sent to your email.")

if st.button("Verify"):
    response = requests.get(url=f"{API_BASE_URL}/users/verify/{verification_code}")
    if response.status_code == 200:
        st.success("Email verified, you can now log in.")
        st.page_link("pages/welcome_page.py", label="Go to log in.", icon="🖥️")
    else:
        st.error("Invalid or expired verification code.")
