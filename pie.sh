#!/bin/bash
for filename in data/curated/corpus/generic/**/*.txt; do
   these_env/bin/pie tag data/models/latin.tar "$filename" --device cuda
done
