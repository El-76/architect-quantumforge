#!/bin/bash

cd `dirname $0`;

mkdir -p knowledge_base/

while read TITLE; do
    NAME=`echo -n "${TITLE}" | tr '"' "'"`

    echo -e "### ${TITLE}\n" > "knowledge_base/${NAME}.md"

    while true; do
        read LINE;

        echo "$LINE  " >> "knowledge_base/${NAME}.md"

        if [ -z `echo -n $LINE | tr -d ' '` ]; then
            break
        fi
    done
done
