#!/bin/bash

find "${1%/}" -type f -a -name '*.flac' | while read filename ; do
        metaflac "$filename" --export-tags-to=/tmp/tmp.txt --no-utf8-convert
        album=$(awk 'BEGIN {FS="="; IGNORECASE=1} /^ALBUM=/{print $2}' /tmp/tmp.txt | sed 's/\//_/g' | sed 's/ /_/g')
        artist=$(awk 'BEGIN {FS="="; IGNORECASE=1} /^ARTIST/{print $2}' /tmp/tmp.txt | sed 's/\//_/g' | sed 's/ /_/g')
        title=$(awk 'BEGIN {FS="="; IGNORECASE=1} /^TITLE/{print $2}' /tmp/tmp.txt | sed 's/\//_/g' | sed 's/ /_/g')
        tracknumber=$(awk 'BEGIN {FS="="; IGNORECASE=1} /^TRACKNUMBER/{print $2}' /tmp/tmp.txt | sed 's/\//_/g' | sed 's/ /_/g')
        rm /tmp/tmp.txt

        if [ ${#tracknumber} = 1 ]; then
                tracknumber="0${tracknumber}"
        fi

        output="${2%/}/${artist}-${album}/${tracknumber}-${artist}-${title}.flac"
        echo $output
        mkdir -p $(dirname $output)
        mv "$filename" "$output"
done
