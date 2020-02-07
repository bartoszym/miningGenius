from bs4 import BeautifulSoup
import requests

def fetch_url(url):
    try:
        resp = requests.get(url)
    except requests.exceptions.MissingSchema:
        return "Wrong URL, maybe missed 'http://'"

    try:
        resp.raise_for_status()
    except requests.HTTPError as err:
        if 400 <= err.response.status_code < 500:
            return 'Client error'
        if 500 <= err.response.status_code < 600:
            return 'Server error'

    return resp.text

def func():
    page = fetch_url("https://genius.com/artists/Mac-miller")
    print(page)


if __name__ == "__main__":
	func()
