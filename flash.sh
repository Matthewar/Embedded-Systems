#!/bin/bash

mkdir tmp
for i in *.py; do
   sed -e "s/\s*#.*$//;/^\s*$/d" $i > tmp/$i
done
cd tmp
for i in *.py; do
   ampy -p $1 -b 115200 put $i
done
cd ..
rm tmp -r

ampy -p $1 -b 115200 reset
