import rdflib
import glob
from helpers.cache import memoize


def get_graph(src="data/curated/inventory.xml.turtle"):
    g = rdflib.Graph()
    g.parse(src, format="n3")
    return g


def get_texts(src="data/curated/corpus/generic"):
    """ Return path and id of texts

    :param src:
    :return:
    """
    texts = glob.glob(src+"/**/*.txt") + glob.glob(src+"/**/.txt")
    return [(text, text.replace(src+"/", "").split("/")[0]) for text in texts]


def get_text_length(path):
    with open(path) as f:
        cnt = len(f.read().split())
    return cnt


@memoize
def get_text_length_dict(texts):
    """ Get a dictionary of passages length

    :param texts: Texts to investigate as a list of path and text identifiers
    :return: Dictionary where the key is the text identifier and the value is a list of passage length
    """
    texts_dicts = {text_id: [] for path, text_id in texts}
    for text, text_id in texts:
        texts_dicts[text_id].append(get_text_length(text))
    return texts_dicts
