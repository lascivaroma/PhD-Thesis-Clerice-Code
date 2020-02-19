from pprint import pprint
from glob import glob
from typing import Dict, List, Union, Tuple
import regex as re
import os.path as op
from Levenshtein import ratio
from lxml.builder import E as Builder
import lxml.etree as ET

from helpers.reader.capitains import transform
from MyCapytain.common.constants import Mimetypes
from MyCapytain.common.utils import parse
from MyCapytain.resources.texts.local.capitains.cts import CapitainsCtsText, CapitainsCtsPassage

LANG = "lat"
RAISE_ON_NO_CITATION = True
PATH_TSV = "./data/curated/corpus/base"
XML_FILES = "./data/raw/corpora/**/*.xml"


normalize_space = re.compile(r"\s+")

# Dictionary of filenames -> Path
_xmls: Dict[str, str] = {
    op.basename(path): path
    for path in glob(XML_FILES, recursive=True)
}


def get_text_object(ident: str) -> CapitainsCtsText:
    """ Given an identifier, gets a text
    """
    filename = ident.split(":")[-1]+".xml"
    current_file = _xmls.get(filename)
    if current_file:
        return CapitainsCtsText(resource=parse(current_file))
    else:
        raise Exception("% not found".format(ident))


def minimal(text: str, annotations: List[Dict[str, str]]) -> int:
    """ Get the minimal amount of tokens"""
    next_tokens = 1
    distance = .0
    current_ratio = ratio(text, " ".join([tok["form"] for tok in annotations[:next_tokens]]))
    while distance < current_ratio:
        next_tokens += 1
        distance = current_ratio
        current_ratio = ratio(text, " ".join([tok["form"] for tok in annotations[:next_tokens]]))
        if next_tokens > len(annotations):
            break
    return next_tokens - 1


def normalize_form(form: str) -> str:
    if form.startswith("-"):
        return form[1:]
    return form


def aligned(text: str, annotations: List[Dict[str, str]]) -> Tuple[
                                                             List[Union[str, Dict[str, str]]],
                                                             List[Dict[str, str]]
]:
    start_text = ""+text  # Make a copy for debugging
    minimal_diff_nb_tokens = minimal(text, annotations)
    # If we are not emptying
    if minimal_diff_nb_tokens != len(annotations):
        tokens, annotations = annotations[:minimal_diff_nb_tokens], annotations[minimal_diff_nb_tokens:]
    else:
        tokens = annotations
        annotations = []

    alignement = []

    while text and tokens:
        found = False

        # We search in the text the first token
        for match in re.finditer(pattern=normalize_form(tokens[0]["form"]), string=text):
            if not found:
                s, e = match.start(), match.end()
                found = True

        if found == False:
            pprint(alignement)
            print("Text [{}]".format(text))
            print(start_text)
            print("Tokens, ", " ".join([t["form"] for t in tokens]))
            print(tokens)
            raise Exception()

        # Otherwise, if the beginning of match is not 0, we have supplementary text
        if s != 0:
            alignement.append(text[:s])
        alignement.append(tokens.pop(0))
        text = text[e:]

    if tokens:
        print("Remaining tokens", tokens)
        print("Text", text)
        pprint(alignement)
        raise Exception("All tokens should be aligned !")

    if text:
        alignement.append(text)

    return alignement, annotations


texts = sorted(glob(op.join(PATH_TSV, "**", "*.tsv")) + glob(op.join(PATH_TSV, "**", ".tsv")), reverse=True)

def element_or_tail(str_or_dict: Union[str, Dict[str, str]]):
    """ Transforms an element as str or dict """
    if isinstance(str_or_dict, str):
        return str
    return Builder("token", str_or_dict["form"], **{key: val for key, val in str_or_dict.items() if key != "form"})


for text in texts:

    with open(text) as tsv_io:
        tsv = []
        header = []
        for line_no, line in enumerate(tsv_io.readlines()):
            line = line.strip()
            if line:
                if line_no == 0:
                    header = line.split("\t")
                else:
                    tsv.append(dict(list(zip(header, line.split("\t")))))

    # We get identifiers connected to the item
    text_ident = op.split(op.dirname(text))[-1]
    passage_ident = op.basename(text).replace(".tsv", "")
    root = None
    depth = 0
    if passage_ident:
        root = passage_ident
        depth = passage_ident.count(".") + 1
    # We get the text medata
    print(text_ident)
    text_obj = get_text_object(text_ident)
    # Get the citation System
    citation = text_obj.citation
    # Set-up the current level citation
    current_level = citation[depth - 1]

    # Retrieve the same passage in XML
    root_passage: CapitainsCtsPassage = text_obj.getTextualNode(subreference=passage_ident)
    # Compute the maximum depth we have
    remaining_depth = len(current_level) - depth

    parent = Builder("root", text_id=text_ident, n=str(root_passage.reference))

    # Iterate over the passage
    for child in root_passage.getReffs(level=-1):
        current = root_passage.getTextualNode(subreference=child)

        # Get plain text
        plain_text = normalize_space.sub(" ", transform(current.export(Mimetypes.PYTHON.ETREE))).strip()
        alignment, tsv = aligned(plain_text, annotations=tsv)

        print(ET.tostring(Builder("passage", n=str(child), *list(map(element_or_tail, alignment))), encoding=str))


    break