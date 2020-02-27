import sys
import os.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from glob import glob
from typing import Dict, List, Union, Tuple, Optional
import regex as re
import os.path as op
from lxml.builder import E as Builder
import lxml.etree as ET
import tqdm
from Bio import pairwise2

from helpers.reader.capitains import _transformer, _number, _hyphen
from MyCapytain.common.constants import Mimetypes
from MyCapytain.common.utils import parse
from MyCapytain.resources.texts.local.capitains.cts import CapitainsCtsText, CapitainsCtsPassage
from unidecode import unidecode


class AlignmentError(Exception):
    """ Error of alignment """

RATIO_SIZE_TOKENS = 3
MAX_SIZE_PASSAGE = 75
LANG = "lat"
RAISE_ON_NO_CITATION = True
PATH_TSV = "./data/curated/corpus/pie"
XML_FILES = "./data/raw/corpora/**/*.xml"
GAP_PAIRWISE = "£££"
debug = False
IGNORED_ANNOTATIONS = ["token"]
HYPHEN_REPLACE = "__hyphen__"

normalize_space = re.compile(r"\s+")
ending_hyphen = re.compile(r"-\s*$")

# Dictionary of filenames -> Path
_xmls: Dict[str, str] = {
    op.basename(path): path
    for path in glob(XML_FILES, recursive=True)
}


has_word = re.compile(r".*\w+.*")


from pie_extended.models.lasla.tokenizer import LatMemorizingTokenizer
latin_tokenizer = LatMemorizingTokenizer()


def tokenizer(string: str, _tokenizer=latin_tokenizer._real_word_tokenizer) -> List[str]:
    return _tokenizer(string)


def get_text_object(ident: str) -> CapitainsCtsText:
    """ Given an identifier, gets a text from Capitains
    """
    filename = ident.split(":")[-1]+".xml"
    current_file = _xmls.get(filename)
    if current_file:
        return CapitainsCtsText(resource=parse(current_file))
    else:
        raise Exception("% not found".format(ident))


def transform(resource):
    return unidecode(
        _number.sub(
            "",
            _hyphen.sub(
                "",
                LatMemorizingTokenizer.re_add_space_around_punct.sub(
                    r" \g<2> ",
                    ending_hyphen.sub(
                        HYPHEN_REPLACE,
                        normalize_space.sub(" ", str(_transformer(resource)))
                    )
                )
            ).
            replace("AUG ", "Augustus").
            replace("/", "")
        )
    )


def get_plain_text(current):
    return transform(current.export(Mimetypes.PYTHON.ETREE)).strip()


def biggest_gap_at_the_end(sequence: List[str]):
    """

    :param sequence:
    :return:

    >>> biggest_gap_at_the_end([",", "£££", ",", "£££", ",", "£££", "£££", "£££", "£££", "£££", "£££"])
    6
    """
    for i, el in enumerate(sequence[::-1]):
        if el != GAP_PAIRWISE:
            return i
    return i


def get_best_alignement(alignements: List[Tuple[List[str], List[str], float, int, int]]) -> Tuple[int, int]:
    """ Get the alignment with the smallest gap

    :param alignements:
    :return: start, end
    """
    biggest = 0
    _best = 0

    for index, align in enumerate(alignements):
        from_pie, from_text, *_ = align
        curr = biggest_gap_at_the_end(from_text)
        if curr > biggest:
            biggest = curr
            _best = index

    #if _best == 0:
    #    # We might want to take the one with the less replacement in pie
    #    print([score for _, _, score, *_ in alignements])
    #    print(index)
    #    print(from_text)
    #    print(from_pie)
    return biggest, _best


def map_tokens(aligned_pie: List[str]) -> List[int]:
    """ Given a list of string, returns a list of index
    that represent items without gap
    
    :param aligned_pie: 
    :return: List of index to align
    """
    pas = 0
    out = []
    for tok in aligned_pie:
        if tok == GAP_PAIRWISE:
            out.append(None)
        else:
            out.append(pas)
            pas += 1
    return out


def get_tsv_annotations(text) -> List[Dict[str, str]]:
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
    return tsv


def align_elements_and_write(
        passage_identifier: str,
        annotations_tokens: List[str], annotations: List[Dict[str, str]],
        tokenized: List[str], io_output
):
    """

    :param passage_identifier: Passage identifier to write in the @id attr
    :param annotations_tokens: Tokens from the TSV
    :param annotations: Full annotations from the CSV
    :param tokenized: Tokenized text
    :param io_output: File in which we can write
    :return: annotation, annotations_tokens
    """
    # We make the size of the annotation maximum n time the input text
    annotations_taken_into_account = annotations_tokens[:int(RATIO_SIZE_TOKENS*len(tokenized))]
    # We get alignments from the pairwise where we add penalties for gaps
    #   Use the constant PAIRWISE to align things back
    #   (Honestly thinking should get a way to export raw texts from Capitains including the passages id)
    alignments = pairwise2.align.localms(
        annotations_taken_into_account,
        tokenized,
        10,  # 5 points for identical character
        0,  # -1 point for non-identical character
        -2,  # -1 for opening a gap in annotation tokens
        -1.9,  # -2 for extending a gap in annotations tokens
        #-3,  # -1 for opening a gap in input text  (There should be no gap in it)
        #-2,  # -2 for extending a gap in input text
        gap_char=[GAP_PAIRWISE],
    )

    # Once we get it, we try to get the best alignement: this function returns the index (end_index)
    #  at which we should stop aligning pie data (longer than text normally)
    #  as well as the index of the alignment containing this best index. Best alignement is computed
    #  so that the alignement ends as far as possible from the end of the text
    if not alignments:
        raise AlignmentError("No alignments found")

    end_index, best = get_best_alignement(alignments)
    aligned_pie, aligned_text, *_ = alignments[best]
    if debug:
        print(" === Alignment === ")
        print("Al Pie ", aligned_pie)
        print("Al Txt ", aligned_text)
        print("Maped  ", annotations_tokens[:-end_index])
        print("Tokens ", tokenized)
        print("Pie Id ", )

    # For each tokens from our input text, we get an equivalent ID
    #   where this ID is the index of a token in our tsv OR None.
    #   If it's none, our token comes from less cleaning and we decide we keep it.
    tags = {}
    for token, pie_index in zip(tokenized, map_tokens(aligned_pie)):
        attrs, form = {}, token
        if pie_index is not None:
            attrs.update({
                attr: val
                for attr, val in annotations[pie_index].items()
                if attr not in IGNORED_ANNOTATIONS
            })
        io_output.write(
            "    " +
            ET.tostring(
                  Builder(
                      "token",
                      form,
                      id=passage_identifier,
                      **attrs
                  ),
                  encoding=str,
                  pretty_print=True
              )
        )
    # Now that we have aligned, we move tsv and annotations_as_word till the end
    #  Although, if end index is 0, we do not have any more annotations
    if end_index == 0 and len(annotations_taken_into_account) == annotations_tokens:
        return [], []

    real_end_index = - end_index - len(annotations_taken_into_account)
    annotations_tokens, annotations = annotations_tokens[real_end_index:], annotations[real_end_index:]
    return annotations, annotations_tokens


def smaller_passages(l: List[str], n: int):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


if __name__ == "__main__":
    texts = sorted(glob(op.join(PATH_TSV, "**", "*.tsv")) + glob(op.join(PATH_TSV, "**", ".tsv")), reverse=True)
    for text in texts:
        # We get identifiers connected to the item
        text_ident = op.split(op.dirname(text))[-1]
        passage_ident = op.basename(text).replace(".tsv", "")
        output_file = open("aligned_texts/"+text_ident+"_"+passage_ident+".xml", "w")

        root = None
        depth = 0
        if passage_ident:
            root = passage_ident
            depth = passage_ident.count(".") + 1

        print(text_ident, passage_ident)

        # We get the text medata
        text_obj = get_text_object(text_ident)
        # Get the citation System
        citation = text_obj.citation
        # Set-up the current level citation
        current_level = citation[depth - 1]

        # Retrieve the same passage in XML
        root_passage: CapitainsCtsPassage = text_obj.getTextualNode(subreference=passage_ident)
        # Compute the maximum depth we have
        remaining_depth = len(current_level) - depth

        # To align with the text later, we need to get the annotations as well as its representation
        #   as list of words
        tsv = get_tsv_annotations(text)
        annotations_as_words = [anno["token"] for anno in tsv]
        output_file.write("<root id=\""+text_ident+"\">\n")

        # Two situations:
        #  1. We have levels below, we need to retrieve them
        #  2. We have the lowest level already
        # Iterate over the passage
        try:
            if remaining_depth == 0:
                tokenized = tokenizer(get_plain_text(root_passage))
                tsv, annotations_as_words = align_elements_and_write(
                    passage_identifier=str(passage_ident),
                    annotations_tokens=annotations_as_words,
                    annotations=tsv,
                    io_output=output_file,
                    tokenized=tokenized
                )
            else:
                passages = []
                child_ids = []
                # Firt we retrieve the text of the passage as tokenized input
                print("   -> Multiple children from the root passage: reading")

                for child in root_passage.getReffs(level=remaining_depth):
                    # We get the text passage
                    current = root_passage.getTextualNode(subreference=child)
                    for small_current in smaller_passages(tokenizer(get_plain_text(current)), MAX_SIZE_PASSAGE):
                        passages.append(small_current)
                        child_ids.append(str(child))

                print("   -> Multiple children from the root passage: aligning\n")
                for id_passage, (tokenized_passage, passage_id) in tqdm.tqdm(enumerate(zip(passages, child_ids)),
                                                                             total=len(child_ids)):
                    # At transformation time, we replace ending hyphen glued to word with HYPHEN_REPLACE value
                    #   Which we can now replace with the next passage token
                    if tokenized_passage[-1].endswith(HYPHEN_REPLACE):
                        tokenized_passage[-1] = tokenized_passage[-1].replace(
                            HYPHEN_REPLACE, passages[id_passage+1].pop(0)
                        )

                    if not tsv:
                        print(tokenized_passage)
                        print(tsv)
                        raise AlignmentError("We got text but no more annotations !")

                    tsv, annotations_as_words = align_elements_and_write(
                        passage_identifier=passage_id,
                        annotations_tokens=annotations_as_words,
                        annotations=tsv,
                        io_output=output_file,
                        tokenized=tokenized_passage
                    )

            if tsv:
                # Should have been taken care of no ?
                print("Remaining TSV ! ", len(tsv))
        except AlignmentError as E:
            print(E)
            print("Error on {} from {}".format(passage_ident, text_ident))
        output_file.write("\n</root>")
        output_file.close()
