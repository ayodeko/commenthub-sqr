import re
import smtplib
from datetime import timedelta, datetime
from email.mime.text import MIMEText
from urllib.parse import urlparse

import bcrypt
import requests
from bs4 import BeautifulSoup
from jose import jwt

from api.settings import SETTINGS


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SETTINGS.SECRET_KEY, algorithm=SETTINGS.ALGORITHM)
    return encoded_jwt


def send_verification_email(email, verification_token):
    msg = MIMEText(f"Use the following code to verify your email: {verification_token}")
    msg['Subject'] = 'Email Verification'
    msg['From'] = SETTINGS.SMTP_FROM_EMAIL
    msg['To'] = email

    try:
        with smtplib.SMTP_SSL(SETTINGS.SMTP_HOST, SETTINGS.SMTP_PORT) as server:
            server.login(SETTINGS.SMTP_LOGIN, SETTINGS.SMTP_PASSWORD)
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
    except Exception as e:
        print("Error sending email:", e)


def shorten_youtube_link(link: str) -> str:
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:.*v=|.*\/v\/|.*shorts\/)|youtu\.be\/)([\w-]+)"
    match = re.search(pattern, link)

    if match:
        video_id = match.group(1)
        return f"https://youtu.be/{video_id}"

    return link


def get_open_graph_name(url: str) -> str:
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        og_title = soup.find("meta", property="og:title")
        if og_title:
            return og_title["content"]

        return ""
    except requests.HTTPError:
        return ""


def get_platform_name(url: str) -> str:
    parsed_url = urlparse(url)

    domain_parts = parsed_url.netloc.split(".")

    if len(domain_parts) >= 2:
        main_domain = domain_parts[-2] + "." + domain_parts[-1]
        return main_domain.split(":")[0]
    return ""
