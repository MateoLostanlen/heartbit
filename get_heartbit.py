import json
import os
from datetime import datetime
from getpass import getpass
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()
API_URL: str = os.environ.get("API_URL", "")
API_LOGIN: str = os.environ.get("API_LOGIN", "")
API_PWD: str = os.environ.get("API_PWD", "")


def get_token(api_url: str, login: str, pwd: str) -> str:
    response = requests.post(
        f"{api_url}/login/access-token",
        data={"username": login, "password": pwd},
        timeout=5,
    )
    if response.status_code != 200:
        raise ValueError(response.json()["detail"])
    return response.json()["access_token"]


def api_request(
    method_type: str,
    route: str,
    headers: Dict[str, str],
    payload: Optional[Dict[str, Any]] = None,
) -> Any:
    kwargs = {"json": payload} if payload else {}
    response = getattr(requests, method_type)(route, headers=headers, **kwargs)

    # Attempt to parse the JSON response
    try:
        response_json = response.json()
    except requests.exceptions.JSONDecodeError:
        raise ValueError("Failed to decode JSON from response")

    # Check for a successful response (HTTP status code 2xx)
    if response.status_code // 100 != 2:
        # Extract error detail from either a dict or a list response
        detail = (
            response_json.get("detail")
            if isinstance(response_json, dict)
            else "Error without detail"
        )
        raise ValueError(f"API request failed: {detail}")

    return response_json


def get_device_info(
    api_url: str, device_id: int, auth_headers: Dict[str, str]
) -> Dict[str, Any]:
    """
    Fetches information for a specific device by its ID.

    :param api_url: The base URL of the API.
    :param device_id: The ID of the device to fetch.
    :param auth_headers: Authentication headers containing the bearer token.
    :returns: A dictionary with the device information.
    """
    route = f"{api_url}/devices/{device_id}/"
    return api_request("get", route, auth_headers)


def get_all_device_info(api_url: str, auth_headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Fetches information for all devices

    :param api_url: The base URL of the API.

    :param auth_headers: Authentication headers containing the bearer token.
    :returns: A dictionary with the device information.
    """
    route = f"{api_url}/devices/"
    return api_request("get", route, auth_headers)


auth_token = get_token(API_URL, API_LOGIN, API_PWD)
auth_headers = {
    "Authorization": f"Bearer {auth_token}",
    "Content-Type": "application/json",
}

# Get last 50 devices data

try:
    all_devices_info = get_all_device_info(API_URL, auth_headers)
except ValueError as e:
    print(f"Error fetching device info: {e}")


# Get missing data

idx = all_devices_info[0]["id"]

for i in range(1, idx):
    try:
        all_devices_info.append(get_device_info(API_URL, i, auth_headers))
    except ValueError as e:
        print(f"Error fetching device info: {e}")


# Save to json

file_path = "heartbit.json"

if os.path.isfile(file_path):
    with open(file_path, "r") as file:
        hearbit_dict = json.load(file)

else:
    hearbit_dict = {}



for data in all_devices_info:
    login = data["login"]
    heartbit = data["last_ping"]
    if login not in hearbit_dict.keys():
        hearbit_dict[login] = []

    hearbit_dict[login].append(
        (datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), heartbit.split(".")[0])
    )


with open(file_path, "w") as f:
    json.dump(hearbit_dict, f, indent=4)
