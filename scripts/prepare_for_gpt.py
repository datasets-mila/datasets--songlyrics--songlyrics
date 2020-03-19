import json
import numpy as np
import nltk
from nltk import word_tokenize

# Check nltk dependencies
try:
    nltk.find('tokenize/punkt')
except LookupError:
    nltk.download('punkt')  # used in word_tokenize()


def get_json_from_file(file_path):
    with open(file_path, 'r') as f:
        json_object = json.load(f)
    return json_object


def main():

    for scope in ('train', 'valid', 'test'):
        print("reading %s_songlyrics.json..." % scope)
        data = get_json_from_file('%s_songlyrics.json' % scope)
        '''
        {
            'artists': list(d2['artists'][scope_idx]),
            'titles':  list(d2['titles'][scope_idx]),
            'lyrics':  list(d2['lyrics'][scope_idx]),
            'genres':  list(d2['genres'][scope_idx]),
            'tfidf_keywords' : list of top key words
        }
        '''

        f_out = open("./gpt/%s_songlyrics.gpt.txt" % scope, "w")

        np.random.seed(1234)
        empty_songs = 0
        for idx, song in enumerate(data['lyrics']):
            if (idx+1) % 10000 == 0:
                print('Finished %d / %d songs' % ((idx+1), len(data['lyrics'])))

            if len(song) == 0:
                empty_songs += 1
                continue

            # sample a subset of key words
            keywords = data['tfidf_keywords'][idx]
            k = np.random.randint(len(keywords))
            keywords = ' '.join(keywords[:k+1])

            song_lines = [
                '<GENRE> %s' % data['genres'][idx],
                '<ARTIST> %s' % data['artists'][idx],
                '<TITLE> %s' % data['titles'][idx],
                '<KEYWORDS> %s' % keywords,
                '<LYRICS>'
                # start-of-song
            ]
            lines = ''
            for line in song.split('\n'):
                line = word_tokenize(line)
                line.append('<END-OF-LINE>')
                lines += (' '.join(line[::-1]) + ' ')  # each line is reversed
            song_lines.append(lines)
            song_lines.append('<END-OF-SONG>')

            # f_out.write('\n'.join(song_lines) + '\n')  # 6 lines per song
            f_out.write(' '.join(song_lines) + '\n')    # 1 line per song

        print("skipped %d empty songs." % empty_songs)


if __name__ == '__main__':
    main()
    print("done.")
