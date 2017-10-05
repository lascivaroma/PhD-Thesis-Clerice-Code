from MyCapytain.resolvers.cts.api import HttpCtsResolver, HttpCtsRetriever
from MyCapytain.common.reference import URN


def names_of_texts(texts="helpers/metadata/names.txt"):
    resolver = HttpCtsResolver(HttpCtsRetriever("http://cts.dh.uni-leipzig.de/api/cts"))
    inventory = resolver.getMetadata()

    output = []
    with open(texts) as f:
        for line in f.readlines():
            line = line.replace("\n", "")
            line = URN(line)
            output.append("{}\t{}".format(line, inventory[line.upTo(URN.TEXTGROUP)].get_label()))

    print("\n".join(output))
