import rdflib
import glob
from helpers.cache import memoize
import os

def _local_path(path):
    return os.path.join(os.path.dirname(__file__), os.path.basename(path))


def get_graph(src=_local_path(_local_path("data/curated/inventory.xml.turtle"))):
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
def get_passage_dict(texts):
    """ Get a dictionary of texts length

    :param texts: Texts to investigate as a list of path and text identifiers
    :return: Dictionary where the key is the text identifier and the value is a list of passage length
    """
    text_dicts = {}
    for text_path, text_id in texts:
        with open(text_path) as f:
            text_dicts[":".join(text_path.split("/")[-2:])] = " ".join(f.read().split())
    return text_dicts


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


def texts_date(graph):
    """ Get text using a range

    :param graph: Graph to use to retrieve date
    :return: {TextID : [StartDate, EndDate]}
    """
    results = graph.query("""SELECT DISTINCT ?s ?sdate ?edate
        WHERE {
            ?s lr:EndDate ?edate .
            ?s lr:StartDate ?sdate .
            ?s lr:Ignore false
        }""")
    return {str(r): (int(s), int(e)) for r, s, e in results}


def tg_dates(graph, tg):
    """ Get textgroup (Authors) dates

    :param graph: Graph to use to retrieve date
    :return: {TextID : [StartDate, EndDate]}
    """
    results = graph.query("""SELECT DISTINCT ?sdate ?edate
        WHERE {
            <"""+tg+"""> lr:EndDate ?edate .
            <"""+tg+"""> lr:StartDate ?sdate
        }""")
    for s, e in results:
        return int(s), int(e)
    return None


def ignored(graph):
    """ Get ignored texts

    :param graph: Graph to use to retrieve date
    :return: [TextId]
    """
    results = graph.query("""SELECT DISTINCT ?s
        WHERE {
            ?s lr:Ignore true
        }""")
    return [str(r) for r, *_ in results]

