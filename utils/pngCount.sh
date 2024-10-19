#!/bin/bash

if [[ $# == 2 && $1 == "-s" ]]; then
    find $2 -type f -name "*.png" | cut -d "/" -f 3 | uniq -c | sort -n
else
    echo "Wrong format! Use -s flag to determine source directory of png files"
    echo "Example: ./pngCount.sh -s ./dataset/"
fi
