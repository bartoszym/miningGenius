from bs4 import BeautifulSoup
import requests
import re
from nltk.stem.snowball import EnglishStemmer
from nltk.tokenize import RegexpTokenizer
from nltk.lm.preprocessing import padded_everygram_pipeline
from nltk.lm import MLE


def fetch_url(url, *headers):
    try:
        if headers:
            resp = requests.get(url, headers=headers[0])
        else:
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

    return resp


def request_songs_urls(artist_number):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + 'ng7AckqnHLgmtcr1cW-Mk1qvngwnBzBUeAJszvm048jR4mV8z0vEsHRCz2o7RiHY'}
    number_of_songs = 30
    search_url = base_url + '/artists/'+str(artist_number)+'/songs?per_page={}'.format(number_of_songs)
    print(search_url)
    response = fetch_url(search_url, headers)

    data = response.json()
    data = data['response']['songs']
    links = []
    for url in data:
        links.append(url['url'])

    return links


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
    texts = []
    for url in links:
        page = fetch_url(url)
        soup = BeautifulSoup(page, 'html.parser')
        text = soup.find("div", {"class": "lyrics"}).get_text()
        texts.append(text)

    return texts


def delete_square_bracket(texts):
    new_texts = []
    for text in texts:
        text = re.sub(r'\[.*\]', '', text)
        new_texts.append(text)

    return new_texts


def stemming(texts):
    eng_stemmer = EnglishStemmer(ignore_stopwords=True)
    for i in range(len(texts)):
        text = texts[i]
        stemmed = ' '.join([eng_stemmer.stem(word) for word in text.split(" ")])
        texts[i] = stemmed
        # print(stemmed)


def preprocessing(texts):
    texts = delete_square_bracket(texts)
    tokenizer = RegexpTokenizer(r'\w+')
    tokenized_texts = []
    for text in texts:
        text = text.lower()
        tokenized_texts.append(tokenizer.tokenize(text))
    # stemming(texts)

    return tokenized_texts


def func():
    links = request_songs_urls(16775)

    print(links)
    # page = fetch_url("https://genius.com/albums/Mac-miller/Swimming")
    # links = get_songs_links(page)
    # texts = get_texts(links)
    # texts = preprocessing(texts)
    # # for text in texts:
    # #     print(text)
    #
    # ngram_length = 3
    # train_texts, vocab_texts = padded_everygram_pipeline(ngram_length, texts)
    # mac_model = MLE(ngram_length)
    # mac_model.fit(train_texts, vocab_texts)
    # generated_text = mac_model.generate(num_words=15)
    # print(generated_text)
    #
    # generated_text = mac_model.generate(num_words=15)
    # print(generated_text)
    # # for text in texts:
    # #     print(text)


    # print(links)


if __name__ == "__main__":
    func()
