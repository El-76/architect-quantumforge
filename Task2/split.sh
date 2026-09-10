#!/bin/bash

cd `dirname $0`;

mkdir -p knowledge_base/

while read TITLE; do
    echo -e "### ${TITLE}\n" > "knowledge_base/${TITLE}.md"

    while true; do
        read LINE;

        echo "$LINE" >> "knowledge_base/${TITLE}.md"

        if [ -z `echo -n $LINE | tr -d ' '` ]; then
            break
        fi
    done
done
