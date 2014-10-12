#!/bin/bash

if [ ! -d Parsed ]; then
  mkdir Parsed
fi

for f in `ls *.txt`; do
  echo "Parsing $f."
  python script_parser.py $f
  mkdir "Parsed_$f"
  cp Parsed/* Parsed_$f
  rm Parsed/*.txt
done
