#!/bin/bash

[ $(date +%H) -lt 1 ] && exit 2

sd=.
[ -n "$1" ] && sd="$1"
exfolder=$(date '+%Y-%m-%d')
for folder in $(find "$sd" -name '2018-??-??' -type d); do
    sfolder="${folder##*/}"
    if [ "$sfolder" == "$exfolder" ]; then
        #echo "$folder"
        continue
    fi

    find "$folder" -name '*.txt' -exec gzip -v {} \;
done
