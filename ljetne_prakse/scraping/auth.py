from getpass import getpass
from typing import Optional

import requests


def login_to_fer(
    username: Optional[str] = None,
    password: Optional[str] = None,
    endpoint_url: str = "https://www.fer.unizg.hr/login/Compound",
) -> requests.Session:
    if username is None:
        username = input("Please input your FERweb username or email: ")

    if password is None:
        password = input("Please input your FERweb password: ")

    payload = {"username": username, "password": password}

    session = requests.Session()
    response = session.post(endpoint_url, data=payload, files=payload)

    if str(response.url).strip() != "https://www.fer.unizg.hr/intranet":
        raise RuntimeError("Login failed! Check credentials!")

    return session
