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


def request_songs_id(artist_number, amount_songs):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer '
                                + 'ng7AckqnHLgmtcr1cW-Mk1qvngwnBzBUeAJszvm048jR4mV8z0vEsHRCz2o7RiHY'}
    search_url = base_url + '/artists/' + str(artist_number) + '/songs?per_page={}'.format(amount_songs)
    response = fetch_url(search_url, headers)

    data = response.json()
    data = data['response']['songs']
    songs_ids = []
    for url in data:
        songs_ids.append(url['id'])

    return songs_ids


def request_text(ids):
    base_url = 'https://genius.com'
    texts = []
    for song_id in ids:
        song_url = base_url + '/songs/' + str(song_id)
        response = fetch_url(song_url)
        texts.append(get_lyrics(response))

    return texts


def get_lyrics(page):
    soup = BeautifulSoup(page.text, 'html.parser')
    text = soup.find("div", {"class": "lyrics"}).get_text()

    return text


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
    ids = request_songs_id(72, 50)

    texts = request_text(ids)
    # for text in texts:
    #     print(text)

    texts = preprocessing(texts)
    # for text in texts:
    #     print(text)

    ngram_length = 3
    train_texts, vocab_texts = padded_everygram_pipeline(ngram_length, texts)
    mac_model = MLE(ngram_length)
    mac_model.fit(train_texts, vocab_texts)
    generated_text = mac_model.generate(num_words=15)
    print(generated_text)

    generated_text = mac_model.generate(num_words=15)
    print(generated_text)
    # for text in texts:
    #     print(text)


    # print(links)


if __name__ == "__main__":
    func()
