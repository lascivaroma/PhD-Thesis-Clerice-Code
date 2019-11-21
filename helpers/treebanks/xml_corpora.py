import lxml.etree
import collections
import os
from MyCapytain.common.reference import URN

from .base import TreebankCorpus
from ..printing import SUBSUBTASK_SEPARATOR, SUBTASK_SEPARATOR

import logging

# Dictionary of files without document IDs
Known_errors = {
    "lattb.6202.1.tb.xml": "urn:cts:latinLit:phi0472.phi001.perseus-lat2",  #:6.1",
    "lattb.5984.1.tb.xml": "urn:cts:latinLit:phi0959.phi006.perseus-lat2",  #:3.44",
    "lattb.6392.1.tb.xml": "urn:cts:latinLit:phi0959.phi006.perseus-lat2",  #:3.44",
    "lattb.6248.1.tb.xml": "urn:cts:latinLit:phi0959.phi006.perseus-lat2",  #:3.44",
    "lattb.5758.1.tb.xml": "urn:cts:latinLit:phi0959.phi001.perseus-lat2",  #:1.1.1",
    "lattb.6282.1.tb.xml": "urn:cts:latinLit:phi0959.phi001.perseus-lat2",  #:1.ep.1",
    "lattb.6561.1.tb.xml": "urn:cts:latinLit:phi0959.phi001.perseus-lat2",  #:1.1.1",
    "lattb.5764.1.tb.xml": "urn:cts:latinLit:phi0959.phi001.perseus-lat2",  #:1.4.1",
    "lattb.6946.1.tb.xml": "urn:cts:latinLit:phi0959.phi001.perseus-lat2",  #:1.12.1",
    #    "lattb.4321.1.tb.xml": Missing document_id on last nodes
    #    "lattb.5608.1.tb.xml": Missing document_id on last nodes
    #    "lattb.6043.1.tb.xml": Missing document_id on last nodes
}


Keys_mapping = {
    "1.384-387": "urn:cts:latinLit:phi0959.phi006.perseus-lat2",
    "Ovid. Met": "urn:cts:latinLit:phi0959.phi001.perseus-lat2",
    "http://perseids.org/annotsrc/urn:cts:latinLit:phi0474.phi024.perseus-lat1": "urn:cts:latinLit:"
                                                                                 "phi0474.phi024.perseus-lat1"
}


_CONLL_LA_CONV_DICT = {
    "a": "ADJ",
    "c": "CCONJ",
    "d": "ADV",
    "e": "INTJ",
    "g": "PART",
    "i": "INTJ",
    "l": "DET",
    "m": "NUM",
    "n": "NOUN",
    "p": "PRON",
    "r": "ADP",
    "t": "VERB",
    "u": "PUNCT",
    "v": "VERB",
    "x": "X"
}


class PerseidsXMLCorpus(TreebankCorpus):

    def parse_sentences(self):
        data = collections.defaultdict(list)
        said_it_was_a_duplicate = []
        for file in self.files:
            filename = os.path.basename(file)
            with open(file) as f:
                xml = lxml.etree.parse(f)
                sentences = xml.xpath("//sentence")
                document_id = None
                for sentence in sentences:
                    # The "or" allows to fallback on last document ID
                    document_id = sentence.get("document_id") or document_id

                    # If we do not have a Document ID, we check in a curated list
                    if not document_id:
                        document_id = Known_errors.get(filename, None)

                    # If we do not have it, we raise an error to curate errors
                    if not document_id:
                        print(filename)
                        raise Exception

                    # We check that the document id has no mapping
                    document_id = Keys_mapping.get(document_id, document_id)
                    document_id = URN(document_id)
                    document_id = str(document_id.upTo(URN.VERSION))

                    tags = [
                        tag
                        for tag in sentence.xpath(".//word")
                        if (not self.remove or not self.remove.match(tag.get("form"))) and
                           tag.get("lemma")
                    ]

                    words = [tag.get("form") for tag in tags]
                    lemmas = [tag.get("lemma") for tag in tags]
                    postags = [tag.get("postag") for tag in tags]
                    joined_words = " ".join(words)

                    if joined_words not in data[document_id]:
                        yield document_id.replace("lat1", "lat2"), tags, words, lemmas, postags
                        data[document_id].append(joined_words)
                    else:
                        if filename not in said_it_was_a_duplicate:
                            logging.info(SUBTASK_SEPARATOR + filename + " is a duplicate treebank")
                            said_it_was_a_duplicate.append(filename)

        logging.info("{}/{} files containing duplicate sentences".format(
            len(said_it_was_a_duplicate),
            len(self.files)
        ))

    def parse(self):
        for doc, s, words, lemmas, postags in self.parse_sentences():
            self._words[doc] += words
            self._lemmas[doc] += lemmas
            for tag in s:
                self._lemma_forms[tag.get("lemma")].add(tag.get("form"))
            for postag in postags:
                try:
                    self._types[doc][_CONLL_LA_CONV_DICT.get(postag[0], postag[0])] += 1
                except:
                    # Pass
                    continue


