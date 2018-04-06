from .xml import PerseidsXMLCorpus
from .conllu import ConlluTreebank
from .utils import flatten_doc_dict, doc_token_dict_sum


Harrington = PerseidsXMLCorpus(
    "data/raw/treebanks_xml/perseids-project_harrington_trees/harrington_trees-*/CITE_TREEBANK_XML/perseus/lattb/**/*.xml",
    name="Perseids Harrington Latin Treebank"
)


Harrington_filtered = PerseidsXMLCorpus(
    "data/raw/treebanks_xml/perseids-project_harrington_trees/harrington_trees-*/CITE_TREEBANK_XML/perseus/lattb/**/*.xml",
    name="Perseids Harrington Latin Treebank (No Punctuation)",
    remove="^\W+$"
)


Proiel = ConlluTreebank(
    "data/raw/treebanks_conllu/UniversalDependencies_UD_Latin-PROIEL/UD_Latin-PROIEL-*/*.conllu",
    name="Proiel UD Treebanks"
)


Proiel_filtered = ConlluTreebank(
    "data/raw/treebanks_conllu/UniversalDependencies_UD_Latin-PROIEL/UD_Latin-PROIEL-*/*.conllu",
    name="Proiel UD Treebanks (No Punctuation)",
    remove="^\W+$"
)


Perseus = ConlluTreebank(
    "data/raw/treebanks_conllu/UniversalDependencies_UD_Latin-Perseus/UD_Latin-Perseus-*/*.conllu",
    name="Perseus UD Treebanks"
)
Perseus_filtered = ConlluTreebank(
    "data/raw/treebanks_conllu/UniversalDependencies_UD_Latin-Perseus/UD_Latin-Perseus-*/*.conllu",
    name="Perseus UD Treebanks (No Punctuation)",
    remove="^\W+$"
)


Corpora = [
    Harrington,
    Proiel,
    Perseus
]

Filtered_Corpora = [
    Harrington_filtered,
    Proiel_filtered,
    Perseus_filtered
]
