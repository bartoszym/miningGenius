from bs4 import BeautifulSoup
import requests
import re
from nltk.stem.snowball import EnglishStemmer
from nltk.tokenize import RegexpTokenizer
from nltk.lm.preprocessing import padded_everygram_pipeline
from nltk.lm import MLE


def fetch_url(url, headers=None, params=None):
    '''Fetches url and returns response'''
    try:
        resp = requests.get(url, headers=headers, params=params)
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


def search_for_artist(artist):
    '''Finds url of artist'''
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer '
                                + 'ng7AckqnHLgmtcr1cW-Mk1qvngwnBzBUeAJszvm048jR4mV8z0vEsHRCz2o7RiHY'}
    search_url = base_url + '/search?q=' + artist
    response = fetch_url(search_url, headers)
    response = response.json()
    return(response['response']['hits'][0]['result']['primary_artist']['api_path'])


def request_songs_id(artist_number, amount_songs):
    '''Returns songs ids of artist'''
    songs_ids = []
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer '
                                + 'ng7AckqnHLgmtcr1cW-Mk1qvngwnBzBUeAJszvm048jR4mV8z0vEsHRCz2o7RiHY'}
    search_url = base_url + str(artist_number) + '/songs?per_page={}'.format(amount_songs)

    i = 0
    page = 1
    not_enough = 1
    while not_enough:
        params = {'page': page}
        response = fetch_url(search_url, headers=headers, params=params)

        data = response.json()
        data = data['response']['songs']
        for song in data:
            if song['primary_artist']['api_path'] == artist_number:
                songs_ids.append(song['id'])
                i += 1
        if i >= 170:
            not_enough = 0
        page += 1

    return songs_ids


def request_text(ids):
    '''Creates array of texts'''
    base_url = 'https://genius.com'
    texts = []
    i = 0
    for song_id in ids:
        song_url = base_url + '/songs/' + str(song_id)
        response = fetch_url(song_url)
        texts.append(get_lyrics(response))
        i += 1
        if i % 10 == 0:
            print('I scrapped {} texts'.format(i))

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
    artist_url = search_for_artist('Ten Typ Mes')
    ids = request_songs_id(artist_url, 50)

    texts = request_text(ids)
    for text in texts:
        print(text)

    texts = preprocessing(texts)

    ngram_length = 3
    train_texts, vocab_texts = padded_everygram_pipeline(ngram_length, texts)
    mac_model = MLE(ngram_length)
    mac_model.fit(train_texts, vocab_texts)
    generated_text = mac_model.generate(num_words=30)
    print(generated_text)



if __name__ == "__main__":
    func()
