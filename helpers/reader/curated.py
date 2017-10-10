import rdflib
import glob


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


def text_length(path):
    with open(path) as f:
        cnt = len(f.read().split())
    return cnt