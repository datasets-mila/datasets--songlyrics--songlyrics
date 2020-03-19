import json
import nltk
import math
import numpy as np
from nltk import word_tokenize
from collections import Counter

# Check nltk dependencies
try:
    nltk.find('tokenize/punkt')
except LookupError:
    nltk.download('punkt')  # used in word_tokenize()


MAX_N_KEYWORDS = 10


def get_json_from_file(file_path):
    with open(file_path, 'r') as f:
        json_object = json.load(f)
    return json_object


def compute_tfidf(lyrics):
    empty_songs = 0

    print("computing TF : freq of term in doc / number of terms in doc...")
    tf = []  # list of dict for each song
    idf = Counter()  # map from term to n_of_doc with this term

    for idx, song in enumerate(lyrics):
        if (idx + 1) % 10000 == 0:
            print(' %d / %d songs' % ((idx + 1), len(lyrics)))

        c = Counter()  # map from term to count
        for line in song.split('\n'):
            line = word_tokenize(line.lower())
            c.update(line)
        # make c a map from term to frequency
        n_words = sum(c.values())*1.0
        for w in c:
            c[w] /= n_words
        tf.append(c)

        idf.update(c.keys())

    print("computing IDF : ln(n_of_docs / n_of_docs with this term)...")

    # make idf a map from term to : ln(n_of_docs / n_of_docs with this term)
    n_doc = len(lyrics)*1.0
    for w in idf:
        idf[w] = math.log(n_doc / idf[w])

    tfidf = []  # list of top keyword for each document
    for doc in tf:
        doc_w2tfidf = dict([(w, doc[w]*idf[w]) for w in doc])
        # print('tfidf :', doc_w2tfidf)
        if len(doc_w2tfidf) == 0:
            # skip empty songs
            empty_songs += 1
            tfidf.append([])
            continue

        # make ordered list of key/values from tfidf dict
        doc_wd, doc_tfidf = [], []
        for w, score in doc_w2tfidf.items():
            doc_wd.append(w)
            doc_tfidf.append(score)

        max_idx = np.array(doc_tfidf).argsort()[-MAX_N_KEYWORDS:][::-1]
        max_wd = np.array(doc_wd)[max_idx]
        tfidf.append(max_wd.tolist())

    return tfidf, empty_songs


def main():

    for scope in ('train', 'valid', 'test'):
        file_name = '%s_songlyrics.json' % scope

        print("reading %s..." % file_name)
        data = get_json_from_file(file_name)
        '''
        {
            'artists': list(d2['artists'][scope_idx]),
            'titles':  list(d2['titles'][scope_idx]),
            'lyrics':  list(d2['lyrics'][scope_idx]),
            'genres':  list(d2['genres'][scope_idx]),
            'tfidf_keyword' : maybe ?
        }
        '''

        if 'tfidf_keyword' in data:
            if len(data['tfidf_keyword']) == len(data['titles']):
                print('tf-idf keyword already computed. skip.')
                continue
            else:
                del data['tfidf_keyword']

        tfidf, skipped = compute_tfidf(data['lyrics'])
        print("skipped :", skipped)
        assert len(tfidf) == len(data['titles'])

        data['tfidf_keywords'] = tfidf

        print("saving %s_songlyrics.json ..." % scope)
        with open("%s_songlyrics.json" % scope, 'w') as f:
            json.dump(data, f)


if __name__ == '__main__':
    main()
    # print(compute_tfidf(["the cat sat on the mat", "the dog sat on the cat"]))
    print("done.")
