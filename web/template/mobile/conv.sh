#!/bin/bash

read filename
while [ -f $filename ]
do
    echo "converting gbk --> utf8 : $filename" 
    iconv -f gbk -t utf8 $filename > /tmp/tmfile && cp /tmp/tmfile $filename
    read filename
done
