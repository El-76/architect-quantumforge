#!/bin/bash

cd `dirname $0`;

mkdir -p knowledge_base/

rm -rf knowledge_base/*

N=1

while read TITLE; do
    NAME=`echo -n "${TITLE}" | tr '"' "'"`

    echo "${N}" > "knowledge_base/${NAME}.txt"

    echo "${TITLE}" >> "knowledge_base/${NAME}.txt"

    while true; do
        read LINE;

        echo "$LINE" >> "knowledge_base/${NAME}.txt"

        if [ -z `echo -n $LINE | tr -d ' '` ]; then
            break
        fi
    done

    N=$(( N + 1 ))
done
