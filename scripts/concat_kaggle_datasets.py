import re
import sys
import csv
import json
import pyprind
import random
import nltk
from nltk import word_tokenize
from collections import defaultdict


def read_columns(path, c_ids=None, skip_first_line=True):
    """
    Read csv file and return list of columns data
    :param path: path to the .csv file to read
    :param c_ids: id of the columns to return - default to all
    :param skip_first_line: skip the first line of the csv file (often header line) - default to True
    """
    if c_ids is not None:
        columns = list([] for _ in c_ids)  # list of required columns
    else:
        columns = None

    with open(path, 'r') as f:
        reader = csv.reader(f)
        for r, row in enumerate(reader):
            # skip first line
            if r == 0 and skip_first_line:
                continue

            # grab all columns as default
            if c_ids is None:
                c_ids = list(range(len(row)))
            if columns is None:
                columns = list([] for _ in c_ids)

            # add relevant columns to data
            for i, idx in enumerate(c_ids):
                columns[i].append(row[idx])

    return columns


def write_songs_to_file(json_object, file_path):
    with open(file_path, 'w') as f:
        json.dump(json_object, f)


def read_song_from_file(file_path):
    with open(file_path, 'r') as f:
        json_object = json.load(f)
    return json_object


def map_fn(sentence):
    """
    function to be applied to all sentences:
    - remove all occurrences of [...]
    - remove all occurrences of (...)

    - check that each line is not only made of "repeat", "chorus", "verse", "refrain", x3, :, ...

    - Ignore those cases:
            "Fc C gc", "F G Em Am", ...
            "Adlib: C-Fc-C-Bb-Fa-F7 sus"
    """
    # print("original sentence: <%s>" % sentence)

    # remove all [*] & (*) - ex: [Bridge] & [Verse #] & [Repeat: x3] & [Guitar solo] & ...
    sentence = re.sub(sq_brackets, '', sentence)
    sentence = re.sub(rd_brackets, '', sentence)

    # check that the line is not only made of "repeat", "chorus", "refrain", x3, :, ...
    tmp_line = sentence.lower().replace('repeat', ' ')
    # tmp_line = tmp_line.replace('times', ' ')
    tmp_line = tmp_line.replace('chorus', ' ')
    tmp_line = tmp_line.replace('verse', ' ')
    tmp_line = tmp_line.replace('refrain', ' ')
    tmp_line = tmp_line.replace('intro', ' ')
    tmp_line = tmp_line.replace('solo', ' ')
    tmp_line = tmp_line.replace(':', ' ')
    tmp_line = re.sub(rp_number, ' ', tmp_line)
    # if original sentence was >0 and there is 0 or 1 word left, consider this line empty
    # ^ this is also removing lines with only one word.
    # Anyway we don't want to generate 1-word lines
    if len(sentence.strip().split()) > 0 and len(tmp_line.strip().split()) < 2:
        # if len(sentence.strip()) > 0:
        #     print("ignoring this line:", sentence)
        return ''

    # replace all bad words by <unk>
    for b_w in BAD_WORDS:
        if b_w.lower().strip() in sentence.lower().split():
            # print("replacing <%s> by <unk> in <%s>" % (b_w.lower().strip(), sentence))
            sentence = re.sub(b_w.strip(), "<unk>", sentence, flags=re.IGNORECASE)

    # print("return   sentence: <%s>" % sentence.strip())
    return sentence.strip()


def extract_kaggle_mousehead_songlyrics():
    """
    extract all lyrics from the cvs file from "extract/songdata.csv"
    """
    artists, titles, links, lyrics = read_columns("extract/songdata.csv")
    assert len(artists) == len(titles) == len(links) == len(lyrics)
    print("\nnumber of songs in kaggle_mousehead_songlyrics:", len(artists))

    n_sentences = 0.0  # avg number of sentences per song
    sent_length = 0.0  # avg number of words per sentence

    lc_songs = 0  # number of songs from leonard cohen

    # lyrics = lyrics[:10]
    bar = pyprind.ProgBar(len(lyrics), stream=sys.stdout)
    for index, song in enumerate(lyrics):
        # remove "
        song = song.replace('"', '')

        sentences = song.split("\n")
        # clean all sentences
        sentences = list(map(map_fn, sentences))
        # remove resulting empty sentences
        sentences = list(filter(lambda s: len(s.strip()) > 0, sentences))

        n_sentences += len(sentences)

        for sent in sentences:
            tokens = word_tokenize(sent)
            sent_length += len(tokens)

        lyrics[index] = '\n'.join(sentences)

        ###
        # regularize artist & title names
        ###
        artists[index] = artists[index].strip().lower().replace(' ', '_').replace('-', '_')
        if 'leonard' in artists[index] and 'cohen' in artists[index]:
            lc_songs += 1

        titles[index] = titles[index].strip().lower()
        # replace all bad words by <unk> in title
        for b_w in BAD_WORDS:
            if b_w.lower().strip() in titles[index].split():
                # print("replacing <%s> by <unk> in <%s>" % (b_w.lower().strip(), titles[index]))
                titles[index] = re.sub(b_w.strip(), "<unk>", titles[index], flags=re.IGNORECASE)

        bar.update()

    sent_length /= n_sentences  # average number of tokens per sentence
    n_sentences /= len(lyrics)  # average number of sentences per song

    print("avg. #of tokens per sentence:", sent_length)
    print("avg. #of sentences per song:", n_sentences)
    print("#of leonard cohen songs:", lc_songs)

    return artists, titles, lyrics


def extract_kaggle_gyani95_songlyrics():
    """
    extract all lyrics from the cvs file from "extract/lyrics.csv"
    """
    indexes, titles, years, artists, genres, lyrics = read_columns("extract/lyrics.csv")
    assert len(indexes) == len(titles) == len(years) == len(artists) == len(genres) == len(lyrics)
    print("\nnumber of songs in kaggle_gyani95_songlyrics:", len(lyrics))

    n_sentences = 0.0  # avg number of sentences per song
    sent_length = 0.0  # avg number of words per sentence

    lc_songs = 0  # number of songs from leonard cohen

    # lyrics = lyrics[:10]
    bar = pyprind.ProgBar(len(lyrics), stream=sys.stdout)
    for index, song in enumerate(lyrics):

        # remove "
        song = song.replace('"', '')

        sentences = song.split("\n")
        # clean all sentences
        sentences = list(map(map_fn, sentences))
        # remove resulting empty sentences
        sentences = list(filter(lambda s: len(s.strip()) > 0, sentences))

        n_sentences += len(sentences)

        for sent in sentences:
            tokens = word_tokenize(sent)
            sent_length += len(tokens)

        lyrics[index] = '\n'.join(sentences)

        ###
        # regularize genre & artist & title
        ###
        genres[index] = genres[index].strip().lower().replace(' ', '_').replace('-', '_')

        artists[index] = artists[index].strip().lower().replace(' ', '_').replace('-', '_')
        if 'leonard' in artists[index] and 'cohen' in artists[index]:
            lc_songs += 1

        titles[index] = titles[index].strip().lower().replace('-', ' ')  # undo the processing from this csv file
        # replace all bad words by <unk> in title
        for b_w in BAD_WORDS:
            if b_w.lower().strip() in titles[index].split():
                # print("replacing <%s> by <unk> in <%s>" % (b_w.lower().strip(), titles[index]))
                titles[index] = re.sub(b_w.strip(), "<unk>", titles[index], flags=re.IGNORECASE)

        bar.update()

    sent_length /= n_sentences  # average number of tokens per sentence
    n_sentences /= len(lyrics)  # average number of sentences per song

    print("avg. #of tokens per sentence:", sent_length)
    print("avg. #of sentences per song:", n_sentences)
    print("#of leonard cohen songs:", lc_songs)

    return artists, titles, genres, lyrics


def extract_kaggle_artimous_songlyrics():
    """
    extract all lyrics from the cvs file from "extract/Lyrics{1|2}.csv"
    """
    bands1, lyrics1, titles1 = read_columns("extract/Lyrics1.csv")
    bands2, lyrics2, titles2 = read_columns("extract/Lyrics2.csv")
    bands = bands1 + bands2
    lyrics = lyrics1 + lyrics2
    titles = titles1 + titles2
    assert len(bands) == len(lyrics) == len(titles)
    print("\nnumber of songs in kaggle_artimous_songlyrics:", len(lyrics))

    n_sentences = 0.0  # avg number of sentences per song
    sent_length = 0.0  # avg number of words per sentence

    lc_songs = 0  # number of songs from leonard cohen

    # lyrics = lyrics[:100]
    bar = pyprind.ProgBar(len(lyrics), stream=sys.stdout)
    for index, song in enumerate(lyrics):
        # remove "
        song = song.replace('"', '')

        sentences = song.split("\n")
        # clean all sentences
        sentences = list(map(map_fn, sentences))
        # remove resulting empty sentences
        sentences = list(filter(lambda s: len(s.strip()) > 0, sentences))

        n_sentences += len(sentences)

        for sent in sentences:
            tokens = word_tokenize(sent)
            sent_length += len(tokens)

        lyrics[index] = '\n'.join(sentences)

        ###
        # regularize artist & title names
        ###
        bands[index] = bands[index].strip().lower().replace(' ', '_').replace('-', '_')
        if 'leonard' in bands[index] and 'cohen' in bands[index]:
            lc_songs += 1

        titles[index] = titles[index].strip().lower()
        # replace all bad words by <unk> in title
        for b_w in BAD_WORDS:
            if b_w.lower().strip() in titles[index].split():
                # print("replacing <%s> by <unk> in <%s>" % (b_w.lower().strip(), titles[index]))
                titles[index] = re.sub(b_w.strip(), "<unk>", titles[index], flags=re.IGNORECASE)

        bar.update()

    sent_length /= n_sentences  # average number of tokens per sentence
    n_sentences /= len(lyrics)  # average number of sentences per song

    print("avg. #of tokens per sentence:", sent_length)
    print("avg. #of sentences per song:", n_sentences)
    print("#of leonard cohen songs:", lc_songs)

    return bands, titles, lyrics


def extract_kaggle_paultimothymooney_songlyrics():
    """
    extract all lyrics from the txt files in "kaggle_paultimothymooney_songlyrics/"
    """
    # NO WAY OF SPLITTING SONGS IN THE DIFFERENT TEXT FILES... -_-
    # IT'S JUST A CONTINUOUS THREAD OF SONG LINES
    return None


def remove_duplicates(items1, items2):
    # remove empty items
    items1 = list(filter(lambda item: len(item) > 0, items1))
    items2 = list(filter(lambda item: len(item) > 0, items2))

    # convert to lowercase
    items1 = list(map(lambda item: item.lower(), items1))
    items2 = list(map(lambda item: item.lower(), items2))

    # remove duplicates
    items = set(items1)
    items.update(items2)
    return list(items)


def get_unique_indices(items):
    """
    Returns a list of indices for all *unique* element
    :param items: list containing duplicated elements
    """
    # remove empty items
    items = list(filter(lambda item: len(item) > 0, items))

    # convert to lowercase
    items = list(map(lambda item: item.lower(), items))

    # get unique indices
    uniques = defaultdict(list)
    for index, element in enumerate(items):
        uniques[element].append(index)

    return [indices[0] for indices in uniques.values()]  # return the index of the first occurrence for every duplicate


def main():
    nltk.download('punkt')

    # -------
    # STEP 1:
    # -------
    # Read each file and create a list of songs in a json file
    #
    artists, titles, lyrics = extract_kaggle_mousehead_songlyrics()
    genres = ['unknown']*len(titles)
    write_songs_to_file(
        {'artists': artists, 'titles': titles, 'lyrics': lyrics, 'genres': genres},
        'kaggle_mousehead_songlyrics.json'
    )
    print("number of songs:", len(lyrics))
    idx = list(range(len(lyrics)))
    random.shuffle(idx)
    print("a few songs...")
    for i in idx[:5]:
        print('#', i, '- ARTIST:', artists[i], '- TITLE:', titles[i], '- GENRE:', genres[i])
        print(lyrics[i])
    print("---------------------------------------")

    artists, titles, genres, lyrics = extract_kaggle_gyani95_songlyrics()
    write_songs_to_file(
        {'artists': artists, 'titles': titles, 'lyrics': lyrics, 'genres': genres},
        'kaggle_gyani95_songlyrics.json'
    )
    print("number of songs:", len(lyrics))
    idx = list(range(len(lyrics)))
    random.shuffle(idx)
    print("a few songs...")
    for i in idx[:5]:
        print('#', i, '- ARTIST:', artists[i], '- TITLE:', titles[i], '- GENRE:', genres[i])
        print(lyrics[i])
    print("---------------------------------------")

    artists, titles, lyrics = extract_kaggle_artimous_songlyrics()
    genres = ['unknown'] * len(titles)
    write_songs_to_file(
        {'artists': artists, 'titles': titles, 'lyrics': lyrics, 'genres': genres},
        'kaggle_artimous_songlyrics.json'
    )
    print("number of songs:", len(lyrics))
    idx = list(range(len(lyrics)))
    random.shuffle(idx)
    print("a few songs...")
    for i in idx[:5]:
        print('#', i, '- ARTIST:', artists[i], '- TITLE:', titles[i], 'GENRE:', genres[i])
        print(lyrics[i])
    print("---------------------------------------")

    # lyrics4 = extract_kaggle_paultimothymooney_songlyrics()
    # write_songs_to_file(lyrics4, 'kaggle_paultimothymooney_songlyrics.json')

    del artists, titles, genres, lyrics

    # -------
    # STEP 2:
    # -------
    # Remove duplicate songs

    # combine all lists into one
    d1 = read_song_from_file('kaggle_mousehead_songlyrics.json')
    d2 = read_song_from_file('kaggle_gyani95_songlyrics.json')
    d3 = read_song_from_file('kaggle_artimous_songlyrics.json')

    # append to d2 bcs that's the dict with a bunch of GENRES so when removing duplicates
    # we will keep the first ones, the ones from d2, the ones with a genre
    for key, values in d2.items():
        values.extend(d1[key])
        values.extend(d3[key])
    del d1, d3

    print("Total number of songs:", (len(d2['lyrics'])))

    unique_indices = get_unique_indices(d2['lyrics'])
    d2['artists'] = [d2['artists'][i] for i in unique_indices]
    d2['titles'] = [d2['titles'][i] for i in unique_indices]
    d2['lyrics'] = [d2['lyrics'][i] for i in unique_indices]
    d2['genres'] = [d2['genres'][i] for i in unique_indices]

    assert len(d2['artists']) == len(d2['titles']) == len(d2['lyrics']) == len(d2['genres']) == len(unique_indices)
    print("Number of unique songs:", len(unique_indices))
    print("Number of leonard cohen songs:", len(list(
        filter(lambda a: 'leonard' in a and 'cohen' in a, d2['artists'])
    )))

    # -------
    # STEP 3:
    # -------
    # Split into train / valid / test set
    #
    train_split_idx = int(0.8 * len(d2['lyrics']))
    valid_split_idx = int(0.9 * len(d2['lyrics']))
    # test_split_idx  = int(1.0 * len(d2['lyrics']))

    random.seed(1234)
    indices = list(range(len(d2['lyrics'])))
    random.shuffle(indices)

    train_idx = indices[:train_split_idx]
    valid_idx = indices[train_split_idx: valid_split_idx]
    test_idx  = indices[valid_split_idx:]

    train_songs = {
        'artists': [d2['artists'][i] for i in train_idx],
        'titles': [d2['titles'][i] for i in train_idx],
        'lyrics': [d2['lyrics'][i] for i in train_idx],
        'genres': [d2['genres'][i] for i in train_idx]
    }
    valid_songs = {
        'artists': [d2['artists'][i] for i in valid_idx],
        'titles': [d2['titles'][i] for i in valid_idx],
        'lyrics': [d2['lyrics'][i] for i in valid_idx],
        'genres': [d2['genres'][i] for i in valid_idx]
    }
    test_songs = {
        'artists': [d2['artists'][i] for i in test_idx],
        'titles': [d2['titles'][i] for i in test_idx],
        'lyrics': [d2['lyrics'][i] for i in test_idx],
        'genres': [d2['genres'][i] for i in test_idx]
    }
    del d2

    print("Number of train songs:", len(train_idx))
    print("Number of train l.c. songs:", len(list(
        filter(lambda a: 'leonard' in a and 'cohen' in a, train_songs['artists'])
    )))
    print("Number of valid songs:", len(valid_idx))
    print("Number of valid l.c. songs:", len(list(
        filter(lambda a: 'leonard' in a and 'cohen' in a, valid_songs['artists'])
    )))
    print("Number of test  songs:", len(test_idx))
    print("Number of test l.c. songs:", len(list(
        filter(lambda a: 'leonard' in a and 'cohen' in a, test_songs['artists'])
    )))

    print("Saving to files...")
    write_songs_to_file(train_songs, 'train_songlyrics.json')
    write_songs_to_file(valid_songs, 'valid_songlyrics.json')
    write_songs_to_file(test_songs, 'test_songlyrics.json')
    print("done.")


if __name__ == '__main__':
    # -------
    # STEP 0:
    # -------
    # Define the list of bad words to filter out and the regular expressions to remove
    #

    # bad words to be removed:
    f = open('profanity_list.txt', 'r')
    BAD_WORDS = [w for w in f]
    f.close()

    # add escape characters
    for i in range(len(BAD_WORDS)):
        bw = BAD_WORDS[i]
        BAD_WORDS[i] = bw.replace('(', '\(').replace(')', '\)') \
            .replace('[', '\[').replace(']', '\]') \
            .replace('.', '\.').replace('*', '\*') \
            .replace('?', '\?').replace('+', '\+')

    BAD_WORDS = tuple(BAD_WORDS)
    print("will replace %d bad words by <unk>" % len(BAD_WORDS))

    # define regular expression that matches all occurrences of [...] & (...) & a number
    sq_brackets = re.compile(r"\[.*?\]")
    rd_brackets = re.compile(r"\(.*?\)")
    rp_number = re.compile(r"x?[0-9]\s")  # matches "x<a number> " with or without 'x'

    main()
