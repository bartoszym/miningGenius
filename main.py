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


def get_songs_links(resptext):
    soup = BeautifulSoup(resptext, 'html.parser')
    arr_links = []
    for link in soup.findAll("a", {"class": "u-display_block"}):
        arr_links.append(link.get('href'))

    if len(arr_links) == 0:
        return 0
    else:
        return arr_links


def get_texts(links):
    for url in links:
        page = fetch_url(url)
        soup = BeautifulSoup(page, 'html.parser')
        text = soup.find("div", {"class": "lyrics"}).get_text()
        print(text)


def func():
    page = fetch_url("https://genius.com/albums/Mac-miller/Swimming")
    links = get_songs_links(page)
    texts = get_texts(links)

    # print(links)


if __name__ == "__main__":
    func()
