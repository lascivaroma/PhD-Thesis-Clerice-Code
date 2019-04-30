import lxml.etree
import collections
import os

from MyCapytain.common.reference import URN
from csv import reader
from helpers.treebanks.base import TreebankCorpus
from helpers.printing import SUBSUBTASK_SEPARATOR, SUBTASK_SEPARATOR


class LaslaCorpus(TreebankCorpus):

    def __init__(self, files, name, equivalency_table="data/raw/lasla.tsv", remove=None):
        super(LaslaCorpus, self).__init__(files, name, remove)
        with open(equivalency_table) as f:
            self.equivalency_table = {
                row[0].replace(".BPN", ".tsv"): row[1]
                for row in reader(f, delimiter="\t")
            }

    def parse_sentences(self):
        for file in self.files:
            filename = os.path.basename(file)
            urn = self.equivalency_table[filename]
            with open(file) as f:

                words, lemmas, postags, tags = [], [], [], []
                for line in reader(f, delimiter="\t"):
                    if len(line):
                        if line[0] == "form":
                            continue
                        words.append(line[0])
                        lemmas.append(line[1])
                        tags.append({"lemma": lemmas[-1], "form": words[-1]})
                        postags.append(line[3])
                    else:
                        yield urn, tags, words, lemmas, postags
                        words, lemmas, postags, morph = [], [], [], []
                yield urn, tags, words, lemmas, postags

    def parse(self):
        for doc, s, words, lemmas, postags in self.parse_sentences():
            self._words[doc] += words
            self._lemmas[doc] += lemmas
            for tag in s:
                self._lemma_forms[tag.get("lemma")].add(tag.get("form"))
            for postag in postags:
                try:
                    self._types[doc][postag] += 1
                except:
                    # Pass
                    continue

