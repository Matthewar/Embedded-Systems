#!/bin/bash

for i in *.py; do
	ampy -p $1 -b 115200 put $i
done

ampy -p $1 -b 115200 reset
