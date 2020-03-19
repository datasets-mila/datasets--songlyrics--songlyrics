# Data processing performed

### STEP 0 : Raw lyrics files downloaded from Kaggle

- kaggle_artimous_songlyrics1.csv
- kaggle_artimous_songlyrics2.csv


- kaggle_gyani95_songlyrics.csv


- kaggle_mousehead_songlyrics.csv

### STEP 1 : Organize knowledge into .json files & merge all the files into train / valid / test splits

python script to run : `python convert_lyrics_to_json_splits.py`

this will:

- create .json files for all raw lyrics files (.csv)
- merge them and remove duplicate lyrics
- shuffle and create an 80/10/10 split for train/valid/test sets
- store each songs in their respective `{train | valid | test}_songlyrics.json` file

### STEP 2 : Additional processing for GPT

python script to run : `python prepare_for_gpt.py`

this will:
- read each `{train | valid | test}_songlyrics.json` file and
create a `{train | valid | test}_songlyrics.gpt.txt` file containing song lyrics, artist, title, and genre
all in one line.
- lyrics are splitted by token using nltk word tokenizer
- tokens within the same sentence are reversed because we want to train to generate lines from last to first token

here is an example:
`<GENRE> hip_hop <ARTIST> benefit <TITLE> a page in hip hop s diary
<LYRICS> <END-OF-LINE> me left and Gone <END-OF-LINE> low mighty ' feelin 'm I And
<END-OF-LINE> depressed me has events of state current The <END-OF-LINE> best the by accessed be used I
<...> <END-OF-SONG>`

### STEP 3 : BPE

git clone and compile https://github.com/glample/fastBPE

then run the following commands to get the BPE codes and apply tem on all the files:
````bash
./fast learnbpe 40000 [DATA_PATH]/train_songlyrics.gpt.txt > [DATA_PATH]/train_songlyrics.gpt.txt.BPE_40000.codes

./fast applybpe [DATA_PATH]/train_songlyrics.gpt.txt.40000 [DATA_PATH]/train_songlyrics.gpt.txt [DATA_PATH]/train_songlyrics.gpt.txt.BPE_40000.codes
./fast applybpe [DATA_PATH]/valid_songlyrics.gpt.txt.40000 [DATA_PATH]/valid_songlyrics.gpt.txt [DATA_PATH]/train_songlyrics.gpt.txt.BPE_40000.codes
./fast applybpe [DATA_PATH]/test_songlyrics.gpt.txt.40000 [DATA_PATH]/test_songlyrics.gpt.txt [DATA_PATH]/train_songlyrics.gpt.txt.BPE_40000.codes
````

### NOTE:

Since we **first** reversed the tokens and **then** performed BPE,
when generating sentences the following will need to be done **in order**:
- (1) remove all occurences of `@@` + `[space]` 
- (2) reverse the tokens from the same line (ie: everything before each `<END-OF-LINE>`)
