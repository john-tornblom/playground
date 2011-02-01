#!/bin/bash

find "${1%/}" -type f -a -name '*.mp3' | while read filename ; do
        title=$(id3info "$filename" | grep '^=== TIT2' | sed -e 's/.*: //g' | sed 's/\//_/g' | sed 's/ /_/g')
        artist=$(id3info "$filename" | grep '^=== TPE1' | sed -e 's/.*: //g' | sed 's/\//_/g' | sed 's/ /_/g')
        album=$(id3info "$filename"| grep '^=== TALB' | sed -e 's/.*: //g' | sed 's/\//_/g' | sed 's/ /_/g')
        tracknumber=$(id3info "$filename" | grep '^=== TRCK' | sed -e 's/.*: //g' | sed 's/\//_/g' | sed 's/ /_/g')

        if [ ${#tracknumber} = 1 ]; then
                tracknumber="0${tracknumber}"
        fi

        output="${2%/}/${artist}-${album}/${tracknumber}-${artist}-${title}.mp3"
        echo $output
        mkdir -p $(dirname $output)
        mv "$filename" "$output"
done

