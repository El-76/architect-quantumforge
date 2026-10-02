#!/bin/bash

cd "$(dirname "$0")"

. ../secret.envsh

python bot.py "$@"
