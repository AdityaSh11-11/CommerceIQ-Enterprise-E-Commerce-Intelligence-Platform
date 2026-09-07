import requests


def get_json(url):
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.json()