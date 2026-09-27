#!/bin/bash

if [ -f /var/run/practicum7/upload ]; then
    exit 0
fi

touch /var/run/practicum7/upload

cd $( dirname $0 )

export PYENV_ROOT="$HOME/.pyenv"

[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"

eval "$(pyenv init -)"

python /opt/practicum7/bin/index_or_query.py --wiki /var/lib/practicum7/knowledge_base --hashes /var/lib/practicum7/hashes/local.txt >> /var/log/practicum7/upload.log 2>&1

rm -f /var/run/practicum7/upload
