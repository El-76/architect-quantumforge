#!/bin/bash

set -e

cd `dirname $0`

if [ ! -f ./d.zip ]; then
    curl -L https://archive.org/download/wikia_dump_20200214/d.zip -O
fi

unzip d.zip dozoryfandomcom-20200214-history.xml.7z
mkdir -p dump
7z e dozoryfandomcom-20200214-history.xml.7z -odump
python clean.py dump/dozoryfandomcom-20200214-history.xml
mkdir -p extracted-dump
wikiextractor dump/dozoryfandomcom-20200214.xml -o extracted-dump/ --processes 2 --json -b 0
find extracted-dump/ -type f | while read F; do jq -r '.title, .text' $F; echo; done | python replace.py > pseudo-wiki-draft.txt
