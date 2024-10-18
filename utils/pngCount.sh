#!/bin/bash

find $2 -type f -name "*.png" | cut -d "/" -f 3 | uniq -c | sort -n