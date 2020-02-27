#!/bin/bash
mkdir -p data/cqp/data
cwb-encode -c utf8 -d data/cqp/data -F ./corpus_cqp/ -R data/cqp/latin -xsB -S text:0+id -S s:0+id -P pos -P lemma -P morph
cwb-makeall -r data/cqp/ -V latin
cwb-huffcode -r data/cqp -A latin
cwb-compress-rdx -A -r data/cqp latin
