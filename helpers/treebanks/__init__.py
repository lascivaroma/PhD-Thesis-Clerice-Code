from .xml import PerseidsXMLCorpus

Harrington = PerseidsXMLCorpus(
    "data/raw/treebanks_xml/perseids-project_harrington_trees/harrington_trees-*/CITE_TREEBANK_XML/perseus/lattb/**/*.xml",
    name="Perseids Harrington Latin Treebank"
)


Corpora = [
    Harrington
]
