import json

import streamlit as st
import requests

API_BASE_URL = "http://localhost:8000"

st.title("Welcome to Comment Hub!")
choice = st.selectbox("Are you new here or returning?", ("Sign up", "Log in"))

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if choice == "Log in":
    with st.form("login_form"):
        st.write("Log in")
        email = st.text_input("E-mail", placeholder="email")
        password = st.text_input("Password", type="password")
        login_data = {"email": email, "password": password}
        login_button = st.form_submit_button("Log in")

    if login_button:
        response = requests.post(url=f"{API_BASE_URL}/users/login", data=json.dumps(login_data))
        if response.status_code == 200:
            st.success("Logged in successfully!")
            st.session_state['logged_in'] = True
            st.page_link("pages/create_content.py", label="Create content.", icon="📖")
        else:
            st.error("Invalid login credentials")

if choice == "Sign up":
    with st.form("register_form"):
        st.write("Sign up")
        reg_username = st.text_input("Unique username", placeholder="username")
        reg_email = st.text_input("E-mail", placeholder="email")
        reg_password = st.text_input("Password", type="password")
        reg_data = {"username": reg_username, "email": reg_email, "password": reg_password}
        signup_button = st.form_submit_button("Sign up")

    if signup_button:
        response = requests.post(url=f"{API_BASE_URL}/users", data=json.dumps(reg_data))
        if response.status_code == 200:
            st.success("Verification code sent! Please check your email.")
            st.page_link("pages/email_verification.py", label="Go to email verification.", icon="✔️")
        else:
            st.error("Something went wrong with signing up...")


st.page_link("pages/browse_content.py", label="Just browse the content.", icon="👀")

