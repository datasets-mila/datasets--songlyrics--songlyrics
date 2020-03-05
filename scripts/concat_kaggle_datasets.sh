#!/bin/bash

# This script is meant to be used with the command 'datalad run'

pip install -r scripts/requirements_concat_kaggle_datasets.txt
ERR=$?
if [ $ERR -ne 0 ]; then
   echo "Failed to install requirements: pip install: $ERR"
   exit $ERR
fi

datalad install -s ../songlyrics_artimous
datalad install -s ../songlyrics_gyani95
datalad install -s ../songlyrics_mousehead

datalad get songlyrics_*/*.zip

mkdir -p extract

jug status -- scripts/extract.py "songlyrics_*/*.zip" --output "extract/"
jug execute -- scripts/extract.py "songlyrics_*/*.zip" --output "extract/" &>> extract.out

export NLTK_DATA=./nltk_data
mkdir -p $NLTK_DATA

python scripts/concat_kaggle_datasets.py

# Clean up

rm -rf nltk_data/
datalad remove songlyrics_*/
