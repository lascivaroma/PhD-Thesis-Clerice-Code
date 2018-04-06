import lxml.etree
import collections
import os

from conllu import parse
from MyCapytain.common.reference import URN

from .base import TreebankCorpus
from ..printing import SUBSUBTASK_SEPARATOR, SUBTASK_SEPARATOR

docs = []


Conversion_table = {
    "Commentarii belli Gallici, Caes., Gall. ": "urn:cts:latinLit:phi0448.phi001.perseus-lat2:",
    "Epistulae ad Atticum, Book 1, letter ": "urn:cts:latinLit:phi0474.phi057.perseus-lat2:1.",
    "Epistulae ad Atticum, Book 2, letter ": "urn:cts:latinLit:phi0474.phi057.perseus-lat2:2.",
    "Epistulae ad Atticum, Book 3, letter ": "urn:cts:latinLit:phi0474.phi057.perseus-lat2:3.",
    "Epistulae ad Atticum, Book 4, letter ": "urn:cts:latinLit:phi0474.phi057.perseus-lat2:4.",
    "Epistulae ad Atticum, Book 5, letter ": "urn:cts:latinLit:phi0474.phi057.perseus-lat2:5.",
    "Epistulae ad Atticum, Book 6, letter ": "urn:cts:latinLit:phi0474.phi057.perseus-lat2:6.",
    "Epistulae ad Atticum, Book 7, letter ": "urn:cts:latinLit:phi0474.phi057.perseus-lat2:7.",
}


def conversion(doc_id):
    # Perseus TB
    if ".xml" in doc_id:
        prefix = "latinLit"
        if "tlg" in doc_id:
            prefix = "greekLit"

        doc_id = "urn:cts:{pref}:{name}".format(
            pref=prefix,
            name=doc_id.replace(".tb.xml", "").replace("@", ":").replace("lat1", "lat2")
        )
        return doc_id
    # Proiel
    if doc_id.startswith("Jerome's Vulgate") or doc_id.startswith("MATT_"):
        doc_id = "urn:cts:greekLit:tlg0031.tlg001.perseus-lat2"
        return doc_id
    for key, value in Conversion_table.items():
        new_doc_id = doc_id.replace(key, value)
        if new_doc_id != doc_id:
            return new_doc_id

    print("Not found in Conversion Table :" + doc_id)
    return doc_id


class ConlluTreebank(TreebankCorpus):
    def parse_sentences(self):
        """ Parse each conllu file """
        for file in self.files:
            with open(file) as f:
                sentences = f.read().split("\n\n")
                for sentence in sentences:
                    if not sentence:
                        continue

                    metadata = {
                        line.replace("#", "").strip().split(" = ")[0]: line.strip().split(" = ")[1]
                        for line in sentence.split("\n")
                        if line.startswith("#")
                    }

                    try:
                        tokens = [
                            tok
                            for tok in parse(sentence)[0]
                            if not self.remove or not self.remove.match(tok["form"])
                        ]

                        document_id = metadata.get("source", metadata.get("sent_id"))
                        document_id = URN(conversion(document_id))
                        document_id = document_id.upTo(URN.VERSION)

                        yield (
                            document_id,
                            tokens,
                            [tok["form"] for tok in tokens],
                            [tok["lemma"] for tok in tokens],
                            [tok["upostag"] for tok in tokens]
                        )
                    except Exception as E:
                        print(sentence)
                        raise E

    def parse(self):
        for doc, s, words, lemmas, postags in self.parse_sentences():
            self._words[doc] += words
            self._lemmas[doc] += lemmas
            for postag in postags:
                self._types[doc][postag] += 1