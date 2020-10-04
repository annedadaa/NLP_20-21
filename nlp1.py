from html import unescape
from bs4 import BeautifulSoup
import re
import time
import html
import collections
import pymorphy2
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import requests
from fake_useragent import UserAgent

ua = UserAgent(verify_ssl=False)
stopwords = stopwords.words("russian")
morph = pymorphy2.MorphAnalyzer()
session = requests.session()

def get_review(url):
    req = session.get(url, headers={'User-Agent': ua.random})
    page = req.text
    soup = BeautifulSoup(page, 'html.parser')
    page = soup.find_all('span', {'itemprop': 'reviewBody'})
    return page
good = get_review('https://www.kinopoisk.ru/film/401177/reviews/ord/date/status/good/perpage/75/')
bad = get_review('https://www.kinopoisk.ru/film/401177/reviews/ord/date/status/bad/perpage/75/')
both = get_review('https://www.kinopoisk.ru/film/401177/reviews/ord/date/status/all/perpage/25/')

def clean_text(raw):
    lines = []
    for line in raw:
        line = str(line)
        text = re.sub('<.*?>','',line)
        text2 = re.sub('[\n\r]',' ',text)
        lines.append(text2)
    return lines

def tokenize(text):
    words = []
    for i in text:
        for word in nltk.word_tokenize(i.lower()):
            if word.isalpha() and word not in stopwords:
                w = morph.parse(word)[0]
                w = w.normal_form
                words.append(w)
    return words
good_list = tokenize(clean_text(good))
bad_list = tokenize(clean_text(bad))

same_words = list(set(good_list)&set(bad_list))
print(same_words)
def spisok(some_list):
    c = collections.Counter()
    #d = collections.Counter()
    new_list = []
    for i in some_list:
        if i in same_words:
            continue
        else:
            c[i] += 1
    for k,v in c.items():
        if v > 1:
            new_list.append(k)
    return(new_list)

ok = spisok(good_list)
neok = spisok(bad_list)

def detect(both):
    res = []
    cleaned = clean_text(both)
    for j in cleaned:
        good = 0
        bad = 0
        tok = tokenize(j)
        for i in tok:
            if i in ok:
                good += 1
            if i in neok:
                bad += 1
        if good > bad:
            print(j[-100:] + ' положительный отзыв ))))')
            res.append('положит')
        else:
            print(j[-100:] + ' отрицательный отзыв ((((')
            res.append('отрицат')
    return(res)

from sklearn.metrics import accuracy_score
results = []
gold = []
for i in good:
    gold.append('положит')
for i in bad:
    gold.append('отриц')
results = detect(good) + detect(bad)
print("Accuracy: %.4f" % accuracy_score(results, gold))