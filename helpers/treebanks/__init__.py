from .xml_corpora import PerseidsXMLCorpus
from .conll import ConlluTreebank
from .lasla import LaslaCorpus
from .utils import flatten_doc_dict, doc_token_dict_sum, distribution, idict


Harrington = PerseidsXMLCorpus(
    "data/raw/treebanks_xml/perseids-project_harrington_trees/harrington_trees-*/CITE_TREEBANK_XML/perseus/lattb/**/*.xml",
    name="Harrington Latin"
)


Harrington_filtered = PerseidsXMLCorpus(
    "data/raw/treebanks_xml/perseids-project_harrington_trees/harrington_trees-*/CITE_TREEBANK_XML/perseus/lattb/**/*.xml",
    name="Harrington Latin (NoPunc)",
    remove="^\W+$"
)


Proiel = ConlluTreebank(
    "data/raw/treebanks_conllu/UniversalDependencies_UD_Latin-PROIEL/UD_Latin-PROIEL-*/*.conllu",
    name="Proiel"
)


Proiel_filtered = ConlluTreebank(
    "data/raw/treebanks_conllu/UniversalDependencies_UD_Latin-PROIEL/UD_Latin-PROIEL-*/*.conllu",
    name="Proiel (NoPunc)",
    remove="^\W+$"
)


Perseus = ConlluTreebank(
    "data/raw/treebanks_conllu/UniversalDependencies_UD_Latin-Perseus/UD_Latin-Perseus-*/*.conllu",
    name="Perseus UD"
)
Perseus_filtered = ConlluTreebank(
    "data/raw/treebanks_conllu/UniversalDependencies_UD_Latin-Perseus/UD_Latin-Perseus-*/*.conllu",
    name="Perseus UD (NoPunc)",
    remove="^\W+$"
)

LASLA = LaslaCorpus("/home/thibault/dev/LASLA/output/*.tsv", "Corpus Lasla 2018")
LASLA2 = LaslaCorpus("/home/thibault/dev/LASLA/output/*.tsv", "Corpus Lasla 2018")

Corpora = [
    Harrington,
    Proiel,
    Perseus,
    LASLA
]

Filtered_Corpora = [
    Harrington_filtered,
    Proiel_filtered,
    Perseus_filtered,
    LASLA2
]
