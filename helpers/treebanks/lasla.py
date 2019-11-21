import os
import tqdm

from csv import DictReader, reader
from helpers.treebanks.base import TreebankCorpus
from collections import Counter

class LaslaCorpus(TreebankCorpus):

    def __init__(self, files, name, equivalency_table="data/raw/lasla.tsv", remove=None):
        super(LaslaCorpus, self).__init__(files, name, remove)
        with open(equivalency_table) as f:
            self.equivalency_table = {
                row[0].replace(".BPN", ".tsv"): row[1]
                for row in reader(f, delimiter="\t")
            }

    def parse_sentences(self):
        for file in tqdm.tqdm(self.files):
            filename = os.path.basename(file)
            urn = self.equivalency_table[filename]

            with open(file) as f:
                words, lemmas, postags, tags = [], [], [], []
                for line in DictReader(f, delimiter="\t"):
                    if len(line) and len(line["form"]):
                        words.append(line["form"])
                        lemmas.append(line["lemma"])
                        tags.append({"lemma": line["lemma"], "form": line["form"]})
                        postags.append(line["pos"])
                    else:
                        yield urn, tags, words, lemmas, postags
                        words, lemmas, postags, morph = [], [], [], []
                yield urn, tags, words, lemmas, postags

    def parse(self):
        for doc, s, words, lemmas, postags in self.parse_sentences():
            self._words[doc].extend(words)
            self._lemmas[doc].extend(lemmas)
            for tag in s:
                self._lemma_forms[tag.get("lemma")].add(tag.get("form"))

            self._types[doc].update(Counter(postags))

