import lxml.etree
import collections
import os
import statistics
from MyCapytain.common.reference import URN

from .base import TreebankCorpus
from ..printing import SUBSUBTASK_SEPARATOR, SUBTASK_SEPARATOR

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

                    words = " ".join(sentence.xpath(".//word/@form"))
                    if words not in data[document_id]:
                        yield document_id.replace("lat1", "lat2"), sentence, words, " ".join(sentence.xpath(".//word/@lemma"))
                        data[document_id].append(words)
                    else:
                        if filename not in said_it_was_a_duplicate:
                            print(SUBSUBTASK_SEPARATOR + filename + " is a duplicate treebank")
                            said_it_was_a_duplicate.append(filename)

        print(SUBTASK_SEPARATOR + " {}/{} files containing duplicate sentences".format(
            len(said_it_was_a_duplicate),
            len(self.files)
        ))

    def parse(self):
        for doc, s, words, lemmas in self.parse_sentences():
            self._words[doc] += words.split()
            self._lemmas[doc] += lemmas.split()
            for postag in s.xpath(".//@postag"):
                try:
                    self._types[doc][postag[0]] += 1
                except:
                    # Pass
                    continue

