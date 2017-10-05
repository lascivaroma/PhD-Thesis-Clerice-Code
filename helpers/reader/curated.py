import rdflib


def get_graph(src="data/curated/inventory.xml.turtle"):
    g = rdflib.Graph()
    g.parse(src)
    return g

