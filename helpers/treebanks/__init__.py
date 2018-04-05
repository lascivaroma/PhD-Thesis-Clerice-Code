from .xml import PerseidsXMLCorpus
from .conllu import ConlluTreebank


Harrington = PerseidsXMLCorpus(
    "data/raw/treebanks_xml/perseids-project_harrington_trees/harrington_trees-*/CITE_TREEBANK_XML/perseus/lattb/**/*.xml",
    name="Perseids Harrington Latin Treebank"
)


Proiel = ConlluTreebank(
    "data/raw/treebanks_conllu/UniversalDependencies_UD_Latin-PROIEL/UD_Latin-PROIEL-*/*.conllu",
    name="Proiel UD Treebanks"
)


Corpora = [
    Harrington,
    Proiel
]
