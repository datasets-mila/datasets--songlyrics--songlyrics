#!/bin/bash

# this script is meant to be used with 'datalad run'

# Add 'fast' bin to path
export PATH="bin:${PATH}"

fast learnbpe 40000 gpt/train_songlyrics.gpt.txt > gpt/train_songlyrics.gpt.txt.BPE_40000.codes

fast applybpe gpt/train_songlyrics.gpt.txt.40000 gpt/train_songlyrics.gpt.txt gpt/train_songlyrics.gpt.txt.BPE_40000.codes
fast applybpe gpt/valid_songlyrics.gpt.txt.40000 gpt/valid_songlyrics.gpt.txt gpt/train_songlyrics.gpt.txt.BPE_40000.codes
fast applybpe gpt/test_songlyrics.gpt.txt.40000 gpt/test_songlyrics.gpt.txt gpt/train_songlyrics.gpt.txt.BPE_40000.codes
